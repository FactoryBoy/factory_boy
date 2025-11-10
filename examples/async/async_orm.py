"""
Example of using factory_boy async support with ORM factories.

This demonstrates how to use async with:
- DjangoModelFactory
- SQLAlchemyModelFactory
- MogoFactory
- MongoEngineFactory
"""

import asyncio
import factory


# ============================================================================
# Example 1: Basic ORM Factory with Default Async Support
# ============================================================================

class User:
    """Simple model that simulates an ORM model."""
    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email
        self.saved = False
    
    def save(self):
        """Simulate save operation."""
        self.saved = True
    
    def __repr__(self):
        return f"User(name={self.name}, email={self.email}, saved={self.saved})"


class UserFactory(factory.mogo.MogoFactory):
    """Factory using MogoFactory as an example."""
    class Meta:
        model = User
    
    name = factory.Sequence(lambda n: f'User {n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.name.lower().replace(" ", ".")}@example.com')


# ============================================================================
# Example 2: Custom Async ORM (e.g., Django async ORM, SQLAlchemy AsyncSession)
# ============================================================================

class AsyncUser:
    """Model with async save method."""
    def __init__(self, name=None, email=None):
        self.name = name
        self.email = email
        self.async_saved = False
    
    async def async_save(self):
        """Simulate async save operation (e.g., async DB query)."""
        await asyncio.sleep(0.01)  # Simulate I/O
        self.async_saved = True
    
    def __repr__(self):
        return f"AsyncUser(name={self.name}, email={self.email}, async_saved={self.async_saved})"


class AsyncUserFactory(factory.mogo.MogoFactory):
    """Factory with custom async create for true async ORM."""
    class Meta:
        model = AsyncUser
    
    name = factory.Sequence(lambda n: f'AsyncUser {n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.name.lower().replace(" ", ".")}@example.com')
    
    @classmethod
    async def _async_create(cls, model_class, *args, **kwargs):
        """Override to use async ORM methods."""
        instance = model_class(*args, **kwargs)
        await instance.async_save()  # Use async save instead of sync save
        return instance


# ============================================================================
# Example 3: Django-like Factory with Async ORM
# ============================================================================

class DjangoLikeModel:
    """Simulates a Django model."""
    
    class Manager:
        """Simulates Django manager."""
        async def acreate(self, **kwargs):
            """Simulate Django's async create."""
            await asyncio.sleep(0.01)
            instance = DjangoLikeModel(**kwargs)
            instance.saved = True
            return instance
    
    objects = Manager()
    
    def __init__(self, title=None, content=None):
        self.title = title
        self.content = content
        self.saved = False
    
    def __repr__(self):
        return f"DjangoLikeModel(title={self.title}, saved={self.saved})"


class DjangoLikeFactory(factory.django.DjangoModelFactory):
    """Factory that uses Django's async ORM."""
    class Meta:
        model = DjangoLikeModel
    
    title = factory.Sequence(lambda n: f'Post {n}')
    content = 'Content'
    
    @classmethod
    async def _async_create(cls, model_class, *args, **kwargs):
        """Override to use Django's async ORM (Django 3.1+)."""
        # In real Django, you would use:
        # manager = cls._get_manager(model_class)
        # return await manager.acreate(*args, **kwargs)
        return await model_class.objects.acreate(**kwargs)


# ============================================================================
# Main Demo
# ============================================================================

async def main():
    print("=" * 70)
    print("Factory Boy Async ORM Support Demo")
    print("=" * 70)
    print()
    
    # Example 1: Default async support (runs sync _create in thread pool)
    print("1. Default async support (thread pool):")
    print("   Creating users with sync save()...")
    users = await UserFactory.async_create_batch(3)
    for user in users:
        print(f"   - {user}")
    print()
    
    # Example 2: Custom async ORM
    print("2. Custom async ORM (true async):")
    print("   Creating users with async save()...")
    async_users = await AsyncUserFactory.async_create_batch(3)
    for user in async_users:
        print(f"   - {user}")
    print()
    
    # Example 3: Django-like async ORM
    print("3. Django-like async ORM:")
    print("   Creating posts with async manager.acreate()...")
    posts = await DjangoLikeFactory.async_create_batch(3)
    for post in posts:
        print(f"   - {post}")
    print()
    
    # Example 4: Performance comparison
    print("4. Performance comparison:")
    print("   Sequential vs Parallel creation...")
    
    import time
    
    # Sequential
    start = time.time()
    for _ in range(5):
        await AsyncUserFactory.async_create()
    sequential_time = time.time() - start
    
    # Parallel
    start = time.time()
    await AsyncUserFactory.async_create_batch(5)
    parallel_time = time.time() - start
    
    print(f"   Sequential: {sequential_time:.3f}s")
    print(f"   Parallel:   {parallel_time:.3f}s")
    print(f"   Speedup:    {sequential_time / parallel_time:.1f}x")
    print()
    
    print("=" * 70)
    print("Key Points:")
    print("=" * 70)
    print("1. All ORM factories support async")
    print("2. Default: calls sync _create() (simple and straightforward)")
    print("3. Override _async_create() for true async ORM:")
    print("   - Django 3.1+: use manager.acreate()")
    print("   - SQLAlchemy 1.4+: use AsyncSession")
    print("   - MongoDB: use motor for async operations")
    print("4. async_create_batch() provides true parallelism")
    print("=" * 70)


if __name__ == '__main__':
    asyncio.run(main())

