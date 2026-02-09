from app.core.database import engine, Base

# 初始化数据库
def init_db():
    """
    创建所有数据库表
    
    此函数用于在应用启动时初始化数据库结构
    """
    # 创建所有表
    Base.metadata.create_all(bind=engine)
    print("数据库表已创建成功")

if __name__ == "__main__":
    init_db()
