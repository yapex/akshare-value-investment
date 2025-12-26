"""
股票代码历史记录管理器

负责保存和检索用户查询过的股票代码
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from collections import Counter


@dataclass
class StockHistoryItem:
    """股票历史记录项"""
    symbol: str           # 标准化股票代码（如 600519, 00700, AAPL）
    market: str          # 市场类型（A股、港股、美股）
    original_input: str  # 用户原始输入
    name: Optional[str] = None  # 股票名称（可选）
    query_count: int = 0       # 查询次数
    last_query_time: str = ""  # 最后查询时间（ISO格式）

    def __post_init__(self):
        if not self.last_query_time:
            self.last_query_time = datetime.now().isoformat()


class StockHistoryManager:
    """股票历史记录管理器"""

    def __init__(self, cache_dir: Path = None):
        """
        初始化历史记录管理器

        Args:
            cache_dir: 缓存目录路径，默认为 webapp/.cache/
        """
        if cache_dir is None:
            cache_dir = Path(__file__).parent.parent / ".cache"

        self.cache_dir = Path(cache_dir)
        self.history_file = self.cache_dir / "stock_history.json"
        self.history_file.parent.mkdir(parents=True, exist_ok=True)

        # 加载历史记录
        self._history: Dict[str, StockHistoryItem] = self._load_history()

    def _load_history(self) -> Dict[str, StockHistoryItem]:
        """从文件加载历史记录"""
        if not self.history_file.exists():
            return {}

        try:
            with open(self.history_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return {
                    symbol: StockHistoryItem(**item)
                    for symbol, item in data.items()
                }
        except (json.JSONDecodeError, TypeError):
            return {}

    def _save_history(self):
        """保存历史记录到文件"""
        data = {}
        for symbol, item in self._history.items():
            # 转换为字典，并过滤掉None值
            item_dict = asdict(item)
            # 移除None值的字段
            data[symbol] = {k: v for k, v in item_dict.items() if v is not None}

        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_record(self, symbol: str, market: str, original_input: str, name: str = None):
        """
        添加或更新历史记录

        Args:
            symbol: 标准化股票代码
            market: 市场类型
            original_input: 用户原始输入
            name: 股票名称（可选）
        """
        if symbol in self._history:
            # 更新现有记录
            item = self._history[symbol]
            item.query_count += 1
            item.last_query_time = datetime.now().isoformat()
        else:
            # 创建新记录
            self._history[symbol] = StockHistoryItem(
                symbol=symbol,
                market=market,
                original_input=original_input,
                name=name,
                query_count=1
            )

        self._save_history()

    def search(self, searchterm: str, limit: int = 10) -> List[tuple]:
        """
        搜索历史记录

        Args:
            searchterm: 搜索词（支持股票代码或名称）
            limit: 最大返回数量

        Returns:
            list of (显示文本, 股票代码) 元组
        """
        if not searchterm or len(searchterm) < 1:
            # 返回最常查询的记录
            sorted_items = sorted(
                self._history.values(),
                key=lambda x: (-x.query_count, x.last_query_time)
            )
            items = sorted_items[:limit]
        else:
            # 模糊搜索
            searchterm = searchterm.lower()
            matched = []

            for item in self._history.values():
                # 匹配股票代码或原始输入
                if (searchterm in item.symbol.lower() or
                    searchterm in item.original_input.lower() or
                    (item.name and searchterm in item.name.lower())):
                    matched.append(item)

            # 按查询频率和时间排序
            items = sorted(
                matched,
                key=lambda x: (-x.query_count, x.last_query_time)
            )[:limit]

        # 构建显示文本
        results = []
        for item in items:
            display_text = f"{item.symbol}"
            if item.name:
                display_text += f" - {item.name}"
            display_text += f" [{item.market}]"
            results.append((display_text, item.symbol))

        return results

    def get_all_symbols(self) -> List[str]:
        """获取所有历史股票代码"""
        return list(self._history.keys())

    def clear_history(self):
        """清空历史记录"""
        self._history.clear()
        self._save_history()

    def get_statistics(self) -> Dict:
        """获取历史统计信息"""
        items = list(self._history.values())
        return {
            "total_count": len(items),
            "total_queries": sum(item.query_count for item in items),
            "market_distribution": Counter(item.market for item in items),
            "most_queried": sorted(items, key=lambda x: -x.query_count)[:5]
        }
