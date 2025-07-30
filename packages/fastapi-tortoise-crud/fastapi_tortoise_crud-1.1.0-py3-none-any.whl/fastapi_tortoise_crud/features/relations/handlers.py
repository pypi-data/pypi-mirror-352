"""
关系处理器

处理模型关系的创建、更新和删除
"""

import logging
from typing import Any, Dict, List, Optional, Type, Union
from tortoise.models import Model
from tortoise.fields.relational import (
    RelationalField, ForeignKeyFieldInstance, ManyToManyFieldInstance,
    OneToOneFieldInstance, ReverseRelation
)

logger = logging.getLogger(__name__)


class RelationHandler:
    """
    关系处理器
    
    处理模型之间的关系操作
    """
    
    def __init__(self, model: Type[Model], debug_mode: bool = False):
        """
        初始化关系处理器

        Args:
            model: 模型类
            debug_mode: 调试模式，控制详细日志输出
        """
        self.model = model
        self.debug_mode = debug_mode
        self._relation_fields = self._get_relation_fields()
    
    def _get_relation_fields(self) -> Dict[str, RelationalField]:
        """获取模型的关系字段"""
        relation_fields = {}
        
        if hasattr(self.model, '_meta'):
            for field_name, field in self.model._meta.fields_map.items():
                if isinstance(field, RelationalField):
                    relation_fields[field_name] = field
        
        return relation_fields
    
    async def handle_relations_on_create(self, instance: Model, data: Dict[str, Any]) -> Model:
        """
        处理创建时的关系
        
        Args:
            instance: 创建的实例
            data: 原始数据
            
        Returns:
            Model: 处理关系后的实例
        """
        try:
            # 处理外键关系
            await self._handle_foreign_keys(instance, data)
            
            # 处理多对多关系
            await self._handle_many_to_many(instance, data)
            
            # 处理反向关系
            await self._handle_reverse_relations(instance, data)
            
            return instance
            
        except Exception as e:
            logger.error(f"处理创建关系失败: {e}")
            raise e
    
    async def handle_relations_on_update(self, instance: Model, data: Dict[str, Any]) -> Model:
        """
        处理更新时的关系
        
        Args:
            instance: 更新的实例
            data: 更新数据
            
        Returns:
            Model: 处理关系后的实例
        """
        try:
            # 处理外键关系更新
            await self._handle_foreign_keys(instance, data, is_update=True)
            
            # 处理多对多关系更新
            await self._handle_many_to_many(instance, data, is_update=True)
            
            # 处理反向关系更新
            await self._handle_reverse_relations(instance, data, is_update=True)
            
            return instance
            
        except Exception as e:
            logger.error(f"处理更新关系失败: {e}")
            raise e
    
    async def handle_relations_on_delete(self, instance: Model) -> bool:
        """
        处理删除时的关系
        
        Args:
            instance: 要删除的实例
            
        Returns:
            bool: 是否成功处理
        """
        try:
            # 处理级联删除
            await self._handle_cascade_delete(instance)
            
            # 清理多对多关系
            await self._cleanup_many_to_many(instance)
            
            return True
            
        except Exception as e:
            logger.error(f"处理删除关系失败: {e}")
            return False
    
    async def _handle_foreign_keys(self, instance: Model, data: Dict[str, Any], is_update: bool = False):
        """处理外键关系"""
        for field_name, field in self._relation_fields.items():
            if not isinstance(field, ForeignKeyFieldInstance):
                continue
            
            # 检查数据中是否有相关字段
            fk_field_name = f"{field_name}_id"
            
            if field_name in data:
                # 直接关联对象
                related_obj = data[field_name]
                if related_obj:
                    if isinstance(related_obj, dict):
                        # 如果是字典，尝试创建或查找对象
                        related_instance = await self._get_or_create_related(field.related_model, related_obj)
                        setattr(instance, field_name, related_instance)
                    elif isinstance(related_obj, Model):
                        # 如果是模型实例，直接设置
                        setattr(instance, field_name, related_obj)
            
            elif fk_field_name in data:
                # 外键ID
                fk_id = data[fk_field_name]
                if fk_id:
                    try:
                        related_instance = await field.related_model.get(id=fk_id)
                        setattr(instance, field_name, related_instance)
                    except Exception as e:
                        logger.warning(f"找不到关联对象 {field.related_model.__name__}(id={fk_id}): {e}")
        
        # 保存外键更改
        if is_update:
            await instance.save()
    
    async def _handle_many_to_many(self, instance: Model, data: Dict[str, Any], is_update: bool = False):
        """处理多对多关系"""
        for field_name, field in self._relation_fields.items():
            if not isinstance(field, ManyToManyFieldInstance):
                continue
            
            if field_name in data:
                related_data = data[field_name]
                if related_data is not None:
                    await self._set_many_to_many_relations(instance, field_name, field, related_data, is_update)
    
    async def _set_many_to_many_relations(
        self, 
        instance: Model, 
        field_name: str, 
        field: ManyToManyFieldInstance,
        related_data: Union[List[Any], List[Dict], List[int]], 
        is_update: bool = False
    ):
        """设置多对多关系"""
        try:
            # 获取关系管理器
            relation_manager = getattr(instance, field_name)
            
            # 如果是更新，先清除现有关系
            if is_update:
                await relation_manager.clear()
            
            # 处理关联数据
            related_instances = []
            
            for item in related_data:
                if isinstance(item, int):
                    # ID
                    try:
                        related_instance = await field.related_model.get(id=item)
                        related_instances.append(related_instance)
                    except Exception as e:
                        logger.warning(f"找不到关联对象 {field.related_model.__name__}(id={item}): {e}")
                
                elif isinstance(item, dict):
                    # 字典数据
                    if 'id' in item:
                        # 有ID，尝试获取现有对象
                        try:
                            related_instance = await field.related_model.get(id=item['id'])
                            related_instances.append(related_instance)
                        except Exception:
                            # 如果找不到，尝试创建
                            related_instance = await self._get_or_create_related(field.related_model, item)
                            related_instances.append(related_instance)
                    else:
                        # 没有ID，创建新对象
                        related_instance = await self._get_or_create_related(field.related_model, item)
                        related_instances.append(related_instance)
                
                elif isinstance(item, Model):
                    # 模型实例
                    related_instances.append(item)
            
            # 添加关系
            if related_instances:
                await relation_manager.add(*related_instances)
                
        except Exception as e:
            logger.error(f"设置多对多关系失败 {field_name}: {e}")
            raise e
    
    async def _handle_reverse_relations(self, instance: Model, data: Dict[str, Any], is_update: bool = False):
        """处理反向关系"""
        # 处理反向外键关系（一对多）
        for field_name in data:
            if field_name.startswith('_reverse_'):
                reverse_field_name = field_name[9:]  # 移除 '_reverse_' 前缀
                reverse_data = data[field_name]
                
                if reverse_data:
                    await self._handle_reverse_foreign_key(instance, reverse_field_name, reverse_data, is_update)
    
    async def _handle_reverse_foreign_key(
        self, 
        instance: Model, 
        field_name: str, 
        reverse_data: List[Dict], 
        is_update: bool = False
    ):
        """处理反向外键关系"""
        try:
            # 获取反向关系的模型
            if hasattr(instance, field_name):
                relation_manager = getattr(instance, field_name)
                related_model = relation_manager.related_model
                
                # 如果是更新，可能需要处理现有关系
                if is_update:
                    existing_objects = await relation_manager.all()
                    existing_ids = {obj.id for obj in existing_objects}
                
                # 处理反向关系数据
                for item_data in reverse_data:
                    if isinstance(item_data, dict):
                        if 'id' in item_data and is_update:
                            # 更新现有对象
                            if item_data['id'] in existing_ids:
                                await related_model.filter(id=item_data['id']).update(**{
                                    k: v for k, v in item_data.items() if k != 'id'
                                })
                                existing_ids.discard(item_data['id'])
                        else:
                            # 创建新对象
                            item_data[self._get_foreign_key_field_name(related_model, instance)] = instance.id
                            await related_model.create(**item_data)
                
                # 删除不再需要的对象（如果是更新且有剩余的existing_ids）
                if is_update and existing_ids:
                    await related_model.filter(id__in=existing_ids).delete()
                    
        except Exception as e:
            logger.error(f"处理反向外键关系失败 {field_name}: {e}")
    
    def _get_foreign_key_field_name(self, related_model: Type[Model], target_instance: Model) -> str:
        """获取外键字段名"""
        # 查找指向目标模型的外键字段
        for field_name, field in related_model._meta.fields_map.items():
            if isinstance(field, ForeignKeyFieldInstance) and field.related_model == type(target_instance):
                return field_name
        
        # 如果找不到，使用约定的命名
        return f"{type(target_instance).__name__.lower()}_id"
    
    async def _get_or_create_related(self, model: Type[Model], data: Dict[str, Any]) -> Model:
        """获取或创建关联对象"""
        try:
            # 如果有ID，尝试获取
            if 'id' in data:
                try:
                    return await model.get(id=data['id'])
                except Exception:
                    pass
            
            # 尝试根据唯一字段查找
            unique_fields = self._get_unique_fields(model)
            if unique_fields:
                for field_name in unique_fields:
                    if field_name in data:
                        try:
                            return await model.get(**{field_name: data[field_name]})
                        except Exception:
                            continue
            
            # 创建新对象
            return await model.create(**data)
            
        except Exception as e:
            logger.error(f"获取或创建关联对象失败: {e}")
            raise e
    
    def _get_unique_fields(self, model: Type[Model]) -> List[str]:
        """获取模型的唯一字段"""
        unique_fields = []
        
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                if getattr(field, 'unique', False):
                    unique_fields.append(field_name)
        
        return unique_fields
    
    async def _handle_cascade_delete(self, instance: Model):
        """处理级联删除"""
        for field_name, field in self._relation_fields.items():
            if isinstance(field, ForeignKeyFieldInstance):
                # 检查是否需要级联删除
                if getattr(field, 'on_delete', None) == 'CASCADE':
                    related_objects = await field.related_model.filter(**{
                        f"{self._get_foreign_key_field_name(field.related_model, instance)}": instance.id
                    })
                    
                    for related_obj in related_objects:
                        await related_obj.delete()
    
    async def _cleanup_many_to_many(self, instance: Model):
        """清理多对多关系"""
        for field_name, field in self._relation_fields.items():
            if isinstance(field, ManyToManyFieldInstance):
                try:
                    relation_manager = getattr(instance, field_name)
                    await relation_manager.clear()
                except Exception as e:
                    logger.warning(f"清理多对多关系失败 {field_name}: {e}")
    
    def get_preload_relations(self, relations: List[str]) -> List[str]:
        """获取预加载关系列表"""
        valid_relations = []

        for relation in relations:
            if relation in self._relation_fields:
                valid_relations.append(relation)
            else:
                logger.warning(f"无效的关系字段: {relation}")

        return valid_relations

    def get_auto_relations(self, max_depth: int = 1) -> List[str]:
        """
        获取自动关系列表（用于自动查询关联数据）

        Args:
            max_depth: 最大深度，防止循环查询

        Returns:
            List[str]: 自动关系列表
        """
        auto_relations = []

        for field_name, field in self._relation_fields.items():
            # 只包含外键和一对一关系，避免多对多的性能问题
            if isinstance(field, (ForeignKeyFieldInstance, OneToOneFieldInstance)):
                auto_relations.append(field_name)

        return auto_relations

    async def serialize_with_relations(self, instance: Model, visited_models: set = None) -> Dict[str, Any]:
        """
        序列化实例及其关联数据（防止循环引用）

        Args:
            instance: 模型实例
            visited_models: 已访问的模型类型集合

        Returns:
            Dict[str, Any]: 序列化后的数据
        """
        if visited_models is None:
            visited_models = set()

        # 防止循环引用
        model_name = type(instance).__name__
        if model_name in visited_models:
            # 如果已经访问过这个模型类型，只返回基本信息
            return {
                'id': getattr(instance, 'id', None),
                '__model__': model_name
            }

        visited_models.add(model_name)

        # 获取基本字段数据
        data = {}
        if hasattr(instance, '__dict__'):
            for key, value in instance.__dict__.items():
                if not key.startswith('_'):
                    data[key] = value

        # 调试日志（仅在调试模式下输出）
        if self.debug_mode:
            logger.info(f"序列化 {model_name}: 基本字段 = {list(data.keys())}")
            logger.info(f"关系字段 = {list(self._relation_fields.keys())}")

        # 获取关联数据
        for field_name, field in self._relation_fields.items():
            try:
                if isinstance(field, ForeignKeyFieldInstance):
                    # 外键关系
                    # 首先尝试获取预加载的关联对象
                    try:
                        related_obj = getattr(instance, field_name)
                        # 检查是否已经是实际的模型实例
                        if related_obj and hasattr(related_obj, '__dict__'):
                            data[field_name] = await self.serialize_with_relations(related_obj, visited_models.copy())
                        elif related_obj:
                            # 如果是ID，尝试查询完整对象
                            related_model = field.related_model
                            if related_model and hasattr(related_obj, 'id'):
                                full_obj = await related_model.get(id=related_obj.id)
                                data[field_name] = await self.serialize_with_relations(full_obj, visited_models.copy())
                    except AttributeError:
                        # 如果没有预加载，尝试查询
                        related_id = getattr(instance, f"{field_name}_id", None)
                        if related_id:
                            related_model = field.related_model
                            if related_model:
                                try:
                                    related_obj = await related_model.get(id=related_id)
                                    data[field_name] = await self.serialize_with_relations(related_obj, visited_models.copy())
                                except:
                                    # 如果查询失败，只保留ID
                                    data[f"{field_name}_id"] = related_id

                elif isinstance(field, OneToOneFieldInstance):
                    # 一对一关系
                    try:
                        related_obj = getattr(instance, field_name)
                        if related_obj and hasattr(related_obj, '__dict__'):
                            data[field_name] = await self.serialize_with_relations(related_obj, visited_models.copy())
                    except AttributeError:
                        pass

                elif isinstance(field, ManyToManyFieldInstance):
                    # 多对多关系（限制数量）
                    try:
                        related_manager = getattr(instance, field_name)
                        if related_manager:
                            # 检查是否已经预加载
                            if hasattr(related_manager, '_fetched_objects'):
                                # 已预加载
                                related_objs = related_manager._fetched_objects[:5]  # 限制数量
                            else:
                                # 未预加载，查询
                                related_objs = await related_manager.limit(5).all()

                            data[field_name] = [
                                await self.serialize_with_relations(obj, visited_models.copy())
                                for obj in related_objs
                            ]
                    except AttributeError:
                        pass

                elif isinstance(field, ReverseRelation):
                    # 反向关系（限制数量）
                    try:
                        related_manager = getattr(instance, field_name)
                        if related_manager:
                            # 检查是否已经预加载
                            if hasattr(related_manager, '_fetched_objects'):
                                # 已预加载
                                related_objs = related_manager._fetched_objects[:3]  # 限制数量
                            else:
                                # 未预加载，查询
                                related_objs = await related_manager.limit(3).all()

                            data[field_name] = [
                                await self.serialize_with_relations(obj, visited_models.copy())
                                for obj in related_objs
                            ]
                    except AttributeError:
                        pass

            except Exception as e:
                logger.warning(f"序列化关系 {field_name} 失败: {e}")
                continue

        visited_models.remove(model_name)
        return data


__all__ = ["RelationHandler"]
