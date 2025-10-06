# 贡献指南

感谢您对 AI Voice Agent Backend 项目的关注！我们欢迎各种形式的贡献，包括但不限于：

- 🐛 Bug 报告
- 💡 功能建议
- 📝 文档改进
- 🔧 代码贡献
- 🧪 测试用例

## 🚀 快速开始

### 1. Fork 和克隆项目

```bash
# Fork 项目到您的 GitHub 账户
# 然后克隆您的 fork
git clone https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
cd voice-ai-chat-agent-backend

# 添加上游仓库
git remote add upstream https://github.com/neothan-dev/voice-ai-chat-agent-backend.git
```

### 2. 设置开发环境

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 安装开发依赖
pip install -r requirements-dev.txt  # 如果有的话
```

### 3. 配置环境

```bash
# 复制环境变量模板
cp env_example.txt .env

# 编辑 .env 文件，配置必要的API密钥
```

## 📋 贡献流程

### 1. 创建分支

```bash
# 从主分支创建新分支
git checkout main
git pull upstream main
git checkout -b feature/your-feature-name
```

### 2. 进行开发

- 编写代码
- 添加测试
- 更新文档
- 确保代码质量

### 3. 提交更改

```bash
# 添加更改
git add .

# 提交更改（使用清晰的提交信息）
git commit -m "feat: add new feature description"

# 推送到您的 fork
git push origin feature/your-feature-name
```

### 4. 创建 Pull Request

1. 访问您的 GitHub fork 页面
2. 点击 "New Pull Request"
3. 填写 PR 描述
4. 等待代码审查

## 📝 代码规范

### Python 代码规范

- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 规范
- 使用类型提示
- 添加适当的文档字符串
- 保持函数简洁（建议不超过 50 行）

### 提交信息规范

使用 [Conventional Commits](https://www.conventionalcommits.org/) 格式：

```
<type>(<scope>): <description>

[optional body]

[optional footer(s)]
```

类型包括：
- `feat`: 新功能
- `fix`: Bug 修复
- `docs`: 文档更新
- `style`: 代码格式调整
- `refactor`: 代码重构
- `test`: 测试相关
- `chore`: 构建过程或辅助工具的变动

示例：
```
feat(auth): add JWT token refresh functionality

- Add refresh token endpoint
- Update authentication middleware
- Add token expiration validation

Closes #123
```

### 代码审查清单

提交 PR 前请检查：

- [ ] 代码遵循项目规范
- [ ] 添加了必要的测试
- [ ] 更新了相关文档
- [ ] 通过了所有测试
- [ ] 没有破坏现有功能
- [ ] 提交信息清晰明确

## 🧪 测试

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest tests/test_auth.py

# 运行测试并生成覆盖率报告
pytest --cov=api --cov-report=html

# 运行测试并显示详细输出
pytest -v
```

### 编写测试

- 为新功能编写单元测试
- 测试覆盖率应保持在 80% 以上
- 使用描述性的测试名称
- 测试正常情况和边界情况

示例：

```python
def test_user_registration_success():
    """测试用户注册成功的情况"""
    # Arrange
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "password123"
    }
    
    # Act
    response = client.post("/auth/register", json=user_data)
    
    # Assert
    assert response.status_code == 201
    assert "access_token" in response.json()
```

## 📚 文档贡献

### 更新 README

- 保持 README 的准确性和完整性
- 添加新功能的说明
- 更新安装和配置步骤

### API 文档

- 为新 API 添加文档字符串
- 使用 FastAPI 的自动文档功能
- 提供使用示例

### 代码注释

```python
def process_audio_file(file_path: str) -> dict:
    """
    处理音频文件并返回转录结果
    
    Args:
        file_path: 音频文件路径
        
    Returns:
        dict: 包含转录文本和元数据的字典
        
    Raises:
        FileNotFoundError: 当音频文件不存在时
        AudioProcessingError: 当音频处理失败时
    """
    # 实现代码...
```

## 🐛 Bug 报告

### 报告 Bug 时请包含：

1. **环境信息**
   - 操作系统版本
   - Python 版本
   - 项目版本

2. **重现步骤**
   - 详细的操作步骤
   - 预期结果
   - 实际结果

3. **错误信息**
   - 完整的错误堆栈
   - 日志文件（如果相关）

4. **附加信息**
   - 截图或录屏
   - 相关配置文件

### Bug 报告模板

```markdown
## Bug 描述
简要描述遇到的问题

## 重现步骤
1. 执行步骤 1
2. 执行步骤 2
3. 观察结果

## 预期行为
描述您期望的行为

## 实际行为
描述实际发生的行为

## 环境信息
- OS: [e.g. Ubuntu 20.04]
- Python: [e.g. 3.8.5]
- 项目版本: [e.g. v1.0.0]

## 附加信息
添加任何其他相关信息
```

## 💡 功能建议

### 提出新功能时请包含：

1. **功能描述**
   - 详细的功能说明
   - 使用场景
   - 预期效果

2. **实现建议**
   - 技术实现思路
   - 可能的挑战
   - 替代方案

3. **影响评估**
   - 对现有功能的影响
   - 性能影响
   - 兼容性考虑

## 🔧 开发工具

### 推荐工具

- **IDE**: VS Code, PyCharm
- **代码格式化**: black, autopep8
- **代码检查**: flake8, pylint
- **类型检查**: mypy
- **测试**: pytest

### VS Code 配置

```json
{
    "python.defaultInterpreterPath": "./venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true
}
```

## 📞 获取帮助

如果您在贡献过程中遇到问题：

1. 查看 [Issues](https://github.com/neothan-dev/voice-ai-chat-agent-backend/issues)
2. 搜索相关问题
3. 创建新的 Issue
4. 联系维护者

## 🎉 贡献者

感谢所有为项目做出贡献的开发者！

<!-- 这里会自动更新贡献者列表 -->

## 📄 许可证

通过贡献代码，您同意您的贡献将在 Apache 2.0 许可证下发布。

Apache 2.0 许可证提供了更强的法律保护，包括：
- 专利保护条款
- 商标保护
- 详细的贡献条款
- 企业级法律保护

---

再次感谢您的贡献！🎉
