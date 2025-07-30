"""
状态码定义

定义API响应的标准状态码
"""

from enum import IntEnum
from typing import Dict, Any


class StatusCode(IntEnum):
    """API状态码枚举"""
    
    # 成功状态码 (200-299)
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # 客户端错误 (400-499)
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    VALIDATION_ERROR = 422
    TOO_MANY_REQUESTS = 429
    
    # 服务器错误 (500-599)
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    
    # 自定义业务状态码 (1000+)
    HOOK_ERROR = 1001
    CACHE_ERROR = 1002
    DATABASE_ERROR = 1003
    RELATION_ERROR = 1004
    PERMISSION_DENIED = 1005
    DUPLICATE_ENTRY = 1006
    INVALID_OPERATION = 1007
    RESOURCE_LOCKED = 1008
    QUOTA_EXCEEDED = 1009
    DEPENDENCY_ERROR = 1010


# 状态码对应的消息
STATUS_MESSAGES: Dict[int, str] = {
    # 成功状态码
    StatusCode.SUCCESS: "操作成功",
    StatusCode.CREATED: "创建成功", 
    StatusCode.ACCEPTED: "请求已接受",
    StatusCode.NO_CONTENT: "操作成功，无返回内容",
    
    # 客户端错误
    StatusCode.BAD_REQUEST: "请求参数错误",
    StatusCode.UNAUTHORIZED: "未授权访问",
    StatusCode.FORBIDDEN: "禁止访问",
    StatusCode.NOT_FOUND: "资源不存在",
    StatusCode.METHOD_NOT_ALLOWED: "请求方法不允许",
    StatusCode.CONFLICT: "资源冲突",
    StatusCode.VALIDATION_ERROR: "数据验证失败",
    StatusCode.TOO_MANY_REQUESTS: "请求过于频繁",
    
    # 服务器错误
    StatusCode.INTERNAL_ERROR: "服务器内部错误",
    StatusCode.NOT_IMPLEMENTED: "功能未实现",
    StatusCode.BAD_GATEWAY: "网关错误",
    StatusCode.SERVICE_UNAVAILABLE: "服务不可用",
    StatusCode.GATEWAY_TIMEOUT: "网关超时",
    
    # 自定义业务状态码
    StatusCode.HOOK_ERROR: "Hook执行失败",
    StatusCode.CACHE_ERROR: "缓存操作失败",
    StatusCode.DATABASE_ERROR: "数据库操作失败",
    StatusCode.RELATION_ERROR: "关系处理失败",
    StatusCode.PERMISSION_DENIED: "权限不足",
    StatusCode.DUPLICATE_ENTRY: "数据重复",
    StatusCode.INVALID_OPERATION: "无效操作",
    StatusCode.RESOURCE_LOCKED: "资源被锁定",
    StatusCode.QUOTA_EXCEEDED: "配额超限",
    StatusCode.DEPENDENCY_ERROR: "依赖错误",
}


def get_status_message(code: int, default: str = "未知状态") -> str:
    """
    获取状态码对应的消息
    
    Args:
        code: 状态码
        default: 默认消息
        
    Returns:
        str: 状态消息
    """
    return STATUS_MESSAGES.get(code, default)


def create_response_data(
    code: int,
    message: str = None,
    data: Any = None,
    **kwargs
) -> Dict[str, Any]:
    """
    创建标准响应数据
    
    Args:
        code: 状态码
        message: 自定义消息
        data: 响应数据
        **kwargs: 其他响应字段
        
    Returns:
        Dict[str, Any]: 响应数据
    """
    response = {
        "code": code,
        "message": message or get_status_message(code),
        "data": data
    }
    
    # 添加其他字段
    response.update(kwargs)
    
    return response


def is_success_code(code: int) -> bool:
    """
    判断是否为成功状态码
    
    Args:
        code: 状态码
        
    Returns:
        bool: 是否成功
    """
    return 200 <= code < 300


def is_error_code(code: int) -> bool:
    """
    判断是否为错误状态码
    
    Args:
        code: 状态码
        
    Returns:
        bool: 是否错误
    """
    return code >= 400


def is_client_error(code: int) -> bool:
    """
    判断是否为客户端错误
    
    Args:
        code: 状态码
        
    Returns:
        bool: 是否客户端错误
    """
    return 400 <= code < 500


def is_server_error(code: int) -> bool:
    """
    判断是否为服务器错误
    
    Args:
        code: 状态码
        
    Returns:
        bool: 是否服务器错误
    """
    return code >= 500


def is_business_error(code: int) -> bool:
    """
    判断是否为业务错误
    
    Args:
        code: 状态码
        
    Returns:
        bool: 是否业务错误
    """
    return code >= 1000


# 常用状态码快捷方式
class Status:
    """状态码快捷方式"""
    
    # 成功
    OK = StatusCode.SUCCESS
    CREATED = StatusCode.CREATED
    
    # 客户端错误
    BAD_REQUEST = StatusCode.BAD_REQUEST
    UNAUTHORIZED = StatusCode.UNAUTHORIZED
    FORBIDDEN = StatusCode.FORBIDDEN
    NOT_FOUND = StatusCode.NOT_FOUND
    VALIDATION_ERROR = StatusCode.VALIDATION_ERROR
    
    # 服务器错误
    INTERNAL_ERROR = StatusCode.INTERNAL_ERROR
    
    # 业务错误
    HOOK_ERROR = StatusCode.HOOK_ERROR
    CACHE_ERROR = StatusCode.CACHE_ERROR
    DATABASE_ERROR = StatusCode.DATABASE_ERROR
    PERMISSION_DENIED = StatusCode.PERMISSION_DENIED


__all__ = [
    "StatusCode",
    "STATUS_MESSAGES",
    "Status",
    "get_status_message",
    "create_response_data",
    "is_success_code",
    "is_error_code",
    "is_client_error",
    "is_server_error",
    "is_business_error"
]
