from pydantic import BaseModel
from typing import Generic, TypeVar, List, Optional

# 通用响应模型
T = TypeVar('T')

class ResponseModel(BaseModel, Generic[T]):
    """
    通用响应模型
    """
    success: bool = True
    message: str = "操作成功"
    data: Optional[T] = None
    count: Optional[int] = None

# 分页响应模型
class PaginationResponse(BaseModel, Generic[T]):
    """
    分页响应模型
    """
    success: bool = True
    message: str = "操作成功"
    data: List[T]
    total: int
    page: int
    page_size: int

# 错误响应模型
class ErrorResponse(BaseModel):
    """
    错误响应模型
    """
    success: bool = False
    message: str
    error_code: str = "UNKNOWN_ERROR"
    details: Optional[dict] = None
