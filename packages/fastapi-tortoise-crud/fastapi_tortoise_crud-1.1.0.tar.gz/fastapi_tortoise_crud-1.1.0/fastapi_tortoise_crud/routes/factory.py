"""
路由工厂

负责创建和配置CRUD路由
"""

import logging
from typing import Type, Optional, List, Dict, Any, Union
from fastapi import APIRouter, Depends, Query, Request
from tortoise.models import Model
from pydantic import BaseModel as PydanticModel
from ..core.schemas import PaginationParams

from ..core.types import CrudConfig
from ..core.schemas import BaseResponse, PaginatedResponse
from ..features.caching import CacheManager
from ..features.hooks import HookManager
from ..features.monitoring import MonitoringManager
from ..features.relations import RelationHandler
from .crud import CrudRoutes

logger = logging.getLogger(__name__)


class CrudRouteFactory:
    """
    CRUD路由工厂
    
    负责创建和配置完整的CRUD路由
    """
    
    def __init__(
        self,
        model: Type[Model],
        config: CrudConfig,
        cache_manager: Optional[CacheManager] = None,
        hook_manager: Optional[HookManager] = None,
        monitoring_manager: Optional[MonitoringManager] = None
    ):
        """
        初始化路由工厂
        
        Args:
            model: 模型类
            config: CRUD配置
            cache_manager: 缓存管理器
            hook_manager: Hook管理器
            monitoring_manager: 监控管理器
        """
        self.model = model
        self.config = config
        self.cache_manager = cache_manager
        self.hook_manager = hook_manager
        self.monitoring_manager = monitoring_manager
        
        # 初始化组件
        self.relation_handler = RelationHandler(model, debug_mode=config.debug_mode)
        self.crud_routes = CrudRoutes(
            model=model,
            config=config,
            cache_manager=cache_manager,
            hook_manager=hook_manager,
            monitoring_manager=monitoring_manager,
            relation_handler=self.relation_handler
        )
        
        # 生成Schema
        self._generate_schemas()
    
    def _generate_schemas(self):
        """生成Pydantic Schema"""
        try:
            # 如果没有提供自定义Schema，自动生成
            if not self.config.create_schema:
                self.config.create_schema = self._create_pydantic_schema("Create")

            if not self.config.read_schema:
                self.config.read_schema = self._create_pydantic_schema("Read")

            if not self.config.update_schema:
                self.config.update_schema = self._create_pydantic_schema("Update")

            # 自动生成过滤Schema
            if not hasattr(self.config, 'filter_schema') or not self.config.filter_schema:
                self.config.filter_schema = self._create_filter_schema()

        except Exception as e:
            logger.warning(f"自动生成Schema失败: {e}")

    def _create_pydantic_schema(self, schema_type: str) -> Type[PydanticModel]:
        """创建Pydantic Schema"""
        try:
            from tortoise.contrib.pydantic import pydantic_model_creator

            if schema_type == "Create":
                return pydantic_model_creator(
                    self.model,
                    name=f"{self.model.__name__}Create",
                    exclude_readonly=True
                )
            elif schema_type == "Read":
                # 为了支持自动关联查询，我们不生成Read Schema
                # 让系统使用自动序列化
                return None
            elif schema_type == "Update":
                return pydantic_model_creator(
                    self.model,
                    name=f"{self.model.__name__}Update",
                    exclude_readonly=True
                )
        except Exception as e:
            logger.error(f"创建{schema_type} Schema失败: {e}")
            return None

    def _create_filter_schema(self) -> Type[PydanticModel]:
        """创建过滤Schema"""
        try:
            from ..utils.schema_generator import SchemaGenerator

            return SchemaGenerator.generate_filter_schema(
                model=self.model,
                name=f"{self.model.__name__}Filter",
                include_time_range=True
            )
        except Exception as e:
            logger.error(f"创建过滤Schema失败: {e}")
            return None
    
    def create_router(self) -> APIRouter:
        """
        创建完整的CRUD路由器
        
        Returns:
            APIRouter: 配置好的路由器
        """
        # 获取路由器级别的依赖
        router_dependencies = self._get_router_dependencies()

        router = APIRouter(
            # 不在这里设置prefix，让用户在include_router时指定
            # prefix=self.config.prefix,
            tags=self.config.tags,  # 这里使用配置中的tags，用户可以通过include_router覆盖
            dependencies=router_dependencies
        )
        
        # 添加CRUD路由
        self._add_crud_routes(router)
        
        # 添加自定义路由
        self._add_custom_routes(router)
        
        # 添加统计路由
        self._add_stats_routes(router)
        
        return router
    
    def _add_crud_routes(self, router: APIRouter):
        """添加CRUD路由"""
        try:
            # 获取依赖配置
            dependencies_config = self._get_dependencies_config()

            # 列表查询
            list_deps = self._get_endpoint_dependencies("list", dependencies_config)

            # 创建list路由包装函数
            async def list_endpoint(
                filters: dict = None,
                order_by: Union[str, List[str]] = Query(default="-create_time"),
                params: PaginationParams = Depends(),
                request: Request = None
            ):
                return await self.crud_routes.list_items(
                    filters=filters,
                    order_by=order_by,
                    params=params,
                    request=request
                )

            router.add_api_route(
                "/list",
                list_endpoint,
                methods=["POST"],
                response_model=PaginatedResponse,
                summary=f"查询{self.model.__name__}列表",
                description=f"分页查询{self.model.__name__}列表，支持过滤和排序",
                dependencies=list_deps
            )
            
            # 创建
            create_deps = self._get_endpoint_dependencies("create", dependencies_config)
            router.add_api_route(
                "/create",
                self.crud_routes.create_item,
                methods=["POST"],
                response_model=BaseResponse,
                summary=f"创建{self.model.__name__}",
                description=f"创建新的{self.model.__name__}记录",
                dependencies=create_deps
            )

            # 读取
            read_deps = self._get_endpoint_dependencies("read", dependencies_config)
            router.add_api_route(
                "/read/{item_id}",
                self.crud_routes.read_item,
                methods=["GET"],
                response_model=BaseResponse,
                summary=f"读取{self.model.__name__}",
                description=f"根据ID读取{self.model.__name__}记录",
                dependencies=read_deps
            )

            # 更新
            update_deps = self._get_endpoint_dependencies("update", dependencies_config)
            router.add_api_route(
                "/update/{item_id}",
                self.crud_routes.update_item,
                methods=["PUT"],
                response_model=BaseResponse,
                summary=f"更新{self.model.__name__}",
                description=f"根据ID更新{self.model.__name__}记录",
                dependencies=update_deps
            )

            # 删除
            delete_deps = self._get_endpoint_dependencies("delete", dependencies_config)
            router.add_api_route(
                "/delete/{item_id}",
                self.crud_routes.delete_item,
                methods=["DELETE"],
                response_model=BaseResponse,
                summary=f"删除{self.model.__name__}",
                description=f"根据ID删除{self.model.__name__}记录",
                dependencies=delete_deps
            )

            # 批量创建
            bulk_create_deps = self._get_endpoint_dependencies("bulk_create", dependencies_config)
            router.add_api_route(
                "/bulk-create",
                self.crud_routes.bulk_create_items,
                methods=["POST"],
                response_model=BaseResponse,
                summary=f"批量创建{self.model.__name__}",
                description=f"批量创建{self.model.__name__}记录",
                dependencies=bulk_create_deps
            )

            # 批量删除
            bulk_delete_deps = self._get_endpoint_dependencies("bulk_delete", dependencies_config)
            router.add_api_route(
                "/bulk-delete",
                self.crud_routes.bulk_delete_items,
                methods=["POST"],
                response_model=BaseResponse,
                summary=f"批量删除{self.model.__name__}",
                description=f"批量删除{self.model.__name__}记录",
                dependencies=bulk_delete_deps
            )
            
        except Exception as e:
            logger.error(f"添加CRUD路由失败: {e}")
    
    def _add_custom_routes(self, router: APIRouter):
        """添加自定义路由"""
        # 获取依赖配置
        dependencies_config = self._get_dependencies_config()

        # 健康检查
        router.add_api_route(
            "/health",
            self.crud_routes.health_check,
            methods=["GET"],
            summary="健康检查",
            description="检查CRUD服务的健康状态",
            dependencies=dependencies_config.global_dependencies
        )

        # 模型信息
        router.add_api_route(
            "/info",
            self.crud_routes.model_info,
            methods=["GET"],
            summary="模型信息",
            description="获取模型的基本信息和字段定义",
            dependencies=dependencies_config.global_dependencies
        )
    
    def _add_stats_routes(self, router: APIRouter):
        """添加统计路由"""
        if self.monitoring_manager:
            # 性能统计
            router.add_api_route(
                "/stats/performance",
                self.crud_routes.performance_stats,
                methods=["GET"],
                summary="性能统计",
                description="获取CRUD操作的性能统计信息"
            )
            
            # 缓存统计
            if self.cache_manager:
                router.add_api_route(
                    "/stats/cache",
                    self.crud_routes.cache_stats,
                    methods=["GET"],
                    summary="缓存统计",
                    description="获取缓存的统计信息"
                )
            
            # Hook统计
            if self.hook_manager:
                router.add_api_route(
                    "/stats/hooks",
                    self.crud_routes.hook_stats,
                    methods=["GET"],
                    summary="Hook统计",
                    description="获取Hook系统的统计信息"
                )
    
    def add_custom_route(
        self,
        path: str,
        endpoint: callable,
        methods: List[str] = None,
        **kwargs
    ) -> APIRouter:
        """
        添加自定义路由
        
        Args:
            path: 路由路径
            endpoint: 端点函数
            methods: HTTP方法列表
            **kwargs: 其他路由参数
            
        Returns:
            APIRouter: 路由器实例
        """
        router = APIRouter()
        methods = methods or ["GET"]
        
        router.add_api_route(path, endpoint, methods=methods, **kwargs)
        return router
    
    def get_openapi_schema(self) -> Dict[str, Any]:
        """
        获取OpenAPI Schema
        
        Returns:
            Dict[str, Any]: OpenAPI Schema
        """
        router = self.create_router()
        
        # 生成基础Schema
        schema = {
            "openapi": "3.0.2",
            "info": {
                "title": f"{self.model.__name__} CRUD API",
                "version": "1.0.0",
                "description": f"自动生成的{self.model.__name__} CRUD API"
            },
            "paths": {},
            "components": {
                "schemas": {}
            }
        }
        
        # 添加路由信息
        for route in router.routes:
            if hasattr(route, 'path') and hasattr(route, 'methods'):
                path_info = {
                    method.lower(): {
                        "summary": getattr(route, 'summary', ''),
                        "description": getattr(route, 'description', ''),
                        "operationId": f"{method.lower()}_{route.path.replace('/', '_')}",
                        "responses": {
                            "200": {
                                "description": "Successful Response"
                            }
                        }
                    }
                    for method in route.methods if method != "HEAD"
                }
                schema["paths"][route.path] = path_info
        
        return schema

    def _get_dependencies_config(self):
        """获取依赖配置"""
        from ..core.dependencies import DependencyConfig

        if isinstance(self.config.dependencies, DependencyConfig):
            return self.config.dependencies
        elif isinstance(self.config.dependencies, list):
            # 兼容旧的列表格式，转换为DependencyConfig
            return DependencyConfig(global_dependencies=self.config.dependencies)
        else:
            # 返回空配置
            return DependencyConfig()

    def _get_endpoint_dependencies(self, endpoint_type: str, dependencies_config):
        """获取端点依赖"""
        from ..core.dependencies import EndpointType

        # 端点类型映射表
        endpoint_mapping = {
            "list": EndpointType.LIST,
            "create": EndpointType.CREATE,
            "read": EndpointType.READ,
            "update": EndpointType.UPDATE,
            "delete": EndpointType.DELETE,
            "bulk_create": EndpointType.BULK_CREATE,
            "bulk_delete": EndpointType.BULK_DELETE,
        }

        try:
            # 先尝试直接映射
            if endpoint_type in endpoint_mapping:
                endpoint_enum = endpoint_mapping[endpoint_type]
            else:
                # 尝试直接转换为枚举
                endpoint_enum = EndpointType(endpoint_type)

            return dependencies_config.get_dependencies_for_endpoint(endpoint_enum)
        except (ValueError, KeyError):
            # 如果端点类型不存在，返回全局依赖
            return dependencies_config.global_dependencies

    def _get_router_dependencies(self):
        """获取路由器级别的依赖"""
        from ..core.dependencies import DependencyConfig

        if isinstance(self.config.dependencies, DependencyConfig):
            # 对于DependencyConfig，路由器级别不设置依赖，由各个端点单独处理
            return []
        elif isinstance(self.config.dependencies, list):
            # 兼容旧的列表格式
            return self.config.dependencies
        else:
            # 默认返回空列表
            return []


__all__ = ["CrudRouteFactory"]
