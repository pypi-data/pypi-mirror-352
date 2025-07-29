# MCP Demo

一个简单的MCP (Model Context Protocol) 服务器演示包，可以通过Trae AI IDE使用。

## 功能特性

这个MCP服务器提供了三个简单的工具：

1. **echo** - 回显输入的文本
2. **add** - 计算两个数字的和
3. **greet** - 生成多语言个性化问候语（支持中文、英文、法文、西班牙文）

## 安装

### 从PyPI安装
```bash
pip install mcp-demo
```

### 从源码安装
```bash
git clone https://github.com/yourusername/mcp-demo.git
cd mcp-demo
pip install -e .
```

## 在Trae中使用

1. 安装包后，在Trae的MCP配置文件中添加以下配置：

```json
{
  "mcpServers": {
    "yashuashua-mcp-server": {
      "command": "python",
      "args": ["-m", "mcp_demo_yashuashua.server"]
    }
  }
}
```

或者如果你已经安装了包：

```json
{
  "mcpServers": {
    "mcp-demo": {
      "command": "mcp-demo"
    }
  }
}
```

2. 重启Trae，你就可以在对话中使用这些工具了！

## 使用示例

在Trae中，你可以这样使用：

- "帮我回显一下'Hello World'"
- "计算 15 + 27 的结果"
- "用法语向Alice问好"

## 开发

### 本地开发环境设置

```bash
# 克隆仓库
git clone https://github.com/yourusername/mcp-demo.git
cd mcp-demo

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest
```

### 构建和发布

```bash
# 构建包
python -m build

# 发布到PyPI（需要先配置PyPI凭据）
twine upload dist/*
```

## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request！
