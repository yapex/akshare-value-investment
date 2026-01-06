import pandas as pd
from typing import Optional
from .registry import FieldMappingRegistry

class SchemaNormalizer:
    """
    Schema Normalizer (结构归一化器)。
    
    职责：
    1. 接收原始异构数据 (Heterogeneous Raw Data)。
    2. 基于 Registry 中的映射规则，执行 Schema 转换。
    3. 输出标准化数据 (Standardized Data)。
    
    核心特性：
    - 高性能 (High Performance): 使用 Pandas 向量化操作，避免 Python 循环。
    - 无副作用 (Side-effect Free): 不修改原始 DataFrame。
    """

    def __init__(self, registry: FieldMappingRegistry):
        self.registry = registry

    def standardize(self, df: Optional[pd.DataFrame], market: str) -> pd.DataFrame:
        """
        标准化 DataFrame 的列名结构。
        
        Args:
            df: 原始数据 DataFrame
            market: 市场标识符 (e.g., 'a_stock', 'us_stock')
            
        Returns:
            标准化后的 DataFrame。如果输入为空，返回空 DataFrame。
        """
        if df is None or df.empty:
            return pd.DataFrame()
            
        # 1. 获取映射关系: {raw_field: standard_field}
        mapping = self.registry.get_mapping(market)
        
        if not mapping:
            return df.copy()
            
        # 2. 向量化重命名 (Vectorized Rename)
        # 这是一个 C-level 优化操作，速度极快。
        # 仅重命名 mapping 中存在的列，其他列保持原样。
        std_df = df.rename(columns=mapping)
        
        return std_df
