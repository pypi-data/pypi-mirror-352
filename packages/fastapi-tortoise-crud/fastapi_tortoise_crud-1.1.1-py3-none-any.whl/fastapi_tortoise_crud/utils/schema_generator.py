"""
自动Schema生成器

提供自动生成Pydantic Schema的功能
"""

from typing import Any, Dict, List, Optional, Type, Union, get_type_hints
from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field, create_model
from tortoise.models import Model
from tortoise.fields import (
    CharField, TextField, IntField, BigIntField, SmallIntField,
    FloatField, DecimalField, BooleanField, DatetimeField, DateField,
    TimeField, JSONField, UUIDField
)
from tortoise.fields.relational import (
    ForeignKeyFieldInstance, ManyToManyFieldInstance,
    OneToOneFieldInstance, ReverseRelation
)


class SchemaGenerator:
    """Schema自动生成器"""
    
    @staticmethod
    def generate_filter_schema(
        model: Type[Model], 
        name: str = None,
        include_fields: List[str] = None,
        exclude_fields: List[str] = None,
        include_time_range: bool = True
    ) -> Type[BaseModel]:
        """
        生成过滤Schema
        
        Args:
            model: Tortoise模型
            name: Schema名称
            include_fields: 包含的字段
            exclude_fields: 排除的字段
            include_time_range: 是否包含时间范围字段
            
        Returns:
            Type[BaseModel]: 生成的Schema类
        """
        if name is None:
            name = f"{model.__name__}Filter"
        
        fields = {}
        
        # 获取模型字段
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                # 跳过关系字段
                if isinstance(field, (ForeignKeyFieldInstance, ManyToManyFieldInstance, 
                                    OneToOneFieldInstance, ReverseRelation)):
                    continue
                
                # 应用包含/排除规则
                if include_fields and field_name not in include_fields:
                    continue
                if exclude_fields and field_name in exclude_fields:
                    continue
                
                # 生成字段类型
                field_type = SchemaGenerator._get_filter_field_type(field)
                if field_type:
                    fields[field_name] = (Optional[field_type], Field(None, description=getattr(field, 'description', '')))
        
        # 添加时间范围字段
        if include_time_range:
            fields['create_time'] = (Optional[Union[str, List[Union[str, datetime]]]], 
                                   Field(None, description="创建时间范围"))
            fields['update_time'] = (Optional[Union[str, List[Union[str, datetime]]]], 
                                   Field(None, description="更新时间范围"))
        
        # 创建Schema类
        schema_class = create_model(name, **fields)
        
        # 添加示例
        schema_class.Config = type('Config', (), {
            'json_schema_extra': {
                'example': SchemaGenerator._generate_filter_example(model, fields)
            }
        })
        
        return schema_class
    
    @staticmethod
    def generate_create_schema(
        model: Type[Model],
        name: str = None,
        include_fields: List[str] = None,
        exclude_fields: List[str] = None,
        exclude_auto_fields: bool = True
    ) -> Type[BaseModel]:
        """
        生成创建Schema
        
        Args:
            model: Tortoise模型
            name: Schema名称
            include_fields: 包含的字段
            exclude_fields: 排除的字段
            exclude_auto_fields: 是否排除自动字段
            
        Returns:
            Type[BaseModel]: 生成的Schema类
        """
        if name is None:
            name = f"{model.__name__}Create"
        
        fields = {}
        auto_fields = {'id', 'create_time', 'update_time', 'delete_time'}
        
        # 获取模型字段
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                # 跳过自动字段
                if exclude_auto_fields and field_name in auto_fields:
                    continue
                
                # 跳过关系字段（外键除外）
                if isinstance(field, (ManyToManyFieldInstance, OneToOneFieldInstance, ReverseRelation)):
                    continue
                
                # 应用包含/排除规则
                if include_fields and field_name not in include_fields:
                    continue
                if exclude_fields and field_name in exclude_fields:
                    continue
                
                # 生成字段类型
                field_type, is_required = SchemaGenerator._get_create_field_type(field)
                if field_type:
                    if is_required:
                        fields[field_name] = (field_type, Field(..., description=getattr(field, 'description', '')))
                    else:
                        fields[field_name] = (Optional[field_type], Field(None, description=getattr(field, 'description', '')))
        
        # 创建Schema类
        schema_class = create_model(name, **fields)
        
        # 添加示例
        schema_class.Config = type('Config', (), {
            'json_schema_extra': {
                'example': SchemaGenerator._generate_create_example(model, fields)
            }
        })
        
        return schema_class
    
    @staticmethod
    def generate_update_schema(
        model: Type[Model],
        name: str = None,
        include_fields: List[str] = None,
        exclude_fields: List[str] = None
    ) -> Type[BaseModel]:
        """
        生成更新Schema
        
        Args:
            model: Tortoise模型
            name: Schema名称
            include_fields: 包含的字段
            exclude_fields: 排除的字段
            
        Returns:
            Type[BaseModel]: 生成的Schema类
        """
        if name is None:
            name = f"{model.__name__}Update"
        
        fields = {}
        auto_fields = {'id', 'create_time', 'update_time', 'delete_time'}
        
        # 获取模型字段
        if hasattr(model, '_meta'):
            for field_name, field in model._meta.fields_map.items():
                # 跳过自动字段
                if field_name in auto_fields:
                    continue
                
                # 跳过关系字段（外键除外）
                if isinstance(field, (ManyToManyFieldInstance, OneToOneFieldInstance, ReverseRelation)):
                    continue
                
                # 应用包含/排除规则
                if include_fields and field_name not in include_fields:
                    continue
                if exclude_fields and field_name in exclude_fields:
                    continue
                
                # 生成字段类型（更新时所有字段都是可选的）
                field_type, _ = SchemaGenerator._get_create_field_type(field)
                if field_type:
                    fields[field_name] = (Optional[field_type], Field(None, description=getattr(field, 'description', '')))
        
        # 创建Schema类
        schema_class = create_model(name, **fields)
        
        # 添加示例
        schema_class.Config = type('Config', (), {
            'json_schema_extra': {
                'example': SchemaGenerator._generate_update_example(model, fields)
            }
        })
        
        return schema_class
    
    @staticmethod
    def _get_filter_field_type(field) -> Optional[Type]:
        """获取过滤字段类型"""
        if isinstance(field, (CharField, TextField)):
            return str
        elif isinstance(field, (IntField, BigIntField, SmallIntField)):
            return int
        elif isinstance(field, FloatField):
            return float
        elif isinstance(field, DecimalField):
            return Decimal
        elif isinstance(field, BooleanField):
            return bool
        elif isinstance(field, (DatetimeField, DateField, TimeField)):
            return Union[str, datetime]
        elif isinstance(field, UUIDField):
            return str
        elif isinstance(field, JSONField):
            return dict
        elif isinstance(field, ForeignKeyFieldInstance):
            return int  # 外键ID
        return None
    
    @staticmethod
    def _get_create_field_type(field) -> tuple[Optional[Type], bool]:
        """获取创建字段类型和是否必需"""
        field_type = None
        is_required = not getattr(field, 'null', True) and not hasattr(field, 'default')
        
        if isinstance(field, (CharField, TextField)):
            field_type = str
        elif isinstance(field, (IntField, BigIntField, SmallIntField)):
            field_type = int
        elif isinstance(field, FloatField):
            field_type = float
        elif isinstance(field, DecimalField):
            field_type = Decimal
        elif isinstance(field, BooleanField):
            field_type = bool
        elif isinstance(field, (DatetimeField, DateField, TimeField)):
            field_type = datetime
        elif isinstance(field, UUIDField):
            field_type = str
        elif isinstance(field, JSONField):
            field_type = dict
        elif isinstance(field, ForeignKeyFieldInstance):
            field_type = int  # 外键ID
            
        return field_type, is_required
    
    @staticmethod
    def _generate_filter_example(model: Type[Model], fields: Dict) -> Dict:
        """生成过滤示例"""
        example = {}
        
        for field_name, (field_type, field_info) in fields.items():
            if field_name == 'create_time':
                example[field_name] = ["2024-01-01T00:00:00", "2024-12-31T23:59:59"]
            elif field_name == 'update_time':
                example[field_name] = "2024-01-01T00:00:00"
            elif 'str' in str(field_type):
                example[field_name] = "搜索关键词"
            elif 'int' in str(field_type):
                example[field_name] = 1
            elif 'bool' in str(field_type):
                example[field_name] = True
        
        return example
    
    @staticmethod
    def _generate_create_example(model: Type[Model], fields: Dict) -> Dict:
        """生成创建示例"""
        example = {}
        
        for field_name, (field_type, field_info) in fields.items():
            if 'str' in str(field_type):
                if 'name' in field_name.lower():
                    example[field_name] = "示例名称"
                elif 'email' in field_name.lower():
                    example[field_name] = "user@example.com"
                elif 'password' in field_name.lower():
                    example[field_name] = "password123"
                else:
                    example[field_name] = "示例文本"
            elif 'int' in str(field_type):
                if field_name.endswith('_id'):
                    example[field_name] = 1
                else:
                    example[field_name] = 100
            elif 'bool' in str(field_type):
                example[field_name] = True
            elif 'Decimal' in str(field_type):
                example[field_name] = "99.99"
        
        return example
    
    @staticmethod
    def _generate_update_example(model: Type[Model], fields: Dict) -> Dict:
        """生成更新示例"""
        example = SchemaGenerator._generate_create_example(model, fields)
        # 更新示例中只包含部分字段
        if len(example) > 3:
            keys = list(example.keys())[:3]
            example = {k: example[k] for k in keys}
        return example


__all__ = ["SchemaGenerator"]
