# Async Examples for factory_boy

This directory contains examples demonstrating the async support in factory_boy.

## Examples

### 1. `async_basic.py` - Basic Async Usage

Demonstrates the fundamental async features:
- Using `async_create()` method
- Using `await MyFactory()` with `ASYNC_CREATE_STRATEGY`
- Nested SubFactory in async context
- Overriding nested factory attributes
- Creating multiple objects concurrently
- Async batch creation with `async_create_batch()`

**Run:**
```bash
cd examples/async
python3 async_basic.py
```

**Key Features:**
- `ASYNC_CREATE_STRATEGY` - Set as Meta.strategy to enable `await MyFactory()`
- `async_create()` - Create instances asynchronously
- `async_create_batch()` - Create multiple instances in parallel
- `async_build_batch()` - Build multiple instances in parallel
- SubFactory works seamlessly in async context

### 2. `async_orm.py` - ORM Integration

Demonstrates async support with ORM factories:
- Default async support (thread pool for blocking I/O)
- Custom async ORM implementation (Django, SQLAlchemy)
- Performance comparison (sequential vs parallel)

**Run:**
```bash
cd examples/async
python3 async_orm.py
```

**Supported ORMs:**
- `DjangoModelFactory` - Django 3.1+ async ORM
- `SQLAlchemyModelFactory` - SQLAlchemy 1.4+ AsyncSession
- `MongoEngineFactory` - motor for async MongoDB
- `MogoFactory` - motor for async MongoDB

## Quick Start

### Basic Usage

```python
import asyncio
import factory

class UserFactory(factory.Factory):
    class Meta:
        model = User
        strategy = factory.ASYNC_CREATE_STRATEGY  # Enable await syntax
    
    name = factory.Sequence(lambda n: f'User {n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.name}@example.com')

async def main():
    # Single creation
    user = await UserFactory()
    
    # Batch creation (parallel)
    users = await UserFactory.async_create_batch(100)

asyncio.run(main())
```

### ORM Usage

#### Django (3.1+)

```python
class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User
    
    name = 'John'
    
    @classmethod
    async def _async_create(cls, model_class, *args, **kwargs):
        # Use Django's async ORM
        manager = cls._get_manager(model_class)
        return await manager.acreate(*args, **kwargs)

# Usage
user = await UserFactory.async_create()
users = await UserFactory.async_create_batch(50)
```

#### SQLAlchemy (1.4+)

```python
from sqlalchemy.ext.asyncio import AsyncSession

class UserFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = async_session  # AsyncSession
    
    name = 'John'
    
    @classmethod
    async def _async_create(cls, model_class, *args, **kwargs):
        session = cls._meta.sqlalchemy_session
        obj = model_class(*args, **kwargs)
        session.add(obj)
        await session.flush()
        return obj

# Usage
user = await UserFactory.async_create()
```

## Performance Benefits

Async batch creation provides significant performance improvements:

```python
# Sequential: 0.5s (5 × 0.1s)
for _ in range(5):
    await UserFactory.async_create()

# Parallel: 0.1s (all concurrent)
await UserFactory.async_create_batch(5)

# Speedup: 5x
```

## Key Concepts

### 1. Simple and Straightforward

By default, all ORM factories call synchronous `_create()`:
- **Simple**: No complex thread pool management
- **Compatible**: Works with existing sync ORM code
- **No changes needed**: Existing factories work out of the box

### 2. True Async ORM

Override `_async_create()` for true async ORM support:
- **Django 3.1+**: Use `acreate()`, `aget_or_create()`
- **SQLAlchemy 1.4+**: Use `AsyncSession`
- **MongoDB**: Use motor for async operations

### 3. Parallel Batch Creation

`async_create_batch()` uses `asyncio.gather()` for true parallelism:
- Creates multiple instances concurrently
- Significant performance improvement for I/O-bound operations
- Each instance gets unique sequence values

## Testing

All async examples include tests in `tests/test_async.py` and `tests/test_async_orm.py`.

Run tests:
```bash
python3 -m unittest tests.test_async -v
python3 -m unittest tests.test_async_orm -v
```

## Requirements

- Python 3.8+
- factory_boy (with async support)
- Optional: Django 3.1+, SQLAlchemy 1.4+, motor (for async MongoDB)

## Learn More

See the main documentation for more details on async support.

