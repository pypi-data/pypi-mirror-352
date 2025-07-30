"""
CRUD路由实现

提供具体的CRUD操作端点
"""

import time
import logging
from typing import Type, Optional, List, Dict, Any, Union
from fastapi import Request, Query, HTTPException, Depends
from ..core.schemas import PaginationParams
from tortoise.models import Model
from pydantic import BaseModel as PydanticModel

from ..core.types import CrudConfig
from ..core.schemas import (
    BaseResponse, PaginatedResponse, BulkResponse,
    PaginatedData, PaginationInfo, BulkData
)
from ..core.status_codes import StatusCode
from ..features.caching import CacheManager
from ..features.hooks import HookManager, HookStage, HookContext
from ..features.monitoring import MonitoringManager
from ..features.relations import RelationHandler
from ..features.relations.utils import RelationUtils
from ..utils.exceptions import NotFoundError, ValidationError
from ..utils.helpers import generate_cache_key, process_text_filters

logger = logging.getLogger(__name__)


class CrudRoutes:
    """
    CRUD路由实现类
    
    提供所有CRUD操作的具体实现
    """
    
    def __init__(
        self,
        model: Type[Model],
        config: CrudConfig,
        cache_manager: Optional[CacheManager] = None,
        hook_manager: Optional[HookManager] = None,
        monitoring_manager: Optional[MonitoringManager] = None,
        relation_handler: Optional[RelationHandler] = None
    ):
        """
        初始化CRUD路由
        
        Args:
            model: 模型类
            config: CRUD配置
            cache_manager: 缓存管理器
            hook_manager: Hook管理器
            monitoring_manager: 监控管理器
            relation_handler: 关系处理器
        """
        self.model = model
        self.config = config
        self.cache_manager = cache_manager
        self.hook_manager = hook_manager
        self.monitoring_manager = monitoring_manager
        self.relation_handler = relation_handler
    
    async def list_items(
        self,
        filters: Dict[str, Any] = None,
        order_by: Union[str, List[str]] = Query(default="-create_time"),
        params: PaginationParams = Depends(),
        request: Request = None
    ) -> PaginatedResponse:
        """
        列表查询
        
        Args:
            request: 请求对象
            filters: 过滤条件
            order_by: 排序字段
            params: 分页参数
            
        Returns:
            PaginatedResponse: 分页响应
        """
        start_time = time.time()
        
        try:
            # 创建Hook上下文
            context = HookContext(
                stage=HookStage.PRE_LIST,
                model=self.model,
                request=request,
                data={"filters": filters, "order_by": order_by, "params": params}
            )
            
            # 执行PRE_LIST Hook
            if self.hook_manager:
                hook_data = {"filters": filters, "order_by": order_by, "params": params}
                hook_result = await self.hook_manager.execute_hooks(HookStage.PRE_LIST, hook_data, context)
                # 应用Hook的修改
                if hook_result and isinstance(hook_result, dict):
                    if "filters" in hook_result:
                        filters = hook_result["filters"]
                    if "order_by" in hook_result:
                        order_by = hook_result["order_by"]

            # 标准化order_by参数
            if isinstance(order_by, str):
                order_by = [order_by]
            elif order_by is None:
                order_by = ["-create_time"]

            # 处理过滤条件，移除分页参数
            clean_filters = {}
            if filters:
                # 移除分页参数，这些参数不应该传递给Tortoise ORM
                pagination_params = {'page', 'size', 'limit', 'offset'}
                clean_filters = {k: v for k, v in filters.items() if k not in pagination_params and v is not None}

                # 处理时间范围过滤
                from ..utils.helpers import process_time_range_filters
                clean_filters = process_time_range_filters(clean_filters)

                # 处理文本字段过滤（转换为包含查询）
                clean_filters = process_text_filters(
                    self.model,
                    clean_filters,
                    use_contains=self.config.text_contains_search
                )

            # 生成缓存键
            cache_key = None
            if self.cache_manager and self.cache_manager.enabled:
                cache_key = generate_cache_key(
                    "list",
                    self.model.__name__,
                    clean_filters,
                    order_by,
                    params.page,
                    params.size
                )
                
                # 尝试从缓存获取
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    # 记录缓存命中
                    if self.monitoring_manager:
                        self.monitoring_manager.record_cache_operation("list", hit=True)
                    
                    # 执行缓存命中Hook
                    if self.hook_manager:
                        await self.hook_manager.execute_hooks(HookStage.ON_CACHE_HIT, cached_result, context)
                    
                    return PaginatedResponse(**cached_result)
                else:
                    # 记录缓存未命中
                    if self.monitoring_manager:
                        self.monitoring_manager.record_cache_operation("list", hit=False)
            
            # 构建查询
            query = self.model.all()

            # 应用过滤条件
            if clean_filters:
                query = query.filter(**clean_filters)
            
            # 应用排序
            if order_by:
                query = query.order_by(*order_by)
            
            # 预加载关系
            if self.config.relations:
                valid_relations = self.relation_handler.get_preload_relations(self.config.relations)
                if valid_relations:
                    query = query.prefetch_related(*valid_relations)
            
            # 分页查询
            total = await query.count()
            items = await query.offset((params.page - 1) * params.size).limit(params.size)
            
            # 转换为响应格式
            data = []
            for item in items:
                if self.config.read_schema:
                    item_data = await self.config.read_schema.from_tortoise_orm(item)
                    data.append(item_data.dict() if hasattr(item_data, 'dict') else item_data)
                else:
                    # 如果没有定义read_schema，自动查询关联数据
                    if self.relation_handler:
                        item_data = await self.relation_handler.serialize_with_relations(item)
                        data.append(item_data)
                    else:
                        data.append(item.__dict__)
            
            # 构建响应
            pages = (total + params.size - 1) // params.size

            pagination_info = PaginationInfo(
                page=params.page,
                size=params.size,
                total=total,
                pages=pages,
                has_next=params.page < pages,
                has_prev=params.page > 1
            )

            paginated_data = PaginatedData(
                items=data,
                pagination=pagination_info
            )

            result = {
                "code": StatusCode.SUCCESS,
                "message": "查询成功",
                "data": paginated_data
            }
            
            # 缓存结果
            if cache_key and self.cache_manager:
                await self.cache_manager.set(cache_key, result)
            
            # 执行POST_LIST Hook
            if self.hook_manager:
                context.data = result
                await self.hook_manager.execute_hooks(HookStage.POST_LIST, result, context)
            
            # 记录性能指标
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("list", duration, self.model.__name__)
            
            return PaginatedResponse(**result)
            
        except Exception as e:
            # 记录错误
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("list", duration, self.model.__name__, success=False)
            
            logger.error(f"列表查询失败: {e}")
            raise e
    
    async def create_item(
        self,
        item_data: dict,
        request: Request = None
    ) -> BaseResponse:
        """
        创建记录
        
        Args:
            item_data: 创建数据
            request: 请求对象
            
        Returns:
            BaseResponse: 创建响应
        """
        start_time = time.time()
        
        try:
            # 转换数据
            data = item_data
            
            # 创建Hook上下文
            context = HookContext(
                stage=HookStage.PRE_CREATE,
                model=self.model,
                request=request,
                data=data
            )
            
            # 执行PRE_VALIDATE Hook
            if self.hook_manager:
                data = await self.hook_manager.execute_hooks(HookStage.PRE_VALIDATE, data, context)
            
            # 执行PRE_CREATE Hook
            if self.hook_manager:
                data = await self.hook_manager.execute_hooks(HookStage.PRE_CREATE, data, context)
            
            # 分离关系数据
            normal_data, relation_data = RelationUtils.extract_relation_data(data)
            
            # 创建记录
            instance = await self.model.create(**normal_data)
            
            # 处理关系
            if relation_data and self.relation_handler:
                instance = await self.relation_handler.handle_relations_on_create(instance, relation_data)
            
            # 转换为响应格式
            if self.config.read_schema:
                response_data = await self.config.read_schema.from_tortoise_orm(instance)
                response_data = response_data.dict() if hasattr(response_data, 'dict') else response_data
            else:
                response_data = instance.__dict__
            
            # 更新上下文
            context.data = response_data
            context.id = instance.id
            
            # 执行POST_CREATE Hook
            if self.hook_manager:
                response_data = await self.hook_manager.execute_hooks(HookStage.POST_CREATE, response_data, context)
            
            # 清除相关缓存
            if self.cache_manager and self.cache_manager.enabled:
                await self.cache_manager.delete_pattern(f"list:{self.model.__name__}:*")
            
            # 记录性能指标
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("create", duration, self.model.__name__)
            
            # 应用响应修改
            from ..core.status_codes import StatusCode
            response = BaseResponse(
                code=StatusCode.CREATED,
                message="创建成功",
                data=response_data
            )

            # 如果Hook修改了响应数据，应用修改
            if context.response_modifications.get("data"):
                response.data = context.response_modifications["data"]

            # 应用响应头和Cookie修改
            from fastapi import Response
            from fastapi_tortoise_crud.features.hooks.response_handler import ResponseHandler

            # 创建FastAPI Response对象来应用修改
            fastapi_response = Response()
            ResponseHandler.apply_response_modifications(fastapi_response, context)

            return response
            
        except Exception as e:
            # 记录错误
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("create", duration, self.model.__name__, success=False)
            
            logger.error(f"创建记录失败: {e}")
            raise e
    
    async def read_item(
        self,
        item_id: int,
        request: Request = None
    ) -> BaseResponse:
        """
        读取记录
        
        Args:
            item_id: 记录ID
            request: 请求对象
            
        Returns:
            BaseResponse: 读取响应
        """
        start_time = time.time()
        
        try:
            # 创建Hook上下文
            context = HookContext(
                stage=HookStage.PRE_READ,
                model=self.model,
                request=request,
                id=item_id
            )
            
            # 执行PRE_READ Hook
            if self.hook_manager:
                await self.hook_manager.execute_hooks(HookStage.PRE_READ, {"id": item_id}, context)
            
            # 生成缓存键
            cache_key = None
            if self.cache_manager and self.cache_manager.enabled:
                cache_key = generate_cache_key("read", self.model.__name__, item_id)
                
                # 尝试从缓存获取
                cached_result = await self.cache_manager.get(cache_key)
                if cached_result:
                    # 记录缓存命中
                    if self.monitoring_manager:
                        self.monitoring_manager.record_cache_operation("read", hit=True)
                    
                    # 执行缓存命中Hook
                    if self.hook_manager:
                        await self.hook_manager.execute_hooks(HookStage.ON_CACHE_HIT, cached_result, context)
                    
                    return BaseResponse(**cached_result)
                else:
                    # 记录缓存未命中
                    if self.monitoring_manager:
                        self.monitoring_manager.record_cache_operation("read", hit=False)
            
            # 构建查询
            query = self.model.filter(id=item_id)
            
            # 预加载关系
            if self.config.relations:
                valid_relations = self.relation_handler.get_preload_relations(self.config.relations)
                if valid_relations:
                    query = query.prefetch_related(*valid_relations)
            
            # 查询记录
            instance = await query.first()
            if not instance:
                raise NotFoundError(self.model.__name__, item_id)
            
            # 转换为响应格式
            logger.info(f"read_schema存在: {self.config.read_schema is not None}")
            if self.config.read_schema:
                response_data = await self.config.read_schema.from_tortoise_orm(instance)
                response_data = response_data.dict() if hasattr(response_data, 'dict') else response_data
                logger.info("使用read_schema序列化")
            else:
                # 如果没有定义read_schema，自动查询关联数据
                logger.info("使用自动关联查询序列化")
                if self.relation_handler:
                    response_data = await self.relation_handler.serialize_with_relations(instance)
                else:
                    response_data = instance.__dict__
            
            # 构建响应
            from ..core.status_codes import StatusCode
            result = {
                "code": StatusCode.SUCCESS,
                "message": "查询成功",
                "data": response_data
            }
            
            # 缓存结果
            if cache_key and self.cache_manager:
                await self.cache_manager.set(cache_key, result)
            
            # 更新上下文
            context.data = response_data
            
            # 执行POST_READ Hook
            if self.hook_manager:
                response_data = await self.hook_manager.execute_hooks(HookStage.POST_READ, response_data, context)
                # 如果Hook修改了响应数据，应用修改
                if context.response_modifications.get("data"):
                    response_data = context.response_modifications["data"]
                # 更新result中的数据
                result["data"] = response_data

            # 记录性能指标
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("read", duration, self.model.__name__)

            return BaseResponse(**result)

        except Exception as e:
            # 记录错误
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("read", duration, self.model.__name__, success=False)

            logger.error(f"读取记录失败: {e}")
            raise e

    async def update_item(
        self,
        item_id: int,
        item_data: dict,
        request: Request = None
    ) -> BaseResponse:
        """
        更新记录

        Args:
            item_id: 记录ID
            item_data: 更新数据
            request: 请求对象

        Returns:
            BaseResponse: 更新响应
        """
        start_time = time.time()

        try:
            # 转换数据
            data = item_data

            # 创建Hook上下文
            context = HookContext(
                stage=HookStage.PRE_UPDATE,
                model=self.model,
                request=request,
                id=item_id,
                data=data
            )

            # 查找记录
            instance = await self.model.filter(id=item_id).first()
            if not instance:
                raise NotFoundError(self.model.__name__, item_id)

            # 保存原始数据
            context.original_data = instance.__dict__.copy()

            # 执行PRE_UPDATE Hook
            if self.hook_manager:
                data = await self.hook_manager.execute_hooks(HookStage.PRE_UPDATE, data, context)

            # 分离关系数据
            from ..features.relations.utils import RelationUtils
            normal_data, relation_data = RelationUtils.extract_relation_data(data)

            # 更新基础字段
            if normal_data:
                await self.model.filter(id=item_id).update(**normal_data)
                # 重新获取实例
                instance = await self.model.filter(id=item_id).first()

            # 处理关系
            if relation_data and self.relation_handler:
                instance = await self.relation_handler.handle_relations_on_update(instance, relation_data)

            # 转换为响应格式
            if self.config.read_schema:
                response_data = await self.config.read_schema.from_tortoise_orm(instance)
                response_data = response_data.dict() if hasattr(response_data, 'dict') else response_data
            else:
                response_data = instance.__dict__

            # 更新上下文
            context.data = response_data

            # 执行POST_UPDATE Hook
            if self.hook_manager:
                response_data = await self.hook_manager.execute_hooks(HookStage.POST_UPDATE, response_data, context)

            # 清除相关缓存
            if self.cache_manager and self.cache_manager.enabled:
                await self.cache_manager.delete_pattern(f"*:{self.model.__name__}:*")

            # 记录性能指标
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("update", duration, self.model.__name__)

            from ..core.status_codes import StatusCode
            return BaseResponse(
                code=StatusCode.SUCCESS,
                message="更新成功",
                data=response_data
            )

        except Exception as e:
            # 记录错误
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("update", duration, self.model.__name__, success=False)

            logger.error(f"更新记录失败: {e}")
            raise e

    async def delete_item(
        self,
        item_id: int,
        request: Request = None
    ) -> BaseResponse:
        """
        删除记录

        Args:
            item_id: 记录ID
            request: 请求对象

        Returns:
            BaseResponse: 删除响应
        """
        start_time = time.time()

        try:
            # 创建Hook上下文
            context = HookContext(
                stage=HookStage.PRE_DELETE,
                model=self.model,
                request=request,
                id=item_id
            )

            # 查找记录
            instance = await self.model.filter(id=item_id).first()
            if not instance:
                raise NotFoundError(self.model.__name__, item_id)

            # 保存原始数据
            context.original_data = instance.__dict__.copy()

            # 执行PRE_DELETE Hook
            if self.hook_manager:
                await self.hook_manager.execute_hooks(HookStage.PRE_DELETE, {"id": item_id}, context)

            # 处理关系删除
            if self.relation_handler:
                await self.relation_handler.handle_relations_on_delete(instance)

            # 删除记录
            deleted_count = await self.model.filter(id=item_id).delete()

            # 执行POST_DELETE Hook
            if self.hook_manager:
                await self.hook_manager.execute_hooks(HookStage.POST_DELETE, {"deleted_count": deleted_count}, context)

            # 清除相关缓存
            if self.cache_manager and self.cache_manager.enabled:
                await self.cache_manager.delete_pattern(f"*:{self.model.__name__}:*")

            # 记录性能指标
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("delete", duration, self.model.__name__)

            from ..core.status_codes import StatusCode
            return BaseResponse(
                code=StatusCode.SUCCESS,
                message="删除成功",
                data={"deleted_count": deleted_count}
            )

        except Exception as e:
            # 记录错误
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("delete", duration, self.model.__name__, success=False)

            logger.error(f"删除记录失败: {e}")
            raise e

    async def bulk_create_items(
        self,
        items_data: List[dict],
        request: Request = None
    ) -> BulkResponse:
        """
        批量创建记录

        Args:
            items_data: 创建数据列表
            request: 请求对象

        Returns:
            BulkResponse: 批量创建响应
        """
        start_time = time.time()

        try:
            total = len(items_data)
            success_count = 0
            error_count = 0
            errors = []

            for i, item_data in enumerate(items_data):
                try:
                    # 转换数据
                    data = item_data

                    # 分离关系数据
                    normal_data, relation_data = RelationUtils.extract_relation_data(data)

                    # 创建记录
                    instance = await self.model.create(**normal_data)

                    # 处理关系
                    if relation_data and self.relation_handler:
                        await self.relation_handler.handle_relations_on_create(instance, relation_data)

                    success_count += 1

                except Exception as e:
                    error_count += 1
                    errors.append({
                        "index": i,
                        "error": str(e)
                    })
                    logger.warning(f"批量创建第{i}项失败: {e}")

            # 清除相关缓存
            if self.cache_manager and self.cache_manager.enabled:
                await self.cache_manager.delete_pattern(f"list:{self.model.__name__}:*")

            # 记录性能指标
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("bulk_create", duration, self.model.__name__)

            bulk_data = BulkData(
                total=total,
                success_count=success_count,
                error_count=error_count,
                errors=errors if errors else None
            )

            return BulkResponse(
                code=StatusCode.SUCCESS if error_count == 0 else StatusCode.ACCEPTED,
                message=f"批量创建完成，成功{success_count}项，失败{error_count}项",
                data=bulk_data
            )

        except Exception as e:
            logger.error(f"批量创建失败: {e}")
            raise e

    async def bulk_delete_items(
        self,
        item_ids: List[int],
        request: Request = None
    ) -> BulkResponse:
        """
        批量删除记录

        Args:
            item_ids: 记录ID列表
            request: 请求对象

        Returns:
            BulkResponse: 批量删除响应
        """
        start_time = time.time()

        try:
            total = len(item_ids)

            # 批量删除
            deleted_count = await self.model.filter(id__in=item_ids).delete()

            # 清除相关缓存
            if self.cache_manager and self.cache_manager.enabled:
                await self.cache_manager.delete_pattern(f"*:{self.model.__name__}:*")

            # 记录性能指标
            if self.monitoring_manager:
                duration = time.time() - start_time
                self.monitoring_manager.record_database_query("bulk_delete", duration, self.model.__name__)

            from ..core.schemas import BulkData

            bulk_data = BulkData(
                total=total,
                success_count=deleted_count,
                error_count=total - deleted_count,
                errors=None
            )

            from ..core.status_codes import StatusCode
            return BulkResponse(
                code=StatusCode.SUCCESS,
                message=f"批量删除完成，删除{deleted_count}项",
                data=bulk_data
            )

        except Exception as e:
            logger.error(f"批量删除失败: {e}")
            raise e

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        try:
            # 测试数据库连接
            await self.model.all().count()

            health_data = {
                "status": "healthy",
                "model": self.model.__name__,
                "timestamp": time.time(),
                "components": {
                    "database": "healthy",
                    "cache": "healthy" if self.cache_manager and self.cache_manager.enabled else "disabled",
                    "hooks": "healthy" if self.hook_manager and self.hook_manager.enabled else "disabled",
                    "monitoring": "healthy" if self.monitoring_manager and self.monitoring_manager.enabled else "disabled"
                }
            }

            # 检查缓存健康
            if self.cache_manager and self.cache_manager.enabled:
                cache_health = await self.cache_manager.health_check()
                health_data["components"]["cache"] = cache_health["status"]

            # 检查监控健康
            if self.monitoring_manager and self.monitoring_manager.enabled:
                monitoring_health = await self.monitoring_manager.health_check()
                health_data["components"]["monitoring"] = monitoring_health["status"]

            from ..core.status_codes import StatusCode
            return {
                "code": StatusCode.SUCCESS,
                "message": "健康检查成功",
                "data": health_data
            }

        except Exception as e:
            from ..core.status_codes import StatusCode
            return {
                "code": StatusCode.INTERNAL_ERROR,
                "message": f"健康检查失败: {str(e)}",
                "data": {
                    "status": "unhealthy",
                    "model": self.model.__name__,
                    "error": str(e),
                    "timestamp": time.time()
                }
            }

    async def model_info(self) -> Dict[str, Any]:
        """模型信息"""
        try:
            info_data = {
                "name": self.model.__name__,
                "table": getattr(self.model._meta, 'table', ''),
                "fields": {},
                "relations": {},
                "config": {
                    "cache_enabled": self.cache_manager and self.cache_manager.enabled,
                    "hooks_enabled": self.hook_manager and self.hook_manager.enabled,
                    "monitoring_enabled": self.monitoring_manager and self.monitoring_manager.enabled,
                    "relations": self.config.relations
                }
            }

            # 字段信息
            if hasattr(self.model, '_meta'):
                for field_name, field in self.model._meta.fields_map.items():
                    info_data["fields"][field_name] = {
                        "type": type(field).__name__,
                        "null": getattr(field, 'null', False),
                        "unique": getattr(field, 'unique', False),
                        "max_length": getattr(field, 'max_length', None)
                    }

            # 关系信息
            from ..features.relations.utils import RelationUtils
            relations = RelationUtils.get_model_relations(self.model)
            for field_name, field in relations.items():
                info_data["relations"][field_name] = {
                    "type": type(field).__name__,
                    "related_model": getattr(field, 'related_model', {}).get('__name__', '') if hasattr(field, 'related_model') else ''
                }

            from ..core.status_codes import StatusCode
            return {
                "code": StatusCode.SUCCESS,
                "message": "获取模型信息成功",
                "data": info_data
            }

        except Exception as e:
            logger.error(f"获取模型信息失败: {e}")
            from ..core.status_codes import StatusCode
            return {
                "code": StatusCode.INTERNAL_ERROR,
                "message": f"获取模型信息失败: {str(e)}",
                "data": {"error": str(e)}
            }

    async def performance_stats(self) -> Dict[str, Any]:
        """性能统计"""
        if not self.monitoring_manager or not self.monitoring_manager.enabled:
            return {"error": "监控未启用"}

        try:
            return self.monitoring_manager.get_performance_report()
        except Exception as e:
            logger.error(f"获取性能统计失败: {e}")
            return {"error": str(e)}

    async def cache_stats(self) -> Dict[str, Any]:
        """缓存统计"""
        if not self.cache_manager or not self.cache_manager.enabled:
            return {"error": "缓存未启用"}

        try:
            return self.cache_manager.get_stats()
        except Exception as e:
            logger.error(f"获取缓存统计失败: {e}")
            return {"error": str(e)}

    async def hook_stats(self) -> Dict[str, Any]:
        """Hook统计"""
        if not self.hook_manager or not self.hook_manager.enabled:
            return {"error": "Hook系统未启用"}

        try:
            return self.hook_manager.get_stats()
        except Exception as e:
            logger.error(f"获取Hook统计失败: {e}")
            return {"error": str(e)}


__all__ = ["CrudRoutes"]
