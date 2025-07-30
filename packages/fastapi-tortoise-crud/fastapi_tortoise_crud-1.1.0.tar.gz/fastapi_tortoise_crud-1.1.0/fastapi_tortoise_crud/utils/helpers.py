"""
辅助函数模块

提供各种实用的辅助函数
"""

import hashlib
import json
from typing import Any, Dict, List, Optional, Union, Type
from datetime import datetime
from tortoise.models import Model
from tortoise.fields import CharField, TextField


def generate_cache_key(*args, prefix: str = "", separator: str = ":") -> str:
    """
    生成缓存键
    
    Args:
        *args: 用于生成键的参数
        prefix: 键前缀
        separator: 分隔符
        
    Returns:
        str: 生成的缓存键
    """
    parts = [prefix] if prefix else []
    
    for arg in args:
        if isinstance(arg, dict):
            # 字典转换为排序后的字符串
            sorted_items = sorted(arg.items())
            parts.append(json.dumps(sorted_items, sort_keys=True, ensure_ascii=False))
        elif isinstance(arg, (list, tuple)):
            # 列表/元组转换为字符串
            parts.append(json.dumps(sorted(arg) if isinstance(arg, list) else list(arg), ensure_ascii=False))
        else:
            parts.append(str(arg))
    
    return separator.join(parts)


def generate_hash_key(*args, algorithm: str = "md5") -> str:
    """
    生成哈希键
    
    Args:
        *args: 用于生成哈希的参数
        algorithm: 哈希算法 (md5, sha1, sha256)
        
    Returns:
        str: 生成的哈希键
    """
    content = generate_cache_key(*args)
    
    if algorithm == "md5":
        return hashlib.md5(content.encode()).hexdigest()
    elif algorithm == "sha1":
        return hashlib.sha1(content.encode()).hexdigest()
    elif algorithm == "sha256":
        return hashlib.sha256(content.encode()).hexdigest()
    else:
        raise ValueError(f"Unsupported hash algorithm: {algorithm}")


def format_error_message(
    error: Exception, 
    include_type: bool = True,
    include_traceback: bool = False
) -> str:
    """
    格式化错误消息
    
    Args:
        error: 异常对象
        include_type: 是否包含异常类型
        include_traceback: 是否包含堆栈跟踪
        
    Returns:
        str: 格式化的错误消息
    """
    message = str(error)
    
    if include_type:
        message = f"{type(error).__name__}: {message}"
    
    if include_traceback:
        import traceback
        tb = traceback.format_exc()
        message = f"{message}\n{tb}"
    
    return message


def deep_merge(dict1: Dict, dict2: Dict) -> Dict:
    """
    深度合并字典
    
    Args:
        dict1: 第一个字典
        dict2: 第二个字典
        
    Returns:
        Dict: 合并后的字典
    """
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    
    return result


def flatten_dict(d: Dict, parent_key: str = '', sep: str = '.') -> Dict:
    """
    扁平化字典
    
    Args:
        d: 待扁平化的字典
        parent_key: 父键名
        sep: 分隔符
        
    Returns:
        Dict: 扁平化后的字典
    """
    items = []
    
    for k, v in d.items():
        new_key = f"{parent_key}{sep}{k}" if parent_key else k
        
        if isinstance(v, dict):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))
    
    return dict(items)


# 移除了未使用的辅助函数：
# - unflatten_dict, safe_get, safe_set: 项目中未使用嵌套字典操作
# - filter_dict, convert_keys: 项目中未使用字典转换功能
# - snake_to_camel, camel_to_snake: 项目中未使用命名转换
# - format_datetime, parse_datetime: 项目中未使用日期时间格式化
# - chunk_list: 项目中未使用列表分块功能


def remove_none_values(d: Dict) -> Dict:
    """
    移除字典中的None值
    
    Args:
        d: 字典
        
    Returns:
        Dict: 移除None值后的字典
    """
    return {k: v for k, v in d.items() if v is not None}


def ensure_list(value: Union[Any, List[Any]]) -> List[Any]:
    """
    确保值是列表

    Args:
        value: 任意值

    Returns:
        List[Any]: 列表
    """
    if isinstance(value, list):
        return value
    elif value is None:
        return []
    else:
        return [value]


def process_time_range_filters(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    处理时间范围过滤器

    Args:
        filters: 原始过滤条件

    Returns:
        Dict[str, Any]: 处理后的过滤条件
    """
    processed_filters = filters.copy()

    for time_field in ['create_time', 'update_time']:
        if time_field in processed_filters:
            time_value = processed_filters[time_field]

            if isinstance(time_value, str):
                # 单个时间字符串，转换为[开始时间, 当前时间]
                try:
                    start_time = datetime.fromisoformat(time_value.replace('Z', '+00:00'))
                    end_time = datetime.now()
                    processed_filters[f"{time_field}__gte"] = start_time
                    processed_filters[f"{time_field}__lte"] = end_time
                    del processed_filters[time_field]
                except ValueError:
                    # 如果解析失败，保持原值
                    pass

            elif isinstance(time_value, list) and len(time_value) == 2:
                # 时间范围列表
                try:
                    start_time = time_value[0]
                    end_time = time_value[1]

                    if isinstance(start_time, str):
                        start_time = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
                    if isinstance(end_time, str):
                        end_time = datetime.fromisoformat(end_time.replace('Z', '+00:00'))

                    processed_filters[f"{time_field}__gte"] = start_time
                    processed_filters[f"{time_field}__lte"] = end_time
                    del processed_filters[time_field]
                except (ValueError, TypeError):
                    # 如果解析失败，保持原值
                    pass

    return processed_filters


def validate_pagination_params(page: int, size: int, max_size: int = 100) -> tuple:
    """
    验证分页参数

    Args:
        page: 页码
        size: 页大小
        max_size: 最大页大小

    Returns:
        tuple: (验证后的页码, 验证后的页大小)
    """
    page = max(1, page)
    size = min(max(1, size), max_size)
    return page, size


def is_text_field(model: Type[Model], field_name: str) -> bool:
    """
    检查字段是否为文本类型字段

    Args:
        model: Tortoise模型类
        field_name: 字段名

    Returns:
        bool: 是否为文本字段
    """
    if not hasattr(model, '_meta') or not hasattr(model._meta, 'fields_map'):
        return False

    field = model._meta.fields_map.get(field_name)
    if field is None:
        return False

    return isinstance(field, (CharField, TextField))


def process_text_filters(model: Type[Model], filters: Dict[str, Any], use_contains: bool = True) -> Dict[str, Any]:
    """
    处理文本字段过滤条件，将文本字段转换为包含查询

    Args:
        model: Tortoise模型类
        filters: 原始过滤条件
        use_contains: 是否对文本字段使用包含查询

    Returns:
        Dict[str, Any]: 处理后的过滤条件
    """
    if not use_contains or not filters:
        return filters

    processed_filters = {}

    for field_name, value in filters.items():
        # 跳过已经包含操作符的字段（如 field__gte, field__lte 等）
        if '__' in field_name:
            processed_filters[field_name] = value
            continue

        # 检查是否为文本字段
        if is_text_field(model, field_name) and isinstance(value, str) and value.strip():
            # 对文本字段使用不区分大小写的包含查询
            processed_filters[f"{field_name}__icontains"] = value
        else:
            # 非文本字段保持原样
            processed_filters[field_name] = value

    return processed_filters


__all__ = [
    "generate_cache_key",
    "generate_hash_key",
    "format_error_message",
    "deep_merge",
    "flatten_dict",
    "remove_none_values",
    "ensure_list",
    "process_time_range_filters",
    "validate_pagination_params",
    "is_text_field",
    "process_text_filters"
]
