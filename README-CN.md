# Hacker News CLI

一个终端优先的命令行工具，用于浏览 Hacker News。无需离开终端即可阅读文章、查看评论和访问链接。

## 功能特性

- **浏览文章列表** — 查看热门、最新、最佳、提问、展示和招聘信息
- **查看文章详情** — 查看完整的文章元数据，包括标题、作者、分数和评论数
- **阅读树状评论** — 评论树按层级缩进显示，HTML 转文本，支持深度与数量限制
- **获取文章链接** — 快速提取 URL 以便在浏览器中打开
- **登录 / 登出 / whoami** — 登录 news.ycombinator.com，会话持久化到本地
- **交互模式** — REPL 模式，所有命令复用同一个 HTTP 连接
- **多种输出格式** — JSON 格式便于脚本处理，文本格式便于人工阅读
- **健壮的 API 客户端** — 网络故障时自动重试，支持指数退避

## 安装

### 环境要求

- Python 3.10 或更高版本
- [uv](https://github.com/astral-sh/uv)（推荐）或 pip

### 从源码安装

```bash
# 克隆仓库
git clone <repository-url>
cd hacker-news-cli

# 使用 uv 安装
uv pip install -e .

# 或使用 pip 安装
pip install -e .
```

## 使用方法

可用命令：`list`、`story`、`comments`、`link`、`login`、`logout`、`whoami`、`interactive` 和 `help`。

### 列出文章

显示文章列表（默认：热门文章）：

```bash
# 列出热门文章（默认）
hn list

# 列出特定板块
hn list --feed new
hn list --feed best
hn list --feed ask
hn list --feed show
hn list --feed jobs

# 分页结果
hn list --limit 10 --page 2
```

### 查看文章详情

显示特定文章的详细信息：

```bash
hn story --id 39528747
```

### 阅读评论

显示文章的评论线程。回复缩进显示在父评论下方；JSON 输出中的 `depth`
字段记录嵌套层级：

```bash
hn comments --id 39528747 --format text

# 限制抓取的线程深度（1 = 只看顶层评论）
hn comments --id 39528747 --depth 2

# 限制抓取的评论总数（父评论优先于回复保留）
hn comments --id 39528747 --max-comments 50
```

不传 `--depth` / `--max-comments` 时抓取完整评论树。

### 获取文章链接

提取文章的 URL：

```bash
hn link --id 39528747
```

### 登录、登出、whoami

会话持久化到 `~/.config/hn-cli/auth.json`（可用 `HN_CLI_AUTH_FILE`
环境变量覆盖）：

```bash
# 交互式登录：提示输入用户名和密码
hn login

# 脚本化登录：密码来自环境变量，绝不通过命令行参数传递
HN_CLI_PASSWORD=... hn login --username alice

# 查看当前会话（本地无会话时不发网络请求）
hn whoami

# 远程登出并清除本地会话
hn logout
```

刻意不提供 `--password` 参数——命令行上的密码会泄露到 shell
历史记录和 `ps` 输出中。

### 交互模式

```bash
hn interactive
```

启动 `>` 提示符，接受相同的命令（带不带 `hn` 前缀均可），并在命令间
复用同一个 HTTP 连接。输入 `exit`/`quit` 退出。

### 输出格式

数据命令都支持 `--format` 选项。`list` 默认 `text`；`story`、`comments`、
`link` 默认 `json`：

```bash
# 结构化数据便于脚本处理
hn list --format json

# 格式化的表格和可读文本
hn story --id 39528747 --format text
```

### 连接选项

配置 API 客户端行为：

```bash
hn list --timeout 15 --retries 3 --backoff 1.0
```

## 示例

```bash
# 以文本格式获取前 5 篇文章
hn list --limit 5 --format text

# 查看热门文章的评论
TOP_STORY=$(hn list --limit 1 --format json | jq -r '.items[0].id')
hn comments --id "$TOP_STORY" --format text

# 在默认浏览器中打开文章链接
hn link --id 39528747 | xargs open
```

## 架构设计

项目采用分层架构：

```
src/hn_cli/
├── cli.py      # 命令行界面和参数解析
├── client.py   # Hacker News API 客户端，支持重试逻辑
├── auth.py     # 登录会话持久化（cookies + 用户名）
├── models.py   # 数据模型（Story、Comment）
├── output.py   # JSON 输出格式化
└── render.py   # 使用 Rich 库的文本渲染
```

### API 客户端

`HNClient` 类封装了 [Hacker News Firebase API](https://github.com/HackerNews/API)
和 news.ycombinator.com 网页接口（用于登录状态），具有以下特性：
- 所有请求均支持指数退避的自动重试
- 可配置的超时时间
- 通过 `requests.Session` 实现连接池
- 并发抓取文章和评论
- 单条数据抓取失败时跳过并告警，不会导致整页失败

### 数据模型

核心实体的不可变数据类：
- **Story** — 标题、作者、分数、时间、URL、评论数
- **Comment** — 作者、时间、内容（HTML 转换为文本）、线程深度

## 开发

### 环境设置

```bash
# 安装依赖（包含 dev 组）
uv sync
```

### 运行测试

```bash
uv run pytest

# 带覆盖率门槛（低于 80% 失败）
uv run pytest --cov=hn_cli
```

### 代码质量

```bash
# 代码检查
uv run ruff check .

# 类型检查
uv run mypy src/hn_cli

# 代码格式化
uv run ruff format .
```

## 许可证

[在此填写您的许可证]
