#!/bin/bash
# 企业项目管理系统 - 后端启动脚本

# 激活虚拟环境
source venv/bin/activate

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3 命令"
    exit 1
fi

# 检查依赖
echo "正在检查依赖..."
python3 -c "from main import app" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "正在安装依赖..."
    pip install -r requirements.txt
fi

# 初始化数据库
echo "正在初始化数据库..."
python3 -c "from app.models.database import init_db; init_db(); print('数据库初始化完成')"

# 启动服务
echo "正在启动 FastAPI 服务..."
python3 main.py
