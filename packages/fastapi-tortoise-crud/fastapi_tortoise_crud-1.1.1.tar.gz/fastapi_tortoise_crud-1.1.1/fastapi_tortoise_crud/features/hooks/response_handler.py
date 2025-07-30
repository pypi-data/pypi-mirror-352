"""
Hook响应处理器

处理Hook系统中的request和response修改
"""

from typing import Any, Dict
from fastapi import Response
from .types import HookContext


class ResponseHandler:
    """响应处理器"""
    
    @staticmethod
    def apply_response_modifications(response: Response, context: HookContext) -> Response:
        """
        应用Hook上下文中的响应修改
        
        Args:
            response: FastAPI响应对象
            context: Hook上下文
            
        Returns:
            Response: 修改后的响应对象
        """
        if not context.response_modifications:
            return response
        
        # 应用响应头修改
        headers = context.response_modifications.get("headers", {})
        for key, value in headers.items():
            response.headers[key] = value
        
        # 应用Cookie修改
        cookies = context.response_modifications.get("cookies", {})
        for key, cookie_data in cookies.items():
            value = cookie_data.pop("value")
            response.set_cookie(key, value, **cookie_data)
        
        return response
    
    @staticmethod
    def apply_request_modifications(request_data: Dict[str, Any], context: HookContext) -> Dict[str, Any]:
        """
        应用Hook上下文中的请求修改
        
        Args:
            request_data: 请求数据
            context: Hook上下文
            
        Returns:
            Dict[str, Any]: 修改后的请求数据
        """
        if not context.request_modifications:
            return request_data
        
        # 应用请求体修改
        if "body" in context.request_modifications:
            return context.request_modifications["body"]
        
        return request_data
