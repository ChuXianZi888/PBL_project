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
        user="root", password="",
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