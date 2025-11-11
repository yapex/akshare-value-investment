## TDD Prompt: [功能名称]

### 1. 用户故事 / 背景
*作为一个 [角色]，我想要 [执行一个动作]，以便于 [实现一个价值]。*

### 2. 目标
[清晰、简洁地描述需要实现的功能。]

### 3. 数据模型 / 接口契约 (如果适用)
[在此定义所需的数据结构、API 请求/响应格式等。]

### 4. 测试套件与规格

#### 成功路径测试 (Happy Path)
*   **测试用例 1.1: [描述性名称]**
    *   **描述**: [简要解释此场景]
    *   **背景 (Given)**: [初始状态/上下文]
    *   **当 (When)**: [执行的动作]
    *   **那么 (Then)**: [预期的结果，包括状态码、响应体或状态变更]

#### 错误处理测试
*   **测试用例 2.1: [描述性名称，针对某个错误]**
    *   **描述**: [简要解释此错误场景]
    *   **背景 (Given)**: [导致错误发生的初始状态]
    *   **当 (When)**: [触发错误的操作]
    *   **那么 (Then)**: [预期的错误响应、错误信息和状态码]

#### 边界情况测试 (Edge Case)
*   **测试用例 3.1: [描述性名称，针对某个边界条件]**
    *   **描述**: [简要解释此边界条件]
    *   **背景 (Given)**: [处于边界的初始状态]
    *   **当 (When)**: [在边界上执行的操作]
    *   **那么 (Then)**: [针对此边界情况的预期结果]

### 5. 实现与非功能性要求
- [ ] **技术栈**: [例如：Python, Django, pytest]
- [ ] **安全要求**: [例如：密码哈希算法，输入验证规则]
- [ ] **性能指标**: [例如：响应时间 < 200ms]
- [ ] **代码质量**: [例如：代码覆盖率 > 80%，遵循 ESLint 规则]
- [ ] **外部依赖**: [例如：使用 library-X 来处理功能-Y]

### 6. 测试驱动开发步骤
1.  **红 (Red)**: 为 **测试用例 1.1** 编写一个失败的测试。
2.  **绿 (Green)**: 编写最精简的代码，使其能通过刚刚编写的测试。
3.  **重构 (Refactor)**: 在保持所有测试通过的前提下，优化和清理代码。
4.  为后续的每个测试用例重复此循环。

### **7. 测试代码示例 (可选，但强烈推荐)**

这里我们使用 Python 流行的 `pytest` 框架作为示例。它的语法非常简洁，并且能够很好地体现“背景-行为-断言” (Arrange-Act-Assert) 的测试模式。

```python
# 导入必要的库，例如 pytest
import pytest
# from your_module import your_function_to_test # 假设这是你要测试的函数

# 使用类 (Class) 来组织一组相关的测试，这是一个良好的实践
class TestFeatureName:
    """针对 [功能名称] 的测试套件"""

    def test_happy_path_scenario(self):
        """测试成功路径 (Happy Path)
        
        对应测试用例 1.1: [此处填写测试用例的简短描述，例如：有效用户成功登录]
        """
        # 1. 准备 (Arrange): 准备测试数据和环境
        # 例如，创建一个用户输入或模拟一个数据库记录
        valid_input = {"email": "test@example.com", "password": "password123"}
        expected_token = "a_valid_jwt_token"

        # 2. 执行 (Act): 执行被测试的代码/函数
        # 假设我们正在测试一个名为 login 的函数
        # actual_result = login(valid_input)

        # 3. 断言 (Assert): 验证结果是否符合预期
        # assert actual_result["token"] == expected_token
        # assert actual_result["status_code"] == 200
        pass  # 这里使用 pass 占位，实际编写时应替换为上面的真实代码

    def test_error_handling_scenario(self):
        """测试错误处理 (Error Handling)
        
        对应测试用例 2.1: [此处填写错误场景的简短描述，例如：密码错误返回401]
        """
        # 1. 准备 (Arrange): 准备一个会导致错误的输入
        invalid_input = {"email": "test@example.com", "password": "wrongpassword"}
        expected_error_message = "无效的凭证"

        # 2. 执行 (Act) & 3. 断言 (Assert):
        # 使用 pytest.raises 来断言一个特定的异常是否被正确抛出
        # 假设无效登录会抛出 ValueError
        # with pytest.raises(ValueError) as excinfo:
        #     login(invalid_input)
        
        # (可选) 还可以进一步断言异常信息的内容是否符合预期
        # assert expected_error_message in str(excinfo.value)
        pass # 占位

    def test_edge_case_scenario(self):
        """测试边界情况 (Edge Case)
        
        对应测试用例 3.1: [此处填写边界情况的简短描述，例如：输入为空字符串]
        """
        # 1. 准备 (Arrange): 准备边界条件输入
        edge_case_input = {"email": "", "password": ""}
        
        # 2. 执行 (Act): 调用函数
        # result = login(edge_case_input)

        # 3. 断言 (Assert): 验证系统是否按预期处理了边界情况
        # assert result["status_code"] == 400 # 例如，返回“错误请求”
        pass # 占位
```