"""
核心响应模式
"""

from typing import Any, Optional, List, Generic, TypeVar
from pydantic import BaseModel, Field
from fastapi import Query
from .status_codes import StatusCode, get_status_message

T = TypeVar('T')


class PaginationParams:
    """
    分页参数类

    替代 fastapi-pagination 的 Params 类
    """

    def __init__(
        self,
        page: int = Query(1, ge=1, description="页码，从1开始"),
        size: int = Query(20, ge=1, le=100, description="每页大小，最大100")
    ):
        self.page = page
        self.size = size


class BaseResponse(BaseModel, Generic[T]):
    """基础响应模式"""

    code: int = Field(200, description="响应状态码")
    message: str = Field("操作成功", description="响应消息")
    data: Optional[T] = Field(None, description="响应数据")

    def __init__(self, code: int = None, message: str = None, data: Any = None, **kwargs):
        """
        初始化响应

        Args:
            code: 状态码，默认为200
            message: 消息，如果为None则根据状态码自动生成
            data: 响应数据
            **kwargs: 其他参数
        """
        if code is None:
            code = StatusCode.SUCCESS

        if message is None:
            message = get_status_message(code)

        super().__init__(code=code, message=message, data=data, **kwargs)

    class Config:
        json_encoders = {
            # 自定义编码器
        }


class ErrorResponse(BaseModel):
    """错误响应模式"""

    code: int = Field(description="错误状态码")
    message: str = Field(description="错误消息")
    data: Optional[dict] = Field(None, description="错误详情")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 422,
                "message": "字段 'username': Value must not be None",
                "data": {
                    "field": "username",
                    "original_error": "username: Value must not be None"
                }
            }
        }


class PaginationInfo(BaseModel):
    """分页信息"""
    
    page: int = Field(description="当前页码")
    size: int = Field(description="每页大小")
    total: int = Field(description="总记录数")
    pages: int = Field(description="总页数")
    has_next: bool = Field(description="是否有下一页")
    has_prev: bool = Field(description="是否有上一页")


class PaginatedData(BaseModel, Generic[T]):
    """分页数据模式"""

    items: List[T] = Field(description="数据列表")
    pagination: PaginationInfo = Field(description="分页信息")


class PaginatedResponse(BaseModel, Generic[T]):
    """分页响应模式"""

    code: int = Field(200, description="响应状态码")
    message: str = Field("查询成功", description="响应消息")
    data: PaginatedData[T] = Field(description="分页数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "查询成功",
                "data": {
                    "items": [
                        {
                            "id": 1,
                            "username": "john_doe",
                            "email": "john@example.com",
                            "is_active": True
                        }
                    ],
                    "pagination": {
                        "page": 1,
                        "size": 20,
                        "total": 1,
                        "pages": 1,
                        "has_next": False,
                        "has_prev": False
                    }
                }
            }
        }


class BulkData(BaseModel):
    """批量操作数据模式"""

    total: int = Field(description="总处理数量")
    success_count: int = Field(description="成功数量")
    error_count: int = Field(description="失败数量")
    errors: Optional[List[dict]] = Field(None, description="错误详情")


class BulkResponse(BaseModel):
    """批量操作响应"""

    code: int = Field(200, description="响应状态码")
    message: str = Field(description="响应消息")
    data: BulkData = Field(description="批量操作数据")

    class Config:
        json_schema_extra = {
            "example": {
                "code": 200,
                "message": "批量创建完成",
                "data": {
                    "total": 10,
                    "success_count": 8,
                    "error_count": 2,
                    "errors": [
                        {
                            "index": 3,
                            "error": "字段 'email' 已存在"
                        },
                        {
                            "index": 7,
                            "error": "字段 'username' 不能为空"
                        }
                    ]
                }
            }
        }


class HealthResponse(BaseModel):
    """健康检查响应"""
    
    status: str = Field("healthy", description="服务状态")
    timestamp: str = Field(description="检查时间")
    version: str = Field(description="版本号")
    features: dict = Field(description="功能状态")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "timestamp": "2024-01-01T00:00:00Z",
                "version": "0.4.0",
                "features": {
                    "cache": "enabled",
                    "hooks": "enabled", 
                    "monitoring": "enabled"
                }
            }
        }


class StatsResponse(BaseModel):
    """统计信息响应"""
    
    model: str = Field(description="模型名称")
    total_records: int = Field(description="总记录数")
    cache_stats: Optional[dict] = Field(None, description="缓存统计")
    performance_stats: Optional[dict] = Field(None, description="性能统计")
    
    class Config:
        json_schema_extra = {
            "example": {
                "model": "User",
                "total_records": 1250,
                "cache_stats": {
                    "hit_rate": 85.3,
                    "total_hits": 1024,
                    "total_misses": 180
                },
                "performance_stats": {
                    "avg_response_time": 0.045,
                    "total_requests": 5000,
                    "error_rate": 0.02
                }
            }
        }


__all__ = [
    "PaginationParams",
    "BaseResponse",
    "ErrorResponse",
    "PaginatedResponse",
    "BulkResponse",
    "HealthResponse",
    "StatsResponse",
    "PaginationInfo",
    "PaginatedData",
    "BulkData"
]
