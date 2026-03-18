# Hacker News CLI

一个终端优先的命令行工具，用于浏览 Hacker News。无需离开终端即可阅读文章、查看评论和访问链接。

## 功能特性

- **浏览文章列表** — 查看热门、最新、最佳、提问、展示和招聘信息
- **查看文章详情** — 查看完整的文章元数据，包括标题、作者、分数和评论数
- **阅读评论** — 以可读的格式显示评论线程，支持 HTML 转文本
- **获取文章链接** — 快速提取 URL 以便在浏览器中打开
- **多种输出格式** — JSON 格式便于脚本处理，文本格式便于人工阅读
- ** resilient API 客户端** — 网络故障时自动重试，支持指数退避

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

CLI 提供四个主要命令：`list`、`story`、`comments` 和 `link`。

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

显示文章的评论线程：

```bash
hn comments --id 39528747
```

### 获取文章链接

提取文章的 URL：

```bash
hn link --id 39528747
```

### 输出格式

所有命令都支持 `--format` 选项：

```bash
# JSON 输出（默认）- 结构化数据便于脚本处理
hn list --format json

# 文本输出 - 格式化的表格和可读文本
hn list --format text
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
├── models.py   # 数据模型（Story、Comment、Feed）
├── output.py   # JSON 输出格式化
└── render.py   # 使用 Rich 库的文本渲染
```

### API 客户端

`HNClient` 类封装了 [Hacker News Firebase API](https://github.com/HackerNews/API)，具有以下特性：
- 支持指数退避的自动重试
- 可配置的超时时间
- 通过 `requests.Session` 实现连接池

### 数据模型

核心实体的不可变数据类：
- **Story** — 标题、作者、分数、时间、URL、评论数
- **Comment** — 作者、时间、内容（HTML 转换为文本）
- **Feed** — 命名文章集合（热门、最新、最佳等）

## 开发

### 环境设置

```bash
# 安装开发依赖
uv pip install -e ".[dev]"

# 或使用 pip
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码质量

```bash
# 代码检查
ruff check .

# 类型检查
mypy src/hn_cli

# 代码格式化
ruff format .
```

## 许可证

[在此填写您的许可证]
