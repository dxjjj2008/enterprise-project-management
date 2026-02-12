"""
数据库初始化脚本
"""
from app.core.database import engine, Base, SessionLocal
from app.models import *

def init_db():
    """初始化数据库表"""
    # 导入所有模型以确保它们已注册到 Base.metadata
    from app.models.user import User
    from app.models.project import Project, Task
    from app.models.issue import Issue, IssueComment
    from app.models.risk import Risk
    from app.models.approval import Approval, ApprovalHistory
    from app.models.plan import Plan, Milestone
    from app.models.resource import Resource, Label
    
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("✅ 数据库表创建成功")

def create_test_user():
    """创建测试用户"""
    from app.models.user import User
    from app.core.security import get_password_hash
    
    db = SessionLocal()
    try:
        # 检查是否已存在测试用户
        existing = db.query(User).filter(User.email == "test@example.com").first()
        if existing:
            print("✅ 测试用户已存在")
            return
        
        # 创建测试用户
        test_user = User(
            email="test@example.com",
            username="testuser",
            hashed_password=get_password_hash("test123456"),
            is_active=True
        )
        db.add(test_user)
        db.commit()
        print("✅ 测试用户创建成功")
    except Exception as e:
        db.rollback()
        print(f"❌ 创建测试用户失败: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("正在初始化数据库...")
    init_db()
    create_test_user()
    print("✅ 数据库初始化完成")
