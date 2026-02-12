#!/bin/bash

# 启动 FastAPI 后端服务

# 检查 Python 环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3 命令"
    exit 1
fi

# 安装依赖
echo "正在安装依赖..."
pip install -r requirements.txt

# 初始化数据库
echo "正在初始化数据库..."
python -m app.core.init_db

# 启动服务
echo "正在启动 FastAPI 服务..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
