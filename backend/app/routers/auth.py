from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import Optional, Annotated
from datetime import timedelta

# 导入 Pydantic 模型
from app.schemas.user import UserLogin, UserCreate, Token, TokenData, UserResponse
from app.schemas.common import ResponseModel, ErrorResponse

# 导入数据库相关
from app.core.database import get_db
from sqlalchemy.orm import Session
from app.models.user import User

# 导入密码哈希
from passlib.context import CryptContext

# 导入安全模块
from app.core.security import verify_password, get_password_hash, create_access_token, decode_access_token

# 密码上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# 创建认证路由器
router = APIRouter(
    prefix="/api/v1/auth",
    tags=["认证"],
    responses={404: {"description": "未找到"}}
)

# OAuth2 密码流配置
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

# 登录端点
@router.post("/login", response_model=ResponseModel[Token])
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_db)
):
    """
    用户登录
    
    返回 JWT 访问令牌
    """
    # 查询数据库验证用户
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="邮箱或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 生成 JWT 令牌
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": user.email, "user_id": user.id}, expires_delta=access_token_expires
    )
    
    return ResponseModel[Token](
        data=Token(access_token=access_token, token_type="bearer"),
        message="登录成功"
    )

# 注册端点
@router.post("/register", response_model=ResponseModel[UserResponse])
async def register(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    用户注册
    
    创建新用户并返回用户信息
    """
    # 检查邮箱是否已存在
    existing_user = db.query(User).filter(User.email == user_create.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="邮箱已被注册"
        )
    
    # 创建新用户
    hashed_password = get_password_hash(user_create.password)
    user = User(
        email=user_create.email,
        username=user_create.username,
        hashed_password=hashed_password,
        is_active=True
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return ResponseModel[UserResponse](
        data=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        ),
        message="注册成功"
    )

# 获取当前用户
@router.get("/me", response_model=ResponseModel[UserResponse])
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    获取当前认证用户信息
    
    需要有效的 JWT 令牌
    """
    # 解码令牌获取用户邮箱
    payload = decode_access_token(token)
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的访问令牌",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 查询数据库获取用户信息
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    
    return ResponseModel[UserResponse](
        data=UserResponse(
            id=user.id,
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at
        ),
        message="获取用户信息成功"
    )
