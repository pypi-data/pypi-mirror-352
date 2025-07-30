# FastAPI Tortoise CRUD

🚀 一个功能强大、易于使用的 FastAPI + Tortoise ORM CRUD 库，为快速 API 开发提供高级功能。

[![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-green.svg)](https://fastapi.tiangolo.com/)
[![Tortoise ORM](https://img.shields.io/badge/Tortoise%20ORM-0.20+-orange.svg)](https://tortoise.github.io/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## ✨ 核心特性

### 🔥 核心功能
- **🚀 快速 CRUD 操作**：为 Tortoise ORM 模型自动生成完整的 CRUD 端点
- **🔗 自动关联查询**：智能加载相关模型数据，支持深层关联
- **📊 时间范围过滤**：内置 create_time/update_time 范围过滤支持
- **📋 统一响应格式**：一致的 `{code, message, data}` 响应结构
- **📚 自动 Schema 生成**：自动生成带验证和示例的 API Schema
- **🔍 智能搜索**：文本字段支持包含匹配，数值字段支持范围查询

### 🎯 高级功能
- **🎣 Hook 系统**：灵活的生命周期钩子，支持依赖注入
- **💾 智能缓存**：内存/Redis 缓存，支持自动失效和统计
- **🛡️ 细粒度权限**：不同端点使用不同的依赖注入
- **📈 性能监控**：内置性能指标和数据库查询监控
- **🔧 高度可配置**：丰富的配置选项，满足各种需求
- **🛠️ 类型安全**：完整的类型提示和 Pydantic 集成

## 🚀 快速开始

### 📦 安装

```bash
# 基础安装
pip install fastapi-tortoise-crud

# 包含 Redis 缓存支持
pip install fastapi-tortoise-crud[redis]
```

### ⚡ 5分钟上手

```python
from fastapi import FastAPI
from tortoise import fields
from tortoise.contrib.fastapi import register_tortoise
from fastapi_tortoise_crud import FastCRUD, BaseModel

# 定义模型
class User(BaseModel):
    name = fields.CharField(max_length=50, description="姓名")
    email = fields.CharField(max_length=100, unique=True, description="邮箱")
    age = fields.IntField(null=True, description="年龄")

    class Meta:
        table = "users"

# 创建应用
app = FastAPI()

# 创建 CRUD - 一行代码搞定！
user_crud = FastCRUD(model=User)
app.include_router(user_crud.router)

# 配置数据库
register_tortoise(
    app,
    db_url="sqlite://./db.sqlite3",
    modules={"models": [__name__]},
    generate_schemas=True,
    add_exception_handlers=True,
)
```

🎉 **就这么简单！** 你已经拥有了完整的用户管理 API：

- `GET /users/` - 获取用户列表（支持分页、过滤、排序）
- `POST /users/` - 创建新用户
- `GET /users/{id}` - 获取单个用户
- `PUT /users/{id}` - 更新用户
- `DELETE /users/{id}` - 删除用户

### 🎯 运行示例

```bash
# 克隆项目
git clone https://github.com/your-repo/fastapi-tortoise-crud.git
cd fastapi-tortoise-crud

# 安装依赖
pip install -e .

# 运行快速开始示例
python examples/quick_start.py
```

访问 http://127.0.0.1:8001/docs 查看自动生成的 API 文档！

## 📖 详细文档

### 🏗️ 基础用法

#### 创建 CRUD 实例

```python
from fastapi_tortoise_crud import FastCRUD, CacheConfig, HookConfig

# 基础用法
crud = FastCRUD(model=YourModel)

# 高级配置
crud = FastCRUD(
    model=YourModel,
    prefix="/api/users",           # 自定义路由前缀
    tags=["用户管理"],              # API 文档标签
    cache=True,                    # 启用缓存
    relations=["profile", "orders"], # 自动加载关联数据
    text_contains_search=True,     # 启用文本包含搜索
)
```

#### 自定义 Schema

```python
from pydantic import BaseModel, Field

class UserCreateSchema(BaseModel):
    name: str = Field(..., description="姓名", max_length=50)
    email: str = Field(..., description="邮箱")
    age: int = Field(None, description="年龄", ge=0, le=150)

crud = FastCRUD(
    model=User,
    create_schema=UserCreateSchema,  # 自定义创建 Schema
    # update_schema=UserUpdateSchema,  # 自定义更新 Schema
)
```

### 🎣 Hook 系统

Hook 系统让你可以在 CRUD 操作的各个阶段插入自定义逻辑：

```python
from fastapi_tortoise_crud import HookStage, HookContext

# 创建支持 Hook 的 CRUD
crud = FastCRUD(
    model=User,
    hooks=True  # 启用 Hook 系统
)

# 使用装饰器注册 Hook
@crud.hook(HookStage.PRE_CREATE)
async def validate_user(data: dict, context: HookContext) -> dict:
    """创建用户前验证数据"""
    if len(data.get("name", "")) < 2:
        raise ValueError("姓名至少需要2个字符")
    return data

@crud.hook(HookStage.POST_CREATE)
async def welcome_user(data: dict, result: dict, context: HookContext):
    """创建用户后发送欢迎邮件"""
    print(f"欢迎新用户: {result['name']}")

# Hook 支持依赖注入！
@crud.hook(HookStage.PRE_UPDATE)
async def check_permission(
    data: dict,
    context: HookContext,
    current_user: dict = Depends(get_current_user)  # 依赖注入
) -> dict:
    """更新前检查权限"""
    if not current_user.get("is_admin"):
        raise HTTPException(403, "需要管理员权限")
    return data
```

#### Hook 阶段

- `PRE_CREATE` - 创建前
- `POST_CREATE` - 创建后
- `PRE_READ` - 读取前
- `POST_READ` - 读取后
- `PRE_UPDATE` - 更新前
- `POST_UPDATE` - 更新后
- `PRE_DELETE` - 删除前
- `POST_DELETE` - 删除后
- `PRE_LIST` - 列表查询前
- `POST_LIST` - 列表查询后

### 💾 缓存系统

智能缓存系统支持内存和 Redis 两种后端：

```python
from fastapi_tortoise_crud import CacheConfig

# 内存缓存
crud = FastCRUD(
    model=User,
    cache=CacheConfig(
        backend="memory",
        default_ttl=3600,      # 1小时过期
        max_memory_items=1000  # 最大缓存项数
    )
)

# Redis 缓存
crud = FastCRUD(
    model=User,
    cache=CacheConfig(
        backend="redis",
        redis_url="redis://localhost:6379/0",
        default_ttl=7200,      # 2小时过期
        key_prefix="myapp:"    # 缓存键前缀
    )
)

# 全局缓存配置
from fastapi_tortoise_crud import init_global_cache, get_global_cache_stats

init_global_cache(CacheConfig(backend="memory"))

# 获取缓存统计
stats = get_global_cache_stats()
print(f"缓存命中率: {stats['hit_rate']:.2%}")
```

### 🛡️ 依赖注入与权限控制

细粒度的依赖注入让你可以为不同的端点设置不同的权限：

```python
from fastapi import Depends, HTTPException
from fastapi_tortoise_crud import DependencyConfig, EndpointType

async def get_current_user(request: Request):
    # 从请求中获取用户信息
    token = request.headers.get("Authorization")
    if not token:
        raise HTTPException(401, "需要认证")
    return {"id": 1, "username": "admin"}

async def require_admin(current_user: dict = Depends(get_current_user)):
    if not current_user.get("is_admin"):
        raise HTTPException(403, "需要管理员权限")
    return current_user

# 配置依赖注入
crud = FastCRUD(
    model=User,
    dependencies=DependencyConfig(
        # 全局依赖 - 所有端点都会执行
        global_dependencies=[Depends(get_current_user)],

        # 端点特定依赖
        endpoint_dependencies={
            EndpointType.CREATE: [Depends(require_admin)],  # 只有管理员能创建
            EndpointType.UPDATE: [Depends(require_admin)],  # 只有管理员能更新
            EndpointType.DELETE: [Depends(require_admin)],  # 只有管理员能删除
            # LIST 和 READ 所有认证用户都可以访问
        }
    )
)
```

### 🔗 关联模型处理

自动处理复杂的模型关系：

```python
# 定义关联模型
class User(BaseModel):
    name = fields.CharField(max_length=50)
    profile = fields.OneToOneField("models.Profile", related_name="user")
    orders = fields.ReverseRelation["Order"]

class Profile(BaseModel):
    bio = fields.TextField()
    avatar = fields.CharField(max_length=200)

class Order(BaseModel):
    user = fields.ForeignKeyField("models.User", related_name="orders")
    total = fields.DecimalField(max_digits=10, decimal_places=2)
    items = fields.ReverseRelation["OrderItem"]

# 配置关联查询
user_crud = FastCRUD(
    model=User,
    relations=["profile", "orders", "orders__items"]  # 支持深层关联
)

# 查询用户时自动加载 profile 和 orders 数据
# GET /users/1 会返回：
# {
#   "id": 1,
#   "name": "张三",
#   "profile": {"bio": "...", "avatar": "..."},
#   "orders": [
#     {"id": 1, "total": 100.00, "items": [...]}
#   ]
# }
```

### 📊 高级查询功能

#### 时间范围过滤

```python
# 自动支持时间范围查询
# GET /users/?create_time=2024-01-01,2024-12-31
# GET /users/?update_time=2024-01-01  # 自动扩展到当前时间

# 在代码中使用
from datetime import datetime
filters = {
    "create_time": ["2024-01-01T00:00:00", "2024-12-31T23:59:59"],
    "update_time": "2024-01-01T00:00:00"  # 单个时间自动扩展
}
```

#### 智能搜索

```python
# 文本字段支持包含搜索
crud = FastCRUD(
    model=Product,
    text_contains_search=True  # 启用文本包含搜索
)

# GET /products/?name=手机  # 查找名称包含"手机"的商品
# GET /products/?description=苹果  # 查找描述包含"苹果"的商品

# 数值范围查询
# GET /products/?price=100,500  # 价格在100-500之间
# GET /products/?stock=10  # 库存大于等于10
```

#### 排序和分页

```python
# 自动支持排序和分页
# GET /users/?page=1&size=20&order_by=-create_time,name

# 在代码中使用
from fastapi_tortoise_crud import PaginationParams

params = PaginationParams(page=1, size=20)
result = await crud.crud_routes.list_items(
    filters={},
    order_by=["-create_time", "name"],  # 按创建时间倒序，姓名正序
    params=params
)
```

### 📈 性能监控

内置性能监控帮助你了解应用性能：

```python
from fastapi_tortoise_crud import MonitoringConfig

crud = FastCRUD(
    model=User,
    monitoring=MonitoringConfig(
        enable_metrics=True,           # 启用指标收集
        enable_performance_tracking=True,  # 启用性能跟踪
        enable_error_tracking=True,    # 启用错误跟踪
        track_memory_usage=True,       # 跟踪内存使用
        track_cpu_usage=True,          # 跟踪CPU使用
    )
)

# 获取监控数据
@app.get("/metrics")
async def get_metrics():
    return crud.monitoring_manager.get_metrics()
```

## 🎯 完整示例

我们提供了多个完整的示例来帮助你快速上手：

### 📁 示例文件

- **`examples/quick_start.py`** - 5分钟快速开始
- **`examples/advanced_features.py`** - 高级功能演示
- **`examples/complete_example.py`** - 完整功能示例

### 🚀 运行示例

```bash
# 快速开始示例
python examples/quick_start.py
# 访问 http://127.0.0.1:8001/docs

# 高级功能示例
python examples/advanced_features.py
# 访问 http://127.0.0.1:8002/docs

# 完整功能示例
python examples/complete_example.py
# 访问 http://127.0.0.1:8000/docs
```

### 🎮 交互式体验

1. **创建演示数据**：访问 `/demo/create-sample-data` 端点
2. **查看 API 文档**：访问 `/docs` 查看自动生成的文档
3. **测试 API**：使用 Swagger UI 直接测试各个端点
4. **查看缓存统计**：访问 `/cache/stats` 了解缓存性能

## 🔧 配置参考

### FastCRUD 参数

```python
FastCRUD(
    model: Type[Model],                    # 必需：Tortoise ORM 模型

    # 路由配置
    prefix: str = None,                    # 路由前缀，默认为 "/{model_name}"
    tags: List[str] = None,                # API 文档标签

    # Schema 配置
    create_schema: Type[BaseModel] = None, # 自定义创建 Schema
    read_schema: Type[BaseModel] = None,   # 自定义读取 Schema
    update_schema: Type[BaseModel] = None, # 自定义更新 Schema

    # 功能开关
    cache: Union[bool, CacheConfig] = False,      # 缓存配置
    hooks: Union[bool, HookConfig] = False,       # Hook 配置
    monitoring: Union[bool, MonitoringConfig] = False, # 监控配置

    # 查询配置
    relations: List[str] = None,           # 关联字段列表
    text_contains_search: bool = True,     # 文本包含搜索
    debug_mode: bool = False,              # 调试模式

    # 依赖注入
    dependencies: Union[List[Depends], DependencyConfig] = None,
)
```

### 缓存配置

```python
CacheConfig(
    enabled: bool = True,                  # 是否启用缓存
    backend: str = "memory",               # 缓存后端：memory 或 redis
    default_ttl: int = 3600,               # 默认过期时间（秒）
    key_prefix: str = "fastapi_crud:",     # 缓存键前缀

    # 内存缓存配置
    max_memory_items: int = 1000,          # 最大缓存项数

    # Redis 配置
    redis_url: str = "redis://localhost:6379/0",
    redis_pool_size: int = 10,
    redis_timeout: int = 5,
)
```

### Hook 配置

```python
HookConfig(
    enabled: bool = True,                  # 是否启用 Hook
    debug_mode: bool = False,              # 调试模式
    stop_on_error: bool = True,            # 遇到错误时停止
    max_execution_time: float = 30.0,      # 最大执行时间（秒）
    timeout_per_hook: float = 5.0,         # 单个 Hook 超时时间
    enable_timing: bool = True,            # 启用执行时间统计
    enable_metrics: bool = True,           # 启用指标收集
)
```

## 🤝 最佳实践

### 🏗️ 项目结构建议

```
your_project/
├── models/
│   ├── __init__.py
│   ├── user.py          # 用户模型
│   └── product.py       # 商品模型
├── schemas/
│   ├── __init__.py
│   ├── user.py          # 用户 Schema
│   └── product.py       # 商品 Schema
├── dependencies/
│   ├── __init__.py
│   ├── auth.py          # 认证依赖
│   └── permissions.py   # 权限依赖
├── hooks/
│   ├── __init__.py
│   ├── user_hooks.py    # 用户相关 Hook
│   └── product_hooks.py # 商品相关 Hook
├── crud/
│   ├── __init__.py
│   └── setup.py         # CRUD 配置
└── main.py              # 主应用
```

### 🎯 性能优化建议

1. **合理使用缓存**
   ```python
   # 读多写少的数据使用长期缓存
   category_crud = FastCRUD(
       model=Category,
       cache=CacheConfig(default_ttl=7200)  # 2小时
   )

   # 频繁变化的数据使用短期缓存
   order_crud = FastCRUD(
       model=Order,
       cache=CacheConfig(default_ttl=300)   # 5分钟
   )
   ```

2. **优化关联查询**
   ```python
   # 只加载需要的关联数据
   user_crud = FastCRUD(
       model=User,
       relations=["profile"]  # 不要加载所有关联
   )
   ```

3. **使用分页**
   ```python
   # 设置合理的分页大小
   crud = FastCRUD(
       model=User,
       default_page_size=20,
       max_page_size=100
   )
   ```

### 🛡️ 安全建议

1. **输入验证**
   ```python
   class UserCreateSchema(BaseModel):
       name: str = Field(..., min_length=2, max_length=50)
       email: EmailStr = Field(...)
       age: int = Field(..., ge=0, le=150)
   ```

2. **权限控制**
   ```python
   # 细粒度权限控制
   crud = FastCRUD(
       model=User,
       dependencies=DependencyConfig(
           endpoint_dependencies={
               EndpointType.CREATE: [Depends(require_admin)],
               EndpointType.DELETE: [Depends(require_admin)],
           }
       )
   )
   ```

3. **敏感数据处理**
   ```python
   @crud.hook(HookStage.POST_READ)
   async def filter_sensitive_data(data: dict, result: dict, context: HookContext):
       """过滤敏感数据"""
       if "password" in result:
           del result["password"]
       return result
   ```

## 🔍 故障排除

### 常见问题

**Q: 为什么我的关联数据没有加载？**
```python
# 确保在 relations 中指定了关联字段
crud = FastCRUD(
    model=User,
    relations=["profile", "orders"]  # 添加这一行
)
```

**Q: 缓存没有生效？**
```python
# 检查缓存配置
crud = FastCRUD(
    model=User,
    cache=True  # 或者 CacheConfig(...)
)

# 检查是否安装了 Redis（如果使用 Redis 缓存）
pip install redis
```

**Q: Hook 没有执行？**
```python
# 确保启用了 Hook 系统
crud = FastCRUD(
    model=User,
    hooks=True  # 添加这一行
)

# 检查 Hook 注册
@crud.hook(HookStage.PRE_CREATE)  # 确保使用正确的 crud 实例
async def my_hook(data: dict, context: HookContext):
    pass
```

**Q: 依赖注入不工作？**
```python
# 确保依赖函数是异步的
async def get_current_user(request: Request):  # async 关键字
    pass

# 确保正确配置依赖
crud = FastCRUD(
    model=User,
    dependencies=DependencyConfig(
        global_dependencies=[Depends(get_current_user)]
    )
)
```

### 调试技巧

1. **启用调试模式**
   ```python
   crud = FastCRUD(
       model=User,
       debug_mode=True,  # 启用详细日志
       hooks=HookConfig(debug_mode=True)
   )
   ```

2. **查看生成的路由**
   ```python
   # 打印所有路由
   for route in app.routes:
       print(f"{route.methods} {route.path}")
   ```

3. **监控性能**
   ```python
   # 启用性能监控
   crud = FastCRUD(
       model=User,
       monitoring=True
   )

   # 查看性能指标
   @app.get("/debug/metrics")
   async def debug_metrics():
       return crud.monitoring_manager.get_metrics()
   ```

## 🚀 升级指南

### 从 0.x 版本升级

如果你正在使用旧版本，请参考以下升级指南：

```python
# 旧版本 (0.x)
from fastapi_tortoise_crud import ModelCrud

crud = ModelCrud(
    model=User,
    create_schema=UserCreate,
    update_schema=UserUpdate
)

# 新版本 (1.x)
from fastapi_tortoise_crud import FastCRUD

crud = FastCRUD(
    model=User,
    create_schema=UserCreate,
    update_schema=UserUpdate
)
```

主要变化：
- `ModelCrud` → `FastCRUD`
- 新增 Hook 系统
- 新增缓存系统
- 改进的依赖注入
- 统一的响应格式

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 🐛 报告问题

在 [GitHub Issues](https://github.com/your-repo/fastapi-tortoise-crud/issues) 中报告问题时，请提供：

1. 详细的问题描述
2. 复现步骤
3. 期望的行为
4. 实际的行为
5. 环境信息（Python 版本、依赖版本等）

### 💡 功能建议

我们欢迎新功能建议！请在 Issues 中描述：

1. 功能的用途和价值
2. 详细的功能描述
3. 可能的实现方案
4. 相关的示例代码

### 🔧 开发环境设置

```bash
# 克隆项目
git clone https://github.com/your-repo/fastapi-tortoise-crud.git
cd fastapi-tortoise-crud

# 安装开发依赖
pip install -e ".[dev]"

# 运行测试
pytest

# 运行示例
python examples/complete_example.py
```

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

感谢以下优秀的开源项目：

- [FastAPI](https://fastapi.tiangolo.com/) - 现代、快速的 Web 框架
- [Tortoise ORM](https://tortoise.github.io/) - 异步 ORM
- [Pydantic](https://pydantic-docs.helpmanual.io/) - 数据验证库

## 📞 联系我们

- 📧 邮箱：768091671@qq.com
- 🐛 问题反馈：[GitHub Issues](https://github.com/your-repo/fastapi-tortoise-crud/issues)
- 💬 讨论：[GitHub Discussions](https://github.com/your-repo/fastapi-tortoise-crud/discussions)

---

⭐ 如果这个项目对你有帮助，请给我们一个 Star！
