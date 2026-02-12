# 部署配置目录

本目录包含企业项目管理系统的完整部署配置。

## 目录结构

```
deployment/
├── docker-compose.yml      # Docker Compose 生产环境配置
├── nginx.conf             # Nginx 反向代理配置
├── docker/                # Docker 相关配置
│   └── nginx/            # Nginx Docker 配置
├── kubernetes/           # Kubernetes 部署配置
│   ├── backend-deployment.yaml   # 后端部署
│   ├── frontend-deployment.yaml  # 前端部署
│   ├── secret.yaml              # 密钥配置
│   └── pvc.yaml                 # 持久化存储
└── README.md             # 本文件
```

## 快速开始

### Docker Compose 部署

```bash
# 进入部署目录
cd deployment

# 配置环境变量
cp ../.env.example .env
# 编辑 .env 文件，修改必要配置

# 启动服务
docker-compose up -d

# 查看状态
docker-compose ps

# 停止服务
docker-compose down
```

### Kubernetes 部署

```bash
# 进入 K8s 目录
cd deployment/kubernetes

# 创建命名空间
kubectl create namespace epms

# 部署应用
kubectl apply -f . -n epms

# 查看状态
kubectl get pods -n epms
```

## 详细文档

查看完整的部署指南：
- [部署指南 (docs/DEPLOYMENT_GUIDE.md)](../docs/DEPLOYMENT_GUIDE.md)

## 环境变量

复制 `.env.example` 到 `.env` 并修改以下关键配置：

- `SECRET_KEY`: JWT 密钥（生产环境必须修改）
- `DATABASE_URL`: 数据库连接 URL
- `VITE_API_BASE_URL`: 前端 API 地址

## 端口映射

| 服务 | 内部端口 | 外部端口 | 说明 |
|------|----------|----------|------|
| Nginx | 80/443 | 80/443 | Web 入口 |
| 后端 API | 8000 | 8000 | FastAPI 服务 |
| 前端 | 80 | 3002 | Vue 应用 |

## 故障排查

查看详细文档中的 [故障排查](../docs/DEPLOYMENT_GUIDE.md#故障排查) 章节。

常用命令：

```bash
# 查看日志
docker-compose logs -f

# 重启服务
docker-compose restart

# 进入容器
docker exec -it epms-backend /bin/sh
```
