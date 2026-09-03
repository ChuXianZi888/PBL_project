# 实验一 零售分析平台项目启动与框架搭建

> 课程：PBL5 零售经营分析平台
> 学时：6（实验环境须在课前完成）
> 实验类型：验证性
> 支撑课程目标：课程目标 2、4

---

## 实验说明

本实验搭建零售经营分析平台的前后端基础框架。后端基于 FastAPI + pymysql，能通过接口调用本机 MySQL；前端基于 Vite + Vue 3 + Element Plus，能调用后端接口并在浏览器显示运行状态。代码通过 Gitee 私有仓库统一管理。

## 考察内容

FastAPI 后端框架搭建、Vue 3 前端框架搭建、Git 仓库管理与前后端接口联通验证。对应课程目标 2（系统架构与功能模块）、课程目标 4（团队协作与接口服务/前端页面开发）。

## 实验环境

下表工具须在实验开始前完成安装与配置。

| 工具 | 版本 | 用途 |
|---|---|---|
| Anaconda | 近期版本 | Python 环境管理 |
| Conda 环境 `pbl5` | Python 3.10+ | 本课程统一环境 |
| MySQL | 8.4 LTS | 数据库（本机安装，root 密码已知） |
| Git | 近期版本 | 版本管理 |
| Gitee 账号 | — | 创建私有仓库 |
| VSCode | 近期版本 | 编辑器（+ Python 扩展 + Pylance） |
| Node.js | 18+ | 前端工具链 |
| AI 编程工具 | Work Buddy | Vibe Coding |

## 理论与原理

### 前后端分离

前端负责页面渲染与交互，后端负责业务逻辑与数据处理，通过 HTTP API（RESTful 风格）通信。本课程后端端口 8000（FastAPI / uvicorn），前端端口 5173（Vite dev server）。

### FastAPI

Python 异步 Web 框架，基于 Starlette（Web 层）和 Pydantic（数据校验层）。用 Python 类型注解同时实现参数校验、序列化和 API 文档生成。开发时以开发模式启动（修改代码后自动重载），访问 `http://127.0.0.1:8000/docs` 可查看自动生成的 Swagger UI。安装与启动命令见步骤 4、步骤 6。

### pymysql

MySQL 的 Python 驱动，用于直接连接 MySQL 执行 SQL。连接需要提供主机、端口、用户名、密码和字符集等参数；连接成功后通过游标（cursor）执行 SQL 并取得结果。本实验中连接数据库并执行 `SELECT VERSION()` 的完整代码见步骤 5 的 main.py。

### CORS

浏览器同源策略规定，网页只能请求与自身同源（协议 + 域名 + 端口）的资源。本课程前端（5173）与后端（8000）端口不同，浏览器会将其视为跨域请求，因此后端需要配置 CORS 中间件，声明允许访问的来源。配置项包括：允许的来源（allow_origins）、是否允许携带凭证（allow_credentials）、允许的 HTTP 方法与请求头（allow_methods / allow_headers）。开发阶段来源设为 `*` 表示允许所有来源；生产环境必须改为具体的前端域名。具体配置代码见步骤 5 的 main.py。

### Vite + Vue 3

Vite 是当前主流的前端构建工具，比 Vue CLI 启动快、配置少。Vue 3 使用组合式 API（Composition API），通过 `ref` / `reactive` / `computed` / `onMounted` 等函数组织逻辑。Element Plus 是 Vue 3 官方推荐的桌面端组件库。

### Vibe Coding

用自然语言描述需求让 AI 生成代码，再由开发者验证和调整。本课程前端业务代码由 AI 生成，学生负责验证产出。

## 实验步骤

### 后端部分

#### 步骤 1：激活 pbl5 环境

```bash
conda env list                # 确认 pbl5 环境存在
conda activate pbl5           # 激活
python --version              # 确认 Python ≥3.10
```

激活成功后命令行提示符前出现 `(pbl5)` 前缀。

#### 步骤 2：在 Gitee 新建项目仓库

1. 浏览器打开 https://gitee.com 并登录
2. 点击右上角「+」→「新建仓库」
3. 填写：仓库名 `pbl5_retail_analysis_platform`，是否公开选择**私有**，勾选「使用 Readme 文件初始化这个仓库」，`.gitignore` 选 `Python`
4. 创建并记下 HTTPS 地址

#### 步骤 3：本地拉取仓库

```bash
cd ~/projects      # 示例路径，请替换为你自己存放项目的目录
git clone https://gitee.com/<用户名>/pbl5_retail_analysis_platform.git
cd pbl5_retail_analysis_platform
mkdir backend
```

仓库可以存放在自己习惯的任意目录。后续步骤中的 `~/projects/pbl5_retail_analysis_platform` 均指你自己选择的仓库位置，执行时请替换为实际路径。

仓库根目录下规划两个子目录：`backend/` 存放 FastAPI 后端，`frontend/` 存放 Vue 3 前端。

首次 push 前需配置 Git 用户信息：

```bash
git config --global user.name "你的姓名"
git config --global user.email "你的邮箱"
```

#### 步骤 4：安装依赖

```bash
pip install "fastapi[standard]" pymysql
```

下载慢时可临时使用镜像：

```bash
pip install "fastapi[standard]" pymysql -i https://pypi.tuna.tsinghua.edu.cn/simple
```

验证：

```bash
fastapi --help
python -c "import pymysql; print(pymysql.__version__)"
```

#### 步骤 5：编写 main.py

在 `backend/` 下创建 `main.py`，写入：

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pymysql

app = FastAPI(
    title="PBL5 零售经营分析平台",               # 文档标题，显示在 /docs 页面顶部
    description="PBL5 零售经营分析平台后端 API",   # 文档整体说明，位于标题下方
    version="0.1.0",                             # API 版本号，显示在 /docs 顶部
)

app.add_middleware(
    CORSMiddleware,               # 注册 CORS 中间件
    allow_origins=["*"],          # 允许的来源列表，* 表示所有来源（开发阶段）
    allow_credentials=True,       # 允许请求携带 Cookie 等凭证
    allow_methods=["*"],          # 允许的 HTTP 方法（GET、POST 等）
    allow_headers=["*"],          # 允许的请求头
)


def ok(data: dict = None, msg: str = "ok"):
    return {"code": 0, "msg": msg, "data": data or {}}

# http:127.0.0.1:8000/api/health
@app.get("/api/health/", tags=["系统"], summary="健康检查")
def health():
    """健康检查：返回服务运行状态与版本号。"""
    return ok({"status": "ok", "version": "0.1.0"})


def get_conn():
    return pymysql.connect(
        host="localhost", port=3306,
        user="root", password="你的 MySQL 密码",
        charset="utf8mb4",
    )


@app.get("/api/db/info", tags=["系统"], summary="数据库连通检查")
def db_info():
    """数据库连通检查：连接本机 MySQL，返回其版本号；连接失败时返回错误信息。"""
    try:
        with get_conn() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT VERSION()")
                version = cur.fetchone()[0]
        return ok({"version": version, "connected": True})
    except Exception as e:
        return {"code": 1, "msg": str(e), "data": {"connected": False}}


SAMPLE_PRODUCTS = [
    {"id": "P001", "name": "可口可乐 330ml", "price": 3.5, "stock": 120},
    {"id": "P002", "name": "百事可乐 330ml", "price": 3.5, "stock": 88},
    {"id": "P003", "name": "农夫山泉 550ml", "price": 2.0, "stock": 256},
]


@app.get("/api/sample/products", tags=["示例数据"], summary="示例商品列表")
def sample_products():
    """示例商品接口：返回内存中的示例商品列表，供前端页面联调展示。"""
    return ok({"items": SAMPLE_PRODUCTS})

@app.get("/", tags=["系统"], summary="服务信息")
def root():
    """根路径：返回服务启动提示与接口文档地址。"""
    return {"message": "零售数据分析平台 API 已启动", "docs": "/docs"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
```

将 `password="你的 MySQL 密码"` 改为本机 root 的真实密码。

#### 步骤 6：启动并验证

后端有两种启动方式，任选其一即可，两种方式效果相同。

方式一：终端启动（自动重载，修改代码后服务自动重启）

```bash
cd ~/projects/pbl5_retail_analysis_platform/backend
fastapi dev main.py
```

方式二：VSCode 中直接运行（执行 `main.py` 末尾的 `if __name__ == "__main__"` 块，调用 uvicorn 启动）

1. VSCode 打开项目文件夹 `pbl5_retail_analysis_platform`
2. 按 `Ctrl+Shift+P`（macOS 为 `Cmd+Shift+P`）→ 输入 `Python: Select Interpreter` → 选择 pbl5 环境
3. 打开 `backend/main.py`，点击右上角的运行按钮（或按 `F5` 选择 Python File）

启动成功后终端输出 `Uvicorn running on http://0.0.0.0:8000`。

另开终端用 curl 验证：

```bash
curl http://127.0.0.1:8000/api/health
curl http://127.0.0.1:8000/api/db/info
curl http://127.0.0.1:8000/api/sample/products
```

浏览器打开 `http://127.0.0.1:8000/docs` 查看 Swagger UI，应列出 4 个接口（`/`、`/api/health`、`/api/db/info`、`/api/sample/products`）。

![image-20260907015041010](/Users/liaoyulei/Library/Application Support/typora-user-images/image-20260907015041010.png)

#### 步骤 7：提交到 Gitee

```bash
git add main.py
git commit -m "feat: 初始化 FastAPI 项目 + pymysql 数据库连通"
git push origin main
```

### 前端部分

#### 步骤 8：创建 Vite + Vue 3 项目

国内网络下载 npm 包可能较慢，可先配置 npmmirror 镜像源（一次设置全局生效，后续 npm 命令自动走镜像）：

```bash
npm config set registry https://registry.npmmirror.com
npm config get registry        # 确认输出为 https://registry.npmmirror.com
```

镜像配置完成后创建项目并安装依赖：

```bash
cd ~/projects/pbl5_retail_analysis_platform
npm create vite@latest frontend -- --template vue
cd frontend
npm install
npm install element-plus axios vue-router
```

若提示"目录不为空"时选择 Ignore files and continue。

#### 步骤 9：提交前端骨架

前端相关的忽略规则已包含在 Vite 模板自带的 `frontend/.gitignore` 中（`node_modules/`、`dist/` 等），无需额外配置。提交前用 `git status` 确认暂存内容中不含 `node_modules/`：

```bash
cd ~/projects/pbl5_retail_analysis_platform
git status
git add frontend/
git commit -m "chore: 初始化 Vite + Vue 3 工程（frontend/）"
git push origin main
```

#### 步骤 10：用 AI 生成空壳页面

在 AI 工具（Work Buddy等类似工具）中打开项目目录，将下面的提示词发给 AI。先请 AI 把你说的整理成开发需求清单，不清楚的地方它会提问；确认无误后，让它直接在项目里修改或新建代码文件。完成后按步骤 11 启动并验收页面，不准确的地方让 AI 继续修改。

```bash
请先浏览一下这个项目的结构（backend/ 和 frontend/），了解现有代码。我的需求是：

把 frontend/ 的默认欢迎页改成简单首页：
1. 页面顶部显示标题"零售经营分析平台"；
2. 中间放一张"后端状态"卡片：页面打开时自动请求后端 /health 和 /db/info 接口（具体地址和返回结构看 backend/ 代码），卡片里显示后端状态、后端版本、数据库版本和连通状态；请求失败时"连通状态"显示为红色"未连通"；
3. 卡片上放一个"刷新"按钮，点击后重新请求这两个接口。

本实验只做这一页，不需要菜单，也不需要页面跳转。页面请用 element-plus 组件实现；请求超时 10 秒，出错时弹出红色错误提示。

请你先不要写代码：先把我说的整理成一份开发需求清单，不清楚的地方问我，我确认后，你再直接修改项目里的代码文件。
```



#### 步骤 11：启动并验证前后端联通

确保后端已在运行（见步骤 6 的两种启动方式），另开一个终端启动前端：

```bash
npm run dev
```

浏览器打开 `http://localhost:5173`，应看到：

- 页面顶部标题"零售经营分析平台"
- 一张"后端状态"卡片：后端状态（ok）、后端版本、数据库版本、连通状态
- 点击"刷新"按钮可重新请求

预期结果：页面显示"后端状态：ok，数据库版本：8.4.x"，说明前后端已联通。打开浏览器开发者工具 → Network 面板，应能看到对 `/api/health` 和 `/api/db/info` 的成功请求。

![image-20260907015505778](/Users/liaoyulei/Library/Application Support/typora-user-images/image-20260907015505778.png)

常见问题排查：

- CORS 报错 → 检查后端 `allow_origins` 是否为 `["*"]`
- 请求 404 → 检查前端请求地址是否为 `http://127.0.0.1:8000/api/...`
- 数据库版本号为空 → 检查 `/api/db/info` 返回的 JSON 结构

#### 步骤 12：提交前端

```bash
git add .
git commit -m "feat: 单页空壳，前端调通后端 /api/health 与 /api/db/info"
git push origin main
```

## 注意事项

- 前后端端口冲突时（8000 或 5173 被占用），修改启动端口，因 CORS 已设为 `*`，不需要同步修改后端。
- VSCode 左下角必须显示 pbl5 环境，否则 Python 解释器选错将导致依赖找不到。
- Vibe Coding 产出不唯一，不同 AI 生成的代码可能不同，可运行但需要按步骤 11 的清单二次验证。