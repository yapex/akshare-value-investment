"""
MCP模块接口定义
遵循依赖倒置原则，定义MCP模块的抽象接口
"""

from typing import List, Dict, Any, Protocol


class IMCPResponseFormatter(Protocol):
    """MCP响应格式化器接口"""

    def format_query_response(self,
                            symbol: str,
                            query: str,
                            data: List[Dict[str, Any]],
                            message: str = None,
                            prefer_annual: bool = True) -> str:
        """
        格式化财务指标查询响应

        Args:
            symbol: 股票代码
            query: 查询内容
            data: 查询结果数据
            message: 消息
            prefer_annual: 是否优先年报数据

        Returns:
            格式化的响应文本
        """
        ...

    def format_search_response(self,
                             keyword: str,
                             market: str,
                             fields: List[str]) -> str:
        """
        格式化字段搜索响应

        Args:
            keyword: 搜索关键字
            market: 市场类型
            fields: 搜索结果字段

        Returns:
            格式化的响应文本
        """
        ...

    def format_field_details_response(self,
                                    field_name: str,
                                    field_info: Dict[str, Any]) -> str:
        """
        格式化字段详情响应

        Args:
            field_name: 字段名
            field_info: 字段信息

        Returns:
            格式化的响应文本
        """
        ...

    def format_simple_message(self, message: str) -> str:
        """
        格式化简单消息

        Args:
            message: 消息内容

        Returns:
            格式化的消息
        """
        ...


class IMCPToolHandler(Protocol):
    """MCP工具处理器接口"""

    def get_tool_name(self) -> str:
        """获取工具名称"""
        ...

    def get_tool_description(self) -> str:
        """获取工具描述"""
        ...

    def get_tool_schema(self) -> Dict[str, Any]:
        """获取工具模式"""
        ...

    async def handle(self, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理工具调用

        Args:
            arguments: 工具参数

        Returns:
            处理结果
        """
        ...


class IMCPServer(Protocol):
    """MCP服务器接口"""

    def register_handler(self, tool_name: str, handler: IMCPToolHandler) -> None:
        """
        注册工具处理器

        Args:
            tool_name: 工具名称
            handler: 处理器实例
        """
        ...

    def set_formatter(self, formatter: IMCPResponseFormatter) -> None:
        """
        设置响应格式化器

        Args:
            formatter: 格式化器实例
        """
        ...

    async def start(self) -> None:
        """启动MCP服务器"""
        ...

    async def stop(self) -> None:
        """停止MCP服务器"""
        ...