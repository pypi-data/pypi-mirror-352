"""
异常处理模块

提供统一的异常处理和错误响应
"""

import logging
from typing import Any, Dict, Optional
from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

try:
    from tortoise.exceptions import ValidationError as TortoiseValidationError, IntegrityError
    TORTOISE_AVAILABLE = True
except ImportError:
    TORTOISE_AVAILABLE = False
    TortoiseValidationError = Exception
    IntegrityError = Exception

logger = logging.getLogger(__name__)


class CrudException(Exception):
    """CRUD操作基础异常"""

    def __init__(
        self,
        message: str,
        code: int = 400,
        details: Optional[Dict[str, Any]] = None,
        status_code: int = 400
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        self.status_code = status_code
        super().__init__(self.message)


class ValidationError(CrudException):
    """数据验证异常"""

    def __init__(
        self,
        message: str,
        field: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        from ..core.status_codes import StatusCode
        super().__init__(message, StatusCode.VALIDATION_ERROR, details, 422)
        self.field = field


class NotFoundError(CrudException):
    """资源不存在异常"""

    def __init__(
        self,
        resource: str,
        identifier: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} with identifier '{identifier}' not found"
        from ..core.status_codes import StatusCode
        super().__init__(message, StatusCode.NOT_FOUND, details, 404)
        self.resource = resource
        self.identifier = identifier


class DuplicateError(CrudException):
    """重复资源异常"""

    def __init__(
        self,
        resource: str,
        field: str,
        value: Any,
        details: Optional[Dict[str, Any]] = None
    ):
        message = f"{resource} with {field}='{value}' already exists"
        from ..core.status_codes import StatusCode
        super().__init__(message, StatusCode.DUPLICATE_ENTRY, details, 409)
        self.resource = resource
        self.field = field
        self.value = value


class PermissionError(CrudException):
    """权限异常"""
    
    def __init__(
        self,
        message: str = "Permission denied",
        details: Optional[Dict[str, Any]] = None
    ):
        from ..core.status_codes import StatusCode
        super().__init__(message, StatusCode.PERMISSION_DENIED, details, 403)


class CacheError(CrudException):
    """缓存操作异常"""
    
    def __init__(
        self,
        message: str,
        operation: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        from ..core.status_codes import StatusCode
        super().__init__(message, StatusCode.CACHE_ERROR, details, 500)
        self.operation = operation


class HookError(CrudException):
    """Hook执行异常"""
    
    def __init__(
        self,
        message: str,
        hook_name: str = None,
        stage: str = None,
        details: Optional[Dict[str, Any]] = None
    ):
        from ..core.status_codes import StatusCode
        super().__init__(message, StatusCode.HOOK_ERROR, details, 500)
        self.hook_name = hook_name
        self.stage = stage


def create_error_response(
    status_code: int,
    message: str,
    code: int = None,
    details: Optional[Dict[str, Any]] = None
) -> JSONResponse:
    """创建统一的错误响应"""
    from ..core.status_codes import StatusCode
    if code is None:
        code = StatusCode.INTERNAL_ERROR

    content = {
        "success": False,
        "message": message,
        "code": code,
        "data": None
    }
    
    if details:
        content["details"] = details
    
    return JSONResponse(
        status_code=status_code,
        content=content
    )


async def crud_exception_handler(request: Request, exc: CrudException) -> JSONResponse:
    """CRUD异常处理器"""
    logger.error(f"CRUD Exception: {exc.code} - {exc.message}", extra={"details": exc.details})
    
    return create_error_response(
        status_code=exc.status_code,
        message=exc.message,
        code=exc.code,
        details=exc.details
    )


async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    """HTTP异常处理器"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")

    from ..core.status_codes import StatusCode
    return create_error_response(
        status_code=exc.status_code,
        message=str(exc.detail),
        code=exc.status_code  # 使用HTTP状态码
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    """请求验证异常处理器"""
    logger.warning(f"Validation Exception: {exc.errors()}")
    
    # 格式化验证错误
    errors = []
    for error in exc.errors():
        field = ".".join(str(loc) for loc in error["loc"])
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    from ..core.status_codes import StatusCode
    return create_error_response(
        status_code=422,
        message="Validation failed",
        code=StatusCode.VALIDATION_ERROR,
        details={"errors": errors}
    )


async def tortoise_validation_exception_handler(request: Request, exc: TortoiseValidationError) -> JSONResponse:
    """Tortoise ORM验证异常处理器"""
    logger.warning(f"Tortoise Validation Exception: {str(exc)}")
    
    # 解析Tortoise验证错误
    error_message = str(exc)
    
    # 尝试提取字段名和错误信息
    if ":" in error_message:
        parts = error_message.split(":", 1)
        if len(parts) == 2:
            field_info = parts[0].strip()
            error_detail = parts[1].strip()
            
            # 提取字段名
            if "{" in field_info and "}" in field_info:
                field_name = field_info.split("{")[1].split("}")[0]
                message = f"字段 '{field_name}': {error_detail}"
            else:
                message = error_message
        else:
            message = error_message
    else:
        message = error_message
    
    from ..core.status_codes import StatusCode
    return create_error_response(
        status_code=422,
        message=message,
        code=StatusCode.VALIDATION_ERROR,
        details={"original_error": error_message}
    )


async def tortoise_integrity_exception_handler(request: Request, exc: IntegrityError) -> JSONResponse:
    """Tortoise ORM完整性约束异常处理器"""
    logger.warning(f"Tortoise Integrity Exception: {str(exc)}")
    
    error_message = str(exc).lower()
    
    # 处理常见的完整性约束错误
    if "unique constraint" in error_message or "duplicate" in error_message:
        # 尝试提取字段名
        if "." in error_message:
            parts = error_message.split(".")
            if len(parts) >= 2:
                field_name = parts[-1].strip()
                message = f"字段 '{field_name}' 的值已存在，请使用不同的值"
            else:
                message = "数据重复，请检查唯一字段的值"
        else:
            message = "数据重复，请检查唯一字段的值"
        
        from ..core.status_codes import StatusCode
        return create_error_response(
            status_code=409,
            message=message,
            code=StatusCode.DUPLICATE_ENTRY,
            details={"original_error": str(exc)}
        )
    
    elif "foreign key constraint" in error_message:
        message = "外键约束失败，请检查关联数据是否存在"
        from ..core.status_codes import StatusCode
        return create_error_response(
            status_code=400,
            message=message,
            code=StatusCode.BAD_REQUEST,
            details={"original_error": str(exc)}
        )
    
    elif "not null constraint" in error_message:
        # 尝试提取字段名
        if "." in error_message:
            parts = error_message.split(".")
            if len(parts) >= 2:
                field_name = parts[-1].strip()
                message = f"必填字段 '{field_name}' 不能为空"
            else:
                message = "必填字段不能为空"
        else:
            message = "必填字段不能为空"
        
        from ..core.status_codes import StatusCode
        return create_error_response(
            status_code=422,
            message=message,
            code=StatusCode.VALIDATION_ERROR,
            details={"original_error": str(exc)}
        )
    
    else:
        from ..core.status_codes import StatusCode
        return create_error_response(
            status_code=400,
            message=f"数据完整性错误: {str(exc)}",
            code=StatusCode.BAD_REQUEST,
            details={"original_error": str(exc)}
        )


async def general_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """通用异常处理器"""
    logger.error(f"Unexpected error: {type(exc).__name__} - {str(exc)}", exc_info=True)

    from ..core.status_codes import StatusCode
    return create_error_response(
        status_code=500,
        message="Internal server error",
        code=StatusCode.INTERNAL_ERROR,
        details={"error_type": type(exc).__name__} if logger.level <= logging.DEBUG else None
    )


def setup_exception_handlers(app):
    """设置异常处理器"""
    # 自定义异常处理器
    app.add_exception_handler(CrudException, crud_exception_handler)
    
    # Tortoise ORM异常处理器（如果可用）
    if TORTOISE_AVAILABLE:
        app.add_exception_handler(TortoiseValidationError, tortoise_validation_exception_handler)
        app.add_exception_handler(IntegrityError, tortoise_integrity_exception_handler)
    
    # FastAPI异常处理器
    app.add_exception_handler(HTTPException, http_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    
    # 通用异常处理器（最后注册）
    app.add_exception_handler(Exception, general_exception_handler)


__all__ = [
    "CrudException",
    "ValidationError",
    "NotFoundError",
    "DuplicateError", 
    "PermissionError",
    "CacheError",
    "HookError",
    "create_error_response",
    "setup_exception_handlers"
]
