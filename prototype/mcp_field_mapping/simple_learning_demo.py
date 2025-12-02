"""
最简化的交互式学习演示
"""
import asyncio


class SimpleMCPServer:
    """简化的MCP服务器"""

    def __init__(self):
        # 港股可用字段
        self.hk_fields = ["HOLDER_PROFIT", "OPERATE_INCOME", "NET_PROFIT_RATIO"]
        # 学习存储
        self.learned_mappings = {}

    def query(self, symbol: str, target_fields: list) -> dict:
        """查询财务数据"""
        print(f"🔍 查询 {symbol} 的 {target_fields}")

        # 检查是否有学习过的映射
        if symbol in self.learned_mappings:
            actual_fields = []
            for target in target_fields:
                if target in self.learned_mappings[symbol]:
                    actual = self.learned_mappings[symbol][target]
                    actual_fields.append(actual)
                    print(f"   使用学习映射: {target} -> {actual}")
                else:
                    actual_fields.append(target)

            # 尝试查询
            if self._try_query(actual_fields):
                return {"success": True, "data": f"成功获取 {len(actual_fields)} 个字段"}

        # 首次查询，直接匹配
        print("   尝试直接匹配...")
        matched_fields = []
        for target in target_fields:
            if target in self.hk_fields:
                matched_fields.append(target)
                print(f"   ✅ 直接匹配: {target}")

        if matched_fields:
            return {"success": True, "data": f"成功获取 {len(matched_fields)} 个字段"}

        # 匹配失败，返回指导和可用字段
        print(f"   ❌ 无法匹配: {target_fields}")
        return {
            "success": False,
            "available_fields": self.hk_fields,
            "guidance": f"请从 {self.hk_fields} 中选择最接近的字段"
        }

    def _try_query(self, fields: list) -> bool:
        """模拟查询执行"""
        print(f"   📊 查询字段: {fields}")
        return True  # 简化假设总是成功

    def learn_mapping(self, symbol: str, target_field: str, actual_field: str):
        """学习字段映射"""
        if symbol not in self.learned_mappings:
            self.learned_mappings[symbol] = {}
        self.learned_mappings[symbol][target_field] = actual_field
        print(f"   ✅ 学习成功: {target_field} -> {actual_field}")


class SimpleLLMAgent:
    """简化的LLM Agent"""

    def __init__(self, mcp_server: SimpleMCPServer):
        self.mcp_server = mcp_server

    async def query(self, symbol: str, target_fields: list) -> dict:
        """智能查询"""
        print(f"\n🤖 LLM Agent: 查询 {symbol} 的 {target_fields}")
        print("-" * 30)

        # 首次查询
        result = self.mcp_server.query(symbol, target_fields)

        if result["success"]:
            print(f"✅ 查询成功: {result['data']}")
            return result

        # 查询失败，开始学习
        print("❌ 查询失败，开始学习...")
        available_fields = result["available_fields"]

        # 学习每个未匹配的字段
        for target_field in target_fields:
            print(f"   分析字段: '{target_field}'")
            print(f"   可用字段: {available_fields}")

            # 简单的智能匹配逻辑
            best_match = self._smart_match(target_field, available_fields)
            if best_match:
                print(f"   💡 选择: {target_field} -> {best_match}")
                self.mcp_server.learn_mapping(symbol, target_field, best_match)

        # 重新查询
        print("🔄 重新查询...")
        retry_result = self.mcp_server.query(symbol, target_fields)

        if retry_result["success"]:
            print(f"🎉 学习成功! {retry_result['data']}")
        else:
            print("❌ 学习后仍然失败")

        return retry_result

    def _smart_match(self, target: str, available_fields: list) -> str:
        """智能字段匹配"""
        # 简化的匹配规则
        if target == "净利润":
            for field in available_fields:
                if "PROFIT" in field:
                    return field
        elif target == "营业收入":
            for field in available_fields:
                if "INCOME" in field:
                    return field
        return None


async def demo():
    """演示流程"""
    print("🚀 交互式学习演示")
    print("=" * 40)

    mcp = SimpleMCPServer()
    llm = SimpleLLMAgent(mcp)

    # 场景1: 首次查询腾讯净利润
    print("\n📋 场景1: 首次查询腾讯净利润")
    await llm.query("00700", ["净利润"])

    # 场景2: 第二次查询（使用学习结果）
    print("\n📋 场景2: 第二次查询（使用学习结果）")
    await llm.query("00700", ["净利润"])

    # 场景3: 其他股票验证学习传播
    print("\n📋 场景3: 其他股票验证学习传播")
    await llm.query("09988", ["净利润"])

    print(f"\n📚 学习到的映射:")
    for symbol, mappings in mcp.learned_mappings.items():
        print(f"   {symbol}: {mappings}")


if __name__ == "__main__":
    asyncio.run(demo())