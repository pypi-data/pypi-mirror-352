# TaskMcpClient 文件任务型MCP客户端工具

# 1 设计目的
在各类AI聊天桌面工具（如[Claude for Desktop](https://support.anthropic.com/en/articles/10065433-installing-claude-for-desktop)、[Cursor](https://www.cursor.com/cn/downloads)、[Trae](https://www.trae.com.cn/home)、[CherryStuio](https://www.cherry-ai.com/) ）中，可以方便地配置LLM模型服务和各类MCP服务端，实现LLM+MCP结合的智能体构建与测试。
但测试通过后，就可能需要部署在服务器上，在LLM和MCP服务端配置妥当情况下，让程序自动执行自然语言描述的任务。由程序控制任务指令，并取走任务执行结果。

这里构想这样的任务，请求不会太频繁，大约是分钟级。采用某个目录中的Markdown文件作为输入，采用另外目录作为输出。

这就是“文件任务型MCP客户端工具”，简称“TaskMcpClient”。

另外，TaskMcpClient作为一个通用工具，从当前工作目录读取LLM和MCP配置，不依赖于其它环境和工具。


# 2 安装指南

在Windows或Linux系统中，执行如下命令
```
uv tool install TaskMcpClient
```
即可得到 TaskMcpClient 可执行文件，对应目录分别是
- 在Windows下，`%HOMEPATH%\.local\bin\TaskMcpClient.exe`
- 在Linux下，`$HOME/.local/bin/TaskMcpClient`

# 3 配置指南

1. 创建新的工作目录，假定是`<TaskDir>`
2. 在终端窗口进入到 `<TaskDir>`
3. 执行 TaskMcpClient 命令，可以看到该程序的运行日志，并默认进入聊天状态。此时由于没有配置LLM，会出现`APIConnectionError`错误，输入`quit`退出命令

## 3.1 配置LLM
编辑 `<TaskDir>/.env`文件，以Ollama模型为例，配置如下：
```
OPENAI_BASE_URL=http://127.0.0.1:11434/v1
OPENAI_API_KEY=ollama
OPENAI_MODEL=deepseek-r1
```

## 3.2 配置MCP

### 3.2.1 配置运行MCP服务端的命令路径
编辑 `<TaskDir>/mcp.server/cmdPath.env`文件，以Window环境为例，配置如下：

```
uv=C:\Python3.11\Scripts\uv.exe    # uv run 按指定目录下.venv创建临时环境运行
uvx=C:\Python3.11\Scripts\uvx.exe  # uvx 等同于 uv tool run，运行Python包内命令
bun=C:\Users\Administrator\.bun\bin\bun.exe  # js运行时，内置了打包器、转译器、任务运行器和 npm 客户端
bunx=C:\Users\Administrator\.bun\bin\bunx.exe  # bunx 是 bun x 的别名
python=C:\Python3.11\python.exe
```

### 3.2.2 配置MCP服务端
采用json格式，一个MCP服务端一个json文件

#### 3.2.2.1 stdio示例
- `weather.stdio.json`
```
{
    "command": "uv",
    "args": [
        "--directory",
        "E:/Full/Path/McpServer/weather",
        "run",
        "weather.py"
    ],
    "env": {}
}
```
#### 3.2.2.2 sse示例
- `test_xuanyuan.sse.json`
```
{
    "url": "http://127.0.0.1:8000/sse",
    "headers": {}
}
```

#### 3.2.2.3 websocket

# 4 运行指南
## 4.1 交互聊天
直接运行 TaskMcpClient 命令
```
TaskMcpClient
```

## 4.2 任务执行
直接运行 TaskMcpClient 命令
```
TaskMcpClient task
```

# 5 配置任务