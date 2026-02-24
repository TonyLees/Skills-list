# GitHub AI Agent/Skill 热门项目追踪

自动追踪 GitHub 上热门的 AI Agent 和 Skill 项目，每日更新。支持：
- 静态网站展示（GitHub Pages）
- 飞书多维表格同步

## 功能

- 自动获取 AI Agent/Skill 相关热门项目
- 静态网站展示，支持搜索和筛选
- 同步到飞书多维表格，方便协作和备注
- 每日自动更新

## 快速开始

### 1. 部署到 GitHub

```bash
# 克隆或下载项目
cd ai-trending-site

# 初始化 Git
git init
git add .
git commit -m "Initial commit"

# 推送到 GitHub（替换 YOUR_USERNAME）
git remote add origin https://github.com/YOUR_USERNAME/ai-trending.git
git branch -M main
git push -u origin main
```

### 2. 启用 GitHub Pages

1. 进入仓库 **Settings** → **Pages**
2. Source: **Deploy from a branch**
3. Branch: **main** → 文件夹 **/docs**
4. 点击 **Save**

网站地址：`https://YOUR_USERNAME.github.io/ai-trending/`

---

## 飞书多维表格配置（可选）

### 步骤 1：创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/app)
2. 点击 **创建企业自建应用**
3. 填写应用名称（如：GitHub Trending）
4. 创建后，记录 **App ID** 和 **App Secret**

### 步骤 2：配置应用权限

在应用管理页面：

1. 进入 **权限管理** → **数据权限**
2. 搜索并添加以下权限：
   - `bitable:record:read` - 查看多维表格记录
   - `bitable:record:write` - 编辑多维表格记录
   - `bitable:app:read` - 查看多维表格应用

3. 进入 **权限管理** → **凭证与基础信息**
4. 发布应用版本并申请上线

### 步骤 3：创建多维表格

1. 在飞书中创建新的多维表格
2. 添加以下字段：

| 字段名称 | 字段类型 | 说明 |
|----------|----------|------|
| 项目名称 | 文本 | 仓库完整名称（owner/repo） |
| 描述 | 多行文本 | 项目描述 |
| Stars | 数字 | Star 数量 |
| Forks | 数字 | Fork 数量 |
| 语言 | 单选 | 编程语言 |
| 链接 | 超链接 | GitHub 链接 |
| 作者 | 文本 | 仓库作者 |
| 标签 | 文本 | 项目标签 |
| 更新时间 | 日期 | 最后更新时间 |
| 是否已读 | 复选框 | 个人标记 |
| 备注 | 多行文本 | 个人备注 |

### 步骤 4：获取表格 ID

从多维表格 URL 中获取：

```
https://xxx.feishu.cn/base/bascnXXXXXXXXXX?table=tblnXXXXXXXXXX
                        ↑ base_id              ↑ table_id
```

- `base_id`: `bascnXXXXXXXXXX`
- `table_id`: `tblnXXXXXXXXXX`

### 步骤 5：配置 GitHub Secrets

在 GitHub 仓库中：

1. 进入 **Settings** → **Secrets and variables** → **Actions**
2. 点击 **New repository secret**，添加以下 4 个：

| Secret 名称 | 值 |
|-------------|-----|
| `FEISHU_APP_ID` | 飞书应用的 App ID |
| `FEISHU_APP_SECRET` | 飞书应用的 App Secret |
| `FEISHU_BASE_ID` | 多维表格的 base_id |
| `FEISHU_TABLE_ID` | 数据表的 table_id |

### 步骤 6：验证配置

1. 进入 **Actions** 页面
2. 选择 **Update AI Trending** 工作流
3. 点击 **Run workflow** → **Run workflow**
4. 查看运行日志，确认同步成功

---

## 本地运行

```bash
# 获取数据
python scripts/fetch_trending.py -o trending.json

# 生成网站
python scripts/generate_site.py -i trending.json -o docs

# 同步到飞书（需要设置环境变量）
export FEISHU_APP_ID="your_app_id"
export FEISHU_APP_SECRET="your_app_secret"
export FEISHU_BASE_ID="your_base_id"
export FEISHU_TABLE_ID="your_table_id"
python scripts/sync_to_feishu.py -i trending.json

# 本地预览网站
cd docs && python -m http.server 8000
```

---

## 自定义

### 修改搜索关键词

编辑 `scripts/fetch_trending.py`：

```python
SEARCH_QUERIES = [
    "ai-agent",
    "your-custom-query",  # 添加自定义关键词
]

TOPICS = [
    "ai-agent",
    "your-custom-topic",  # 添加自定义主题
]
```

### 修改网站样式

编辑 `scripts/generate_site.py` 中的 `get_html_template()` 函数。

---

## 文件结构

```
ai-trending-site/
├── .github/
│   └── workflows/
│       └── update-trending.yml  # GitHub Actions 工作流
├── scripts/
│   ├── fetch_trending.py        # 获取 GitHub 数据
│   ├── generate_site.py         # 生成静态网站
│   └── sync_to_feishu.py        # 同步到飞书
├── docs/
│   └── index.html               # 生成的网站
├── trending.json                # 数据文件
└── README.md
```

---

## 常见问题

### Q: 飞书同步失败怎么办？

1. 检查 Secrets 是否正确配置
2. 确认应用权限已添加并发布
3. 确认多维表格字段名称与脚本匹配

### Q: 如何修改更新频率？

编辑 `.github/workflows/update-trending.yml`：

```yaml
on:
  schedule:
    - cron: '0 */6 * * *'  # 每6小时更新一次
```

### Q: 如何添加更多项目？

修改 `scripts/fetch_trending.py` 中的 `-l` 参数：

```python
parser.add_argument("-l", "--limit", type=int, default=200)  # 改为200个项目
```

---

## 许可证

MIT License
