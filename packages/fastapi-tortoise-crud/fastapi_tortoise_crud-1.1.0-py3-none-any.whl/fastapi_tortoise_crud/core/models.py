"""
基础模型类
"""

from tortoise.models import Model
from tortoise import fields
from typing import Optional, List, Dict, Any



class TimestampMixin:
    """时间戳混入类"""

    create_time = fields.DatetimeField(auto_now_add=True, description="创建时间")
    update_time = fields.DatetimeField(auto_now=True, description="更新时间")


class SoftDeleteMixin:
    """软删除混入类"""

    is_deleted = fields.BooleanField(default=False, description="是否已删除")
    delete_time = fields.DatetimeField(null=True, description="删除时间")
    
    @classmethod
    def active_objects(cls):
        """获取未删除的对象"""
        return cls.filter(is_deleted=False)
    
    async def soft_delete(self):
        """软删除"""
        from datetime import datetime
        self.is_deleted = True
        self.delete_time = datetime.now()
        await self.save()
    
    async def restore(self):
        """恢复删除"""
        self.is_deleted = False
        self.delete_time = None
        await self.save()


class UserTrackingMixin:
    """用户追踪混入类"""
    
    created_by = fields.IntField(null=True, description="创建者ID")
    updated_by = fields.IntField(null=True, description="更新者ID")


class VersionMixin:
    """版本控制混入类"""
    
    version = fields.IntField(default=1, description="版本号")
    
    async def save(self, *args, **kwargs):
        """保存时自动增加版本号"""
        if self.pk:  # 更新时增加版本号
            self.version += 1
        await super().save(*args, **kwargs)


class StatusMixin:
    """状态混入类"""
    
    class StatusChoices:
        ACTIVE = "active"
        INACTIVE = "inactive"
        PENDING = "pending"
        ARCHIVED = "archived"
    
    status = fields.CharField(
        max_length=20, 
        default=StatusChoices.ACTIVE,
        description="状态"
    )
    
    @classmethod
    def active_objects(cls):
        """获取活跃对象"""
        return cls.filter(status=cls.StatusChoices.ACTIVE)
    
    def is_active(self) -> bool:
        """是否活跃"""
        return self.status == self.StatusChoices.ACTIVE
    
    async def activate(self):
        """激活"""
        self.status = self.StatusChoices.ACTIVE
        await self.save()
    
    async def deactivate(self):
        """停用"""
        self.status = self.StatusChoices.INACTIVE
        await self.save()


class BaseModel(Model, TimestampMixin):
    """
    基础模型类

    提供常用字段和方法
    """

    id = fields.IntField(pk=True, description="主键ID")

    class Meta:
        abstract = True

    @classmethod
    async def create_one(cls, data: Dict[str, Any]) -> "BaseModel":
        """创建单条记录"""
        return await cls.create(**data)

    @classmethod
    async def find_one(cls, **filters) -> Optional["BaseModel"]:
        """查找单条记录"""
        return await cls.filter(**filters).first()

    @classmethod
    async def find_by_id(cls, id: int) -> Optional["BaseModel"]:
        """根据ID查找记录"""
        return await cls.filter(id=id).first()

    @classmethod
    async def update_one(cls, id: int, data: Dict[str, Any]) -> Optional["BaseModel"]:
        """更新单条记录"""
        await cls.filter(id=id).update(**data)
        return await cls.find_by_id(id)

    @classmethod
    async def delete_one(cls, id: int) -> bool:
        """删除单条记录"""
        deleted_count = await cls.filter(id=id).delete()
        return deleted_count > 0

    @classmethod
    async def delete_many(cls, ids: List[int]) -> int:
        """批量删除记录"""
        return await cls.filter(id__in=ids).delete()

    @classmethod
    async def exists(cls, **filters) -> bool:
        """检查记录是否存在"""
        return await cls.filter(**filters).exists()

    @classmethod
    async def count_all(cls, **filters) -> int:
        """统计记录数量"""
        return await cls.filter(**filters).count()

    def to_dict(self, exclude: List[str] = None, include: List[str] = None) -> Dict[str, Any]:
        """转换为字典"""
        exclude = exclude or []
        data = {}

        for field_name in self._meta.fields:
            if include and field_name not in include:
                continue
            if field_name in exclude:
                continue

            value = getattr(self, field_name, None)
            if value is not None:
                data[field_name] = value

        return data

    def __str__(self) -> str:
        return f"<{self.__class__.__name__}: {self.id}>"

    def __repr__(self) -> str:
        return self.__str__()


__all__ = [
    "BaseModel",
    "TimestampMixin",
    "SoftDeleteMixin", 
    "UserTrackingMixin",
    "VersionMixin",
    "StatusMixin"
]
