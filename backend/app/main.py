from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# 导入路由
from app.routers import auth, projects

# 创建 FastAPI 应用实例
app = FastAPI(
    title="企业项目管理系统 API",
    description="企业级项目管理系统的后端 API 接口",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# 配置 CORS（允许前端开发服务器访问）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "http://127.0.0.1:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Backend is running"}

# 根端点
@app.get("/")
async def root():
    return {
        "message": "欢迎使用企业项目管理系统 API",
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health"
    }

# 包含路由
app.include_router(auth.router)
app.include_router(projects.router)
