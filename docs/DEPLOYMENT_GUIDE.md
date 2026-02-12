# 企业项目管理系统 - 部署指南
# Enterprise Project Management System - Deployment Guide

**版本**: v1.0  
**更新日期**: 2026-02-12  
**适用版本**: v2.1+

---

## 目录

1. [概述](#概述)
2. [环境要求](#环境要求)
3. [快速部署](#快速部署)
4. [开发环境部署](#开发环境部署)
5. [生产环境部署](#生产环境部署)
6. [Docker 部署](#docker-部署)
7. [Kubernetes 部署](#kubernetes-部署)
8. [环境变量配置](#环境变量配置)
9. [常见问题](#常见问题)
10. [故障排查](#故障排查)

---

## 概述

本文档提供企业项目管理系统的完整部署指南，包括：

- 开发环境快速启动
- 生产环境 Docker 部署
- Kubernetes 集群部署
- CI/CD 自动化部署
- 环境变量配置
- 故障排查指南

### 部署架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户访问层                            │
│                    (Browser/Mobile)                          │
└───────────────────────┬─────────────────────────────────────┘
                        │
                        ▼
┌─────────────────────────────────────────────────────────────┐
│                      Nginx 反向代理                          │
│              (负载均衡、SSL终止、静态资源)                    │
└───────────┬───────────────────────────────┬─────────────────┘
            │                               │
            ▼                               ▼
┌───────────────────────┐       ┌─────────────────────────────┐
│     前端服务          │       │       后端 API 服务         │
│   (Vue 3 + Nginx)     │◄─────►│   (FastAPI + SQLite)       │
│       Port: 80        │       │       Port: 8000            │
└───────────────────────┘       └───────────┬─────────────────┘
                                            │
                                            ▼
                                ┌─────────────────────────────┐
                                │      SQLite 数据库          │
                                │    (文件存储，自动初始化)    │
                                └─────────────────────────────┘
```

---

## 环境要求

### 系统要求

| 组件 | 最低配置 | 推荐配置 |
|------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 20GB | 50GB+ SSD |
| 网络 | 10Mbps | 100Mbps+ |

### 软件依赖

#### 开发环境
- **Node.js**: 18+ (前端)
- **Python**: 3.11+ (后端)
- **npm**: 9+ 或 **yarn**: 1.22+
- **Git**: 2.30+

#### 生产环境 (Docker)
- **Docker**: 24.0+
- **Docker Compose**: 2.20+

#### 生产环境 (Kubernetes)
- **Kubernetes**: 1.28+
- **kubectl**: 1.28+
- **Helm**: 3.12+ (可选)

---

## 快速部署

### 方式一：Docker Compose（推荐）

```bash
# 1. 克隆代码
git clone https://github.com/dxjjj2008/enterprise-project-management.git
cd enterprise-project-management

# 2. 启动服务
docker-compose up -d

# 3. 查看状态
docker-compose ps

# 4. 访问系统
# 前端: http://localhost
# 后端 API: http://localhost:8000
# API 文档: http://localhost:8000/docs
```

### 方式二：手动部署

```bash
# 1. 克隆代码
git clone https://github.com/dxjjj2008/enterprise-project-management.git
cd enterprise-project-management

# 2. 启动后端
cd backend
pip install -r requirements.txt
python init_database.py
bash start.sh

# 3. 启动前端（新终端）
cd frontend
npm install
npm run dev

# 4. 访问系统
# 前端: http://localhost:3001
# 后端 API: http://localhost:8000
```

---

## 开发环境部署

### 1. 后端部署

```bash
cd backend

# 创建虚拟环境（推荐）
python3 -m venv venv
source venv/bin/activate  # Linux/Mac
# 或: venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 初始化数据库
python init_database.py

# 启动服务
bash start.sh
# 或: uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 前端部署

```bash
cd frontend

# 安装依赖
npm install

# 开发模式
npm run dev

# 构建生产包
npm run build

# 预览生产包
npm run preview
```

### 3. 运行测试

```bash
# 后端测试
cd backend
pytest -v

# 前端单元测试
cd frontend
npm run test:run

# 前端 E2E 测试
npm run test:e2e
```

---

## 生产环境部署

### 部署前准备

1. **服务器准备**
   - 安装 Docker 和 Docker Compose
   - 配置防火墙（开放 80/443 端口）
   - 配置域名解析

2. **安全设置**
   - 修改默认 SECRET_KEY
   - 配置 SSL 证书
   - 设置数据库备份

3. **环境变量**
   ```bash
   # 复制环境变量模板
   cp .env.example .env
   
   # 编辑配置
   nano .env
   ```

### Docker 生产部署

```bash
# 1. 进入部署目录
cd deployment

# 2. 配置环境变量
cp .env.example .env
nano .env

# 3. 构建并启动
docker-compose up -d --build

# 4. 查看日志
docker-compose logs -f

# 5. 停止服务
docker-compose down

# 6. 停止并删除数据卷（谨慎操作）
docker-compose down -v
```

### Nginx 配置

生产环境 Nginx 配置文件位于 `deployment/nginx.conf`，包含：

- 反向代理配置
- 负载均衡
- 静态资源服务
- SSL/HTTPS 支持
- 健康检查
- Gzip 压缩

#### 启用 HTTPS

```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # ... 其他配置
}
```

---

## Docker 部署

### 镜像构建

```bash
# 构建后端镜像
docker build -t epms-backend:latest ./backend

# 构建前端镜像
docker build -t epms-frontend:latest ./frontend

# 查看镜像
docker images | grep epms
```

### 容器管理

```bash
# 查看运行中的容器
docker ps

# 查看容器日志
docker logs -f epms-backend

# 进入容器
docker exec -it epms-backend /bin/sh

# 重启容器
docker restart epms-backend

# 停止容器
docker stop epms-backend

# 删除容器
docker rm epms-backend
```

### 数据持久化

```bash
# 查看数据卷
docker volume ls

# 备份数据
docker run --rm -v epms_backend_data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz -C /data .

# 恢复数据
docker run --rm -v epms_backend_data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /data
```

---

## Kubernetes 部署

### 快速部署

```bash
# 进入 K8s 配置目录
cd deployment/kubernetes

# 创建命名空间
kubectl create namespace epms

# 部署应用
kubectl apply -f . -n epms

# 查看状态
kubectl get pods -n epms
kubectl get svc -n epms

# 查看日志
kubectl logs -f deployment/backend -n epms
```

### K8s 资源清单

```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: epms-backend
spec:
  replicas: 3
  selector:
    matchLabels:
      app: epms-backend
  template:
    metadata:
      labels:
        app: epms-backend
    spec:
      containers:
      - name: backend
        image: epms-backend:latest
        ports:
        - containerPort: 8000
        env:
        - name: SECRET_KEY
          valueFrom:
            secretKeyRef:
              name: epms-secrets
              key: secret-key
```

---

## 环境变量配置

### 后端环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `DATABASE_URL` | 数据库连接URL | `sqlite:///./app.db` | 是 |
| `SECRET_KEY` | JWT密钥 | - | 是 |
| `ALGORITHM` | JWT算法 | `HS256` | 否 |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token过期时间 | `30` | 否 |
| `REDIS_URL` | Redis连接URL | - | 否 |
| `LOG_LEVEL` | 日志级别 | `INFO` | 否 |

### 前端环境变量

| 变量名 | 说明 | 默认值 | 必填 |
|--------|------|--------|------|
| `VITE_API_BASE_URL` | API基础URL | `http://localhost:8000` | 是 |

### 环境变量文件示例

```bash
# .env 文件
# 后端配置
DATABASE_URL=sqlite:///./data/app.db
SECRET_KEY=your-256-bit-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 前端配置
VITE_API_BASE_URL=http://localhost:8000
```

---

## 常见问题

### Q1: 如何修改默认端口？

**A:** 修改 `docker-compose.yml` 中的端口映射：

```yaml
services:
  backend:
    ports:
      - "8080:8000"  # 主机8080映射到容器8000
```

### Q2: 如何更新部署？

**A:** 
```bash
# 拉取最新代码
git pull origin master

# 重新构建并部署
docker-compose up -d --build
```

### Q3: 如何备份数据库？

**A:**
```bash
# SQLite备份
cp backend/app.db backup/app-$(date +%Y%m%d).db

# 或使用 Docker
docker cp epms-backend:/app/data/app.db ./backup/
```

### Q4: 如何查看日志？

**A:**
```bash
# Docker Compose
docker-compose logs -f backend

# Docker
docker logs -f epms-backend

# Kubernetes
kubectl logs -f deployment/epms-backend
```

### Q5: 如何重置管理员密码？

**A:**
```bash
# 进入后端容器
docker exec -it epms-backend /bin/sh

# 运行重置脚本
python -c "
from app.core.database import SessionLocal
from app.models.user import User
from passlib.context import CryptContext

db = SessionLocal()
pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
user = db.query(User).filter(User.username == 'admin').first()
if user:
    user.hashed_password = pwd_context.hash('newpassword')
    db.commit()
    print('Password reset successfully')
"
```

---

## 故障排查

### 1. 服务无法启动

**症状**: `docker-compose up` 后服务无法访问

**排查步骤**:
```bash
# 1. 检查容器状态
docker-compose ps

# 2. 查看日志
docker-compose logs backend

# 3. 检查端口占用
netstat -tlnp | grep 8000

# 4. 进入容器检查
docker exec -it epms-backend /bin/sh
```

### 2. 数据库连接失败

**症状**: 后端日志显示数据库错误

**解决方案**:
```bash
# 1. 检查数据库文件权限
ls -la backend/data/

# 2. 重新初始化数据库
docker exec epms-backend python init_database.py

# 3. 检查环境变量
docker exec epms-backend env | grep DATABASE
```

### 3. 前端无法访问后端

**症状**: 前端页面加载，但 API 请求失败

**排查步骤**:
```bash
# 1. 检查后端是否运行
curl http://localhost:8000/health

# 2. 检查前端配置
docker exec epms-frontend env | grep VITE

# 3. 检查网络连接
docker network inspect epms-network
```

### 4. 性能问题

**症状**: 系统响应缓慢

**优化建议**:
1. 增加服务器配置（CPU/内存）
2. 启用 Redis 缓存
3. 使用 PostgreSQL 替代 SQLite
4. 配置 Nginx 缓存
5. 启用 Gzip 压缩

---

## 附录

### A. 部署检查清单

- [ ] 服务器资源满足最低要求
- [ ] Docker 和 Docker Compose 已安装
- [ ] 环境变量已正确配置
- [ ] SECRET_KEY 已修改（生产环境）
- [ ] SSL 证书已配置（生产环境）
- [ ] 防火墙端口已开放
- [ ] 数据库备份策略已制定
- [ ] 监控告警已配置

### B. 常用命令速查

```bash
# 部署
docker-compose up -d
docker-compose down
docker-compose logs -f

# 构建
docker-compose build
docker-compose up -d --build

# 更新
git pull
docker-compose up -d --build

# 备份
docker exec epms-backend tar czf /tmp/backup.tar.gz /app/data
docker cp epms-backend:/tmp/backup.tar.gz ./

# 恢复
docker cp ./backup.tar.gz epms-backend:/tmp/
docker exec epms-backend tar xzf /tmp/backup.tar.gz -C /
```

### C. 联系支持

- **GitHub Issues**: https://github.com/dxjjj2008/enterprise-project-management/issues
- **文档**: https://github.com/dxjjj2008/enterprise-project-management/tree/main/docs

---

**最后更新**: 2026-02-12  
**版本**: v1.0
