#!/bin/bash
#
# 企业项目管理系统 - 一键部署脚本
# Enterprise Project Management System - One-Click Deployment Script
#

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 打印函数
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查 Docker
check_docker() {
    print_info "检查 Docker 环境..."
    
    if ! command -v docker &> /dev/null; then
        print_error "Docker 未安装，请先安装 Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose 未安装，请先安装 Docker Compose"
        exit 1
    fi
    
    # 检查 Docker 是否运行
    if ! docker info &> /dev/null; then
        print_error "Docker 服务未运行，请启动 Docker 服务"
        exit 1
    fi
    
    print_success "Docker 环境检查通过"
}

# 检查环境变量
check_env() {
    print_info "检查环境变量配置..."
    
    if [ ! -f ".env" ]; then
        print_warning ".env 文件不存在，从 .env.example 复制..."
        cp .env.example .env
        print_warning "请编辑 .env 文件，修改 SECRET_KEY 等敏感配置"
    fi
    
    print_success "环境变量检查完成"
}

# 构建镜像
build_images() {
    print_info "构建 Docker 镜像..."
    
    docker-compose build --no-cache
    
    print_success "镜像构建完成"
}

# 启动服务
start_services() {
    print_info "启动服务..."
    
    docker-compose up -d
    
    print_success "服务已启动"
}

# 等待服务就绪
wait_for_services() {
    print_info "等待服务就绪..."
    
    # 等待后端服务
    print_info "等待后端服务 (端口 8000)..."
    for i in {1..30}; do
        if curl -s http://localhost:8000/health &> /dev/null; then
            print_success "后端服务已就绪"
            break
        fi
        sleep 1
    done
    
    # 等待前端服务
    print_info "等待前端服务 (端口 80)..."
    for i in {1..30}; do
        if curl -s http://localhost &> /dev/null; then
            print_success "前端服务已就绪"
            break
        fi
        sleep 1
    done
}

# 显示状态
show_status() {
    print_info "服务状态："
    echo ""
    docker-compose ps
    echo ""
    print_success "部署完成！"
    echo ""
    echo -e "${GREEN}访问地址：${NC}"
    echo -e "  前端界面: ${BLUE}http://localhost${NC}"
    echo -e "  后端 API: ${BLUE}http://localhost:8000${NC}"
    echo -e "  API 文档: ${BLUE}http://localhost:8000/docs${NC}"
    echo ""
    echo -e "${YELLOW}常用命令：${NC}"
    echo "  查看日志: docker-compose logs -f"
    echo "  停止服务: docker-compose down"
    echo "  重启服务: docker-compose restart"
}

# 主函数
main() {
    echo "========================================"
    echo "  企业项目管理系统 - 部署脚本"
    echo "========================================"
    echo ""
    
    # 检查是否在项目根目录
    if [ ! -f "docker-compose.yml" ]; then
        print_error "请在项目根目录运行此脚本"
        exit 1
    fi
    
    # 执行部署步骤
    check_docker
    check_env
    build_images
    start_services
    wait_for_services
    show_status
}

# 处理参数
case "${1:-}" in
    "stop")
        print_info "停止服务..."
        docker-compose down
        print_success "服务已停止"
        ;;
    "restart")
        print_info "重启服务..."
        docker-compose restart
        print_success "服务已重启"
        ;;
    "logs")
        docker-compose logs -f
        ;;
    "update")
        print_info "更新部署..."
        git pull origin master
        docker-compose down
        docker-compose up -d --build
        print_success "更新完成"
        ;;
    "backup")
        print_info "备份数据..."
        BACKUP_DIR="backup/$(date +%Y%m%d_%H%M%S)"
        mkdir -p "$BACKUP_DIR"
        docker cp epms-backend:/app/data/app.db "$BACKUP_DIR/" 2>/dev/null || true
        docker cp epms-backend:/app/logs "$BACKUP_DIR/" 2>/dev/null || true
        print_success "备份完成: $BACKUP_DIR"
        ;;
    "")
        main
        ;;
    *)
        echo "用法: $0 [stop|restart|logs|update|backup]"
        echo ""
        echo "命令说明："
        echo "  (无参数)  - 执行完整部署"
        echo "  stop      - 停止服务"
        echo "  restart   - 重启服务"
        echo "  logs      - 查看日志"
        echo "  update    - 更新代码并重新部署"
        echo "  backup    - 备份数据"
        exit 1
        ;;
esac
