"""
关系工具函数

提供关系处理的辅助功能
"""

import logging
from typing import Any, Dict, List, Optional, Type, Union, Set
from tortoise.models import Model
from tortoise.fields.relational import RelationalField, ForeignKeyFieldInstance, ManyToManyFieldInstance

logger = logging.getLogger(__name__)


class RelationUtils:
    """关系工具类"""
    
    @staticmethod
    def get_model_relations(model: Type[Model]) -> Dict[str, RelationalField]:
        """
        获取模型的所有关系字段
        
        Args:
            model: 模型类
            
        Returns:
            Dict[str, RelationalField]: 关系字段映射
        """
        relations = {}
        
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                if isinstance(field, RelationalField):
                    relations[field_name] = field
        
        return relations
    
    @staticmethod
    def get_foreign_key_fields(model: Type[Model]) -> Dict[str, ForeignKeyFieldInstance]:
        """
        获取模型的外键字段
        
        Args:
            model: 模型类
            
        Returns:
            Dict[str, ForeignKeyFieldInstance]: 外键字段映射
        """
        fk_fields = {}
        
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                if isinstance(field, ForeignKeyFieldInstance):
                    fk_fields[field_name] = field
        
        return fk_fields
    
    @staticmethod
    def get_many_to_many_fields(model: Type[Model]) -> Dict[str, ManyToManyFieldInstance]:
        """
        获取模型的多对多字段
        
        Args:
            model: 模型类
            
        Returns:
            Dict[str, ManyToManyFieldInstance]: 多对多字段映射
        """
        m2m_fields = {}
        
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                if isinstance(field, ManyToManyFieldInstance):
                    m2m_fields[field_name] = field
        
        return m2m_fields
    
    @staticmethod
    def get_reverse_relations(model: Type[Model]) -> Dict[str, Any]:
        """
        获取模型的反向关系
        
        Args:
            model: 模型类
            
        Returns:
            Dict[str, Any]: 反向关系映射
        """
        reverse_relations = {}
        
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                if hasattr(field, 'related_name') and field.related_name:
                    reverse_relations[field.related_name] = field
        
        return reverse_relations
    
    @staticmethod
    def validate_relation_data(model: Type[Model], data: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        验证关系数据
        
        Args:
            model: 模型类
            data: 数据字典
            
        Returns:
            Dict[str, List[str]]: 验证错误
        """
        errors = {}
        relations = RelationUtils.get_model_relations(model)
        
        for field_name, value in data.items():
            if field_name in relations:
                field = relations[field_name]
                field_errors = RelationUtils._validate_relation_field(field, value)
                if field_errors:
                    errors[field_name] = field_errors
        
        return errors
    
    @staticmethod
    def _validate_relation_field(field: RelationalField, value: Any) -> List[str]:
        """验证单个关系字段"""
        errors = []
        
        if isinstance(field, ForeignKeyFieldInstance):
            # 验证外键
            if value is not None:
                if isinstance(value, dict):
                    if not value:
                        errors.append("外键对象不能为空字典")
                elif isinstance(value, (int, str)):
                    if not value:
                        errors.append("外键ID不能为空")
                elif not isinstance(value, Model):
                    errors.append("外键值必须是ID、字典或模型实例")
        
        elif isinstance(field, ManyToManyFieldInstance):
            # 验证多对多
            if value is not None:
                if not isinstance(value, (list, tuple)):
                    errors.append("多对多关系值必须是列表或元组")
                else:
                    for i, item in enumerate(value):
                        if isinstance(item, dict):
                            if not item:
                                errors.append(f"索引{i}的对象不能为空字典")
                        elif isinstance(item, (int, str)):
                            if not item:
                                errors.append(f"索引{i}的ID不能为空")
                        elif not isinstance(item, Model):
                            errors.append(f"索引{i}的值必须是ID、字典或模型实例")
        
        return errors
    
    @staticmethod
    def extract_relation_data(data: Dict[str, Any]) -> tuple[Dict[str, Any], Dict[str, Any]]:
        """
        从数据中提取关系数据
        
        Args:
            data: 原始数据
            
        Returns:
            tuple: (普通字段数据, 关系数据)
        """
        normal_data = {}
        relation_data = {}
        
        for key, value in data.items():
            if key.startswith('_m2m_') or key.startswith('_reverse_'):
                # 多对多或反向关系数据
                relation_data[key] = value
            elif isinstance(value, (dict, list)) and not key.endswith('_id'):
                # 可能是关系对象
                relation_data[key] = value
            else:
                # 普通字段
                normal_data[key] = value
        
        return normal_data, relation_data
    
    @staticmethod
    def build_prefetch_related(relations: List[str], model: Type[Model]) -> List[str]:
        """
        构建预取关系列表
        
        Args:
            relations: 关系字段名列表
            model: 模型类
            
        Returns:
            List[str]: 有效的预取关系列表
        """
        valid_relations = []
        model_relations = RelationUtils.get_model_relations(model)
        
        for relation in relations:
            # 支持嵌套关系，如 'user__profile'
            base_relation = relation.split('__')[0]
            
            if base_relation in model_relations:
                valid_relations.append(relation)
            else:
                logger.warning(f"模型 {model.__name__} 中不存在关系字段: {base_relation}")
        
        return valid_relations
    
    @staticmethod
    def get_relation_depth(relations: List[str]) -> int:
        """
        获取关系的最大深度
        
        Args:
            relations: 关系字段名列表
            
        Returns:
            int: 最大深度
        """
        max_depth = 0
        
        for relation in relations:
            depth = len(relation.split('__'))
            max_depth = max(max_depth, depth)
        
        return max_depth
    
    @staticmethod
    def optimize_relations(relations: List[str]) -> List[str]:
        """
        优化关系列表，移除冗余的关系
        
        Args:
            relations: 关系字段名列表
            
        Returns:
            List[str]: 优化后的关系列表
        """
        # 按长度排序，短的在前
        sorted_relations = sorted(relations, key=len)
        optimized = []
        
        for relation in sorted_relations:
            # 检查是否已经被更短的关系包含
            is_redundant = False
            for existing in optimized:
                if relation.startswith(existing + '__'):
                    is_redundant = True
                    break
            
            if not is_redundant:
                optimized.append(relation)
        
        return optimized
    
    @staticmethod
    def get_circular_relations(model: Type[Model], visited: Set[Type[Model]] = None) -> List[str]:
        """
        检测循环关系
        
        Args:
            model: 模型类
            visited: 已访问的模型集合
            
        Returns:
            List[str]: 循环关系路径
        """
        if visited is None:
            visited = set()
        
        if model in visited:
            return [model.__name__]
        
        visited.add(model)
        circular_paths = []
        
        relations = RelationUtils.get_model_relations(model)
        for field_name, field in relations.items():
            if hasattr(field, 'related_model'):
                related_model = field.related_model
                sub_paths = RelationUtils.get_circular_relations(related_model, visited.copy())
                
                for path in sub_paths:
                    if model.__name__ in path:
                        circular_paths.append(f"{model.__name__}.{field_name} -> {path}")
        
        return circular_paths
    
    @staticmethod
    def format_relation_data_for_response(instance: Model, relations: List[str]) -> Dict[str, Any]:
        """
        格式化关系数据用于响应
        
        Args:
            instance: 模型实例
            relations: 要包含的关系列表
            
        Returns:
            Dict[str, Any]: 格式化的数据
        """
        data = {}
        
        for relation in relations:
            try:
                # 支持嵌套关系
                parts = relation.split('__')
                current_obj = instance
                current_data = data
                
                for i, part in enumerate(parts):
                    if hasattr(current_obj, part):
                        related_obj = getattr(current_obj, part)
                        
                        if i == len(parts) - 1:
                            # 最后一级，设置数据
                            if hasattr(related_obj, 'all'):
                                # 多对多或反向关系
                                current_data[part] = [
                                    RelationUtils._serialize_model(obj) 
                                    for obj in related_obj
                                ]
                            else:
                                # 外键关系
                                current_data[part] = RelationUtils._serialize_model(related_obj)
                        else:
                            # 中间级，继续嵌套
                            if part not in current_data:
                                current_data[part] = {}
                            current_data = current_data[part]
                            current_obj = related_obj
                    else:
                        logger.warning(f"对象 {type(current_obj).__name__} 没有属性: {part}")
                        break
                        
            except Exception as e:
                logger.error(f"格式化关系数据失败 {relation}: {e}")
        
        return data
    
    @staticmethod
    def _serialize_model(obj: Any) -> Any:
        """序列化模型对象"""
        if obj is None:
            return None
        
        if isinstance(obj, Model):
            # 基础序列化，只包含基本字段
            data = {}
            for field_name, field in obj._meta.fields_map.items():
                if not isinstance(field, RelationalField):
                    value = getattr(obj, field_name, None)
                    if value is not None:
                        data[field_name] = value
            return data
        
        return obj


__all__ = ["RelationUtils"]
