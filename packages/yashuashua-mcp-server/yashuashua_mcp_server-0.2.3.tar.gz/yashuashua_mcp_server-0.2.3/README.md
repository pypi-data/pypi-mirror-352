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
pip install yashuashua_mcp_server
```

## 在Trae中使用

1. 在Trae的MCP配置文件中添加以下配置：（保持最新版）

```json
{
  "mcpServers": {
    "yashuashua-mcp-server": {
      "command": "uvx",
      "args": ["--reinstall", "yashuashua-mcp-server"]
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




## 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件。

## 贡献

欢迎提交Issue和Pull Request！
