"""
SQLite智能缓存

生产级SQLite缓存实现，支持：
1. 按条缓存和日期范围查询
2. 智能增量更新
3. 多日期字段支持
4. 线程安全访问
"""

import sqlite3
import json
import os
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta
import logging
import threading

logger = logging.getLogger(__name__)


class SQLiteCache:
    """
    SQLite智能缓存

    核心特性：
    1. 按条缓存：每条财务数据独立存储，便于精确管理
    2. 日期范围查询：利用SQL BETWEEN实现高效范围筛选
    3. 智能增量更新：自动识别缺失数据，避免重复API调用
    4. 线程安全：支持并发访问
    """

    def __init__(self, db_path: str = "cache/financial_data.db"):
        """
        初始化SQLite缓存

        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self._local = threading.local()

        # 确保缓存目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        # 初始化数据库
        self._init_database()

        logger.debug(f"SQLite缓存初始化完成: {db_path}")

    def _init_database(self) -> None:
        """初始化数据库表和索引"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()

            # 创建主表 - 使用复合主键，去除cache_key冗余
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS financial_data (
                    symbol TEXT NOT NULL,          -- 股票代码（已包含市场信息）
                    date_value TEXT NOT NULL,      -- 标准化日期值
                    query_type TEXT NOT NULL,      -- 查询类型（indicators/profit/balance/cashflow）
                    data_json TEXT NOT NULL,       -- 完整原始数据JSON
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    PRIMARY KEY (symbol, date_value, query_type)  -- 复合主键
                )
            """)

            # 创建高效索引 - 支持各种查询模式
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_symbol_type ON financial_data(symbol, query_type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_created_at ON financial_data(created_at)")

            conn.commit()

    def _get_connection(self) -> sqlite3.Connection:
        """获取线程安全的数据库连接"""
        if not hasattr(self._local, 'connection'):
            self._local.connection = sqlite3.connect(self.db_path)
        return self._local.connection

    def save_records(self, symbol: str, records: List[Dict[str, Any]],
                    date_field: str, query_type: str) -> int:
        """
        按条保存财务记录

        Args:
            symbol: 股票代码（如SH600519、00700、AAPL）
            records: 财务数据记录列表
            date_field: 日期字段名（date/report_date/end_date）
            query_type: 查询类型（indicators/profit/balance/cashflow）

        Returns:
            实际保存的记录数量
        """
        if records is None or (hasattr(records, 'empty') and records.empty):
            return 0

        # 如果是DataFrame，转换为记录列表
        if hasattr(records, 'to_dict'):
            records = records.to_dict('records')

        saved_count = 0
        conn = self._get_connection()
        cursor = conn.cursor()

        try:
            for record in records:
                # 检查必需的日期字段
                if date_field not in record:
                    logger.warning(f"记录缺少日期字段 {date_field}: {record}")
                    continue

                # 序列化完整数据
                data_json = json.dumps(record, ensure_ascii=False)

                # 使用UPSERT：存在则更新，不存在则插入
                # 直接使用复合主键 (symbol, date_value, query_type)
                cursor.execute("""
                    INSERT INTO financial_data
                    (symbol, date_value, query_type, data_json, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(symbol, date_value, query_type) DO UPDATE SET
                        data_json = excluded.data_json,
                        updated_at = CURRENT_TIMESTAMP
                """, (symbol, record[date_field], query_type, data_json))

                saved_count += 1

            conn.commit()
            if saved_count > 0:
                logger.info(f"💾 保存 {saved_count} 条记录到缓存: {symbol} - {query_type}")

        except Exception as e:
            conn.rollback()
            logger.error(f"保存缓存记录失败: {e}")
            raise

        return saved_count

    def query_by_date_range(self, symbol: str, start_date: str, end_date: str,
                           date_field: str, query_type: str) -> List[Dict[str, Any]]:
        """
        按日期范围查询缓存数据

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            date_field: 日期字段名
            query_type: 查询类型

        Returns:
            匹配的记录列表
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT data_json FROM financial_data
            WHERE symbol = ?
              AND query_type = ?
              AND date_value BETWEEN ? AND ?
            ORDER BY date_value
        """, (symbol, query_type, start_date, end_date))

        rows = cursor.fetchall()
        if not rows:
            return []

        # 解析JSON数据
        results = [json.loads(row[0]) for row in rows]

        if results:
            logger.debug(f"缓存命中: {symbol} {query_type} {start_date}-{end_date} ({len(results)}条)")
        else:
            logger.debug(f"缓存未命中: {symbol} {query_type} {start_date}-{end_date}")

        return results

    def _get_missing_date_ranges(self, symbol: str, start_date: str, end_date: str,
                            date_field: str, query_type: str) -> List[Dict[str, str]]:
        """
        内部方法：获取缺失的日期范围，用于增量更新

        设计原则：
        1. 如果有缺失数据，合并为单个完整时间段
        2. 优化网络开销，减少API调用次数
        3. 简化实现和错误处理

        Args:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            date_field: 日期字段名
            query_type: 查询类型

        Returns:
            空列表（完全缓存）或单个合并范围 [{'start': '2020-01-01', 'end': '2025-12-31'}]
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT date_value FROM financial_data
            WHERE symbol = ?
              AND query_type = ?
              AND date_value BETWEEN ? AND ?
            ORDER BY date_value
        """, (symbol, query_type, start_date, end_date))

        cached_dates = sorted([row[0] for row in cursor.fetchall()])

        if not cached_dates:
            # 完全没有缓存数据，返回整个范围
            return [{'start': start_date, 'end': end_date}]

        # 检查缓存是否完整覆盖整个时间范围
        first_cached = cached_dates[0]
        last_cached = cached_dates[-1]

        # 检查是否有任何缺失
        has_gaps = False
        has_start_gap = first_cached > start_date
        has_end_gap = last_cached < end_date
        has_middle_gaps = False

        if has_start_gap:
            has_gaps = True
        elif has_end_gap:
            has_gaps = True
        else:
            # 检查中间是否有间隙
            for i in range(len(cached_dates) - 1):
                current_date = cached_dates[i]
                next_cached_date = cached_dates[i + 1]
                next_expected_date = self._get_next_quarter(current_date)
                if next_expected_date < next_cached_date:
                    has_middle_gaps = True
                    has_gaps = True
                    break

        if has_gaps:
            if has_middle_gaps or (has_start_gap and has_end_gap):
                # 多边缺失：完整重新获取
                logger.debug(f"检测到多边缺失，将获取完整时间范围: {start_date} 到 {end_date}")
                return [{'start': start_date, 'end': end_date}]
            elif has_start_gap:
                # 左单边缺失：按需补充
                logger.debug(f"检测到左单边缺失，按需补充: {start_date} 到 {first_cached}")
                return [{'start': start_date, 'end': first_cached}]
            elif has_end_gap:
                # 右单边缺失：按需补充
                logger.debug(f"检测到右单边缺失，按需补充: {last_cached} 到 {end_date}")
                return [{'start': last_cached, 'end': end_date}]
            else:
                # 中间有间隙，完整重新获取
                logger.debug(f"检测到中间间隙，将获取完整时间范围: {start_date} 到 {end_date}")
                return [{'start': start_date, 'end': end_date}]
        else:
            # 缓存完全覆盖，无缺失
            return []

    
    def _count_quarters_between(self, start_date: str, end_date: str) -> int:
        """计算两个日期之间的季度数量"""
        from datetime import datetime
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')

        years = end.year - start.year
        months = end.month - start.month
        total_months = years * 12 + months
        return max(1, (total_months + 2) // 3)  # 向上取整

    def _get_next_quarter(self, date_str: str) -> str:
        """获取下一个季度末日期"""
        year, month, day = map(int, date_str.split('-'))

        if month == 3:   # Q1 -> Q2
            return f"{year}-06-30"
        elif month == 6:  # Q2 -> Q3
            return f"{year}-09-30"
        elif month == 9:  # Q3 -> Q4
            return f"{year}-12-31"
        elif month == 12: # Q4 -> next year Q1
            return f"{year + 1}-03-31"
        else:
            # 如果不是标准季度末，简单加3个月
            if month + 3 > 12:
                return f"{year + 1}-{month + 3 - 12:02d}-28"
            else:
                return f"{year}-{month + 3:02d}-28"

    def _get_previous_day(self, date_str: str) -> str:
        """获取前一天"""
        from datetime import datetime, timedelta
        date = datetime.strptime(date_str, '%Y-%m-%d')
        previous_day = date - timedelta(days=1)
        return previous_day.strftime('%Y-%m-%d')

    def close(self) -> None:
        """关闭数据库连接"""
        if hasattr(self._local, 'connection'):
            self._local.connection.close()
            delattr(self._local, 'connection')