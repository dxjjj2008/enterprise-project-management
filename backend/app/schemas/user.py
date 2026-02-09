from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

# 用户基础模型
class UserBase(BaseModel):
    email: EmailStr
    username: str
    is_active: bool = True

# 用户创建模型
class UserCreate(UserBase):
    password: str

# 用户登录模型
class UserLogin(BaseModel):
    email: EmailStr
    password: str

# 用户响应模型（不包含密码）
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# 用户更新模型
class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    is_active: Optional[bool] = None

# 令牌模型
class Token(BaseModel):
    access_token: str
    token_type: str

# 令牌数据模型
class TokenData(BaseModel):
    user_id: Optional[int] = None
    email: Optional[str] = None
