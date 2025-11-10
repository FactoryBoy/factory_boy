"""
Example of using factory_boy with async support.

This demonstrates the ASYNC_CREATE_STRATEGY feature.
"""

import asyncio
import factory


# Define some simple models
class User:
    def __init__(self, name=None, email=None, age=None):
        self.name = name
        self.email = email
        self.age = age
        self.id = None

    def __repr__(self):
        return f"User(id={self.id}, name={self.name}, email={self.email}, age={self.age})"


class Post:
    def __init__(self, title=None, content=None, author=None):
        self.title = title
        self.content = content
        self.author = author
        self.id = None

    def __repr__(self):
        return f"Post(id={self.id}, title={self.title}, author={self.author})"


class Comment:
    def __init__(self, text=None, post=None, author=None):
        self.text = text
        self.post = post
        self.author = author
        self.id = None

    def __repr__(self):
        return f"Comment(id={self.id}, text={self.text[:20]}..., author={self.author})"


# Define factories
class UserFactory(factory.Factory):
    class Meta:
        model = User

    name = factory.Sequence(lambda n: f'User {n}')
    email = factory.LazyAttribute(lambda obj: f'{obj.name.lower().replace(" ", ".")}@example.com')
    age = 25


class PostFactory(factory.Factory):
    class Meta:
        model = Post
        strategy = factory.ASYNC_CREATE_STRATEGY  # Use async strategy

    title = factory.Sequence(lambda n: f'Post Title {n}')
    content = 'This is the post content.'
    author = factory.SubFactory(UserFactory)


class CommentFactory(factory.Factory):
    class Meta:
        model = Comment
        strategy = factory.ASYNC_CREATE_STRATEGY  # Use async strategy

    text = 'This is a comment.'
    post = factory.SubFactory(PostFactory)
    author = factory.SubFactory(UserFactory)


async def main():
    print("=" * 60)
    print("Factory Boy Async Support Demo")
    print("=" * 60)
    print()

    # Example 1: Using async_create() method
    print("1. Using async_create() method:")
    user = await UserFactory.async_create(name='Alice')
    print(f"   Created: {user}")
    print()

    # Example 2: Using await with ASYNC_CREATE_STRATEGY
    print("2. Using await MyFactory() with ASYNC_CREATE_STRATEGY:")
    post = await PostFactory(title='My First Post')
    print(f"   Created: {post}")
    print(f"   Post author: {post.author}")
    print()

    # Example 3: Nested SubFactory in async context
    print("3. Nested SubFactory (Comment -> Post -> User):")
    comment = await CommentFactory(text='Great post!')
    print(f"   Created: {comment}")
    print(f"   Comment post: {comment.post}")
    print(f"   Comment post author: {comment.post.author}")
    print(f"   Comment author: {comment.author}")
    print()

    # Example 4: Override nested factory attributes
    print("4. Override nested factory attributes:")
    comment2 = await CommentFactory(
        text='Another comment',
        post__title='Custom Post Title',
        post__author__name='Bob'
    )
    print(f"   Created: {comment2}")
    print(f"   Comment post: {comment2.post}")
    print(f"   Comment post author: {comment2.post.author}")
    print()

    # Example 5: Multiple async creations
    print("5. Creating multiple objects asynchronously:")
    posts = await asyncio.gather(
        PostFactory(title='Post 1'),
        PostFactory(title='Post 2'),
        PostFactory(title='Post 3'),
    )
    for p in posts:
        print(f"   Created: {p}")
    print()

    # Example 6: Mix of sync and async
    print("6. Mix of sync and async factories:")
    sync_user = UserFactory.build(name='Sync User')
    async_post = await PostFactory(title='Async Post', author=sync_user)
    print(f"   Sync user: {sync_user}")
    print(f"   Async post: {async_post}")
    print(f"   Async post author: {async_post.author}")
    print()

    # Example 7: Async batch creation (parallel)
    print("7. Async batch creation (parallel):")
    import time
    start = time.time()
    posts = await PostFactory.async_create_batch(5, content='Batch content')
    elapsed = time.time() - start
    print(f"   Created {len(posts)} posts in {elapsed:.3f}s")
    for i, post in enumerate(posts):
        print(f"   - {post.title} by {post.author.name}")
    print()

    # Example 8: Async build batch
    print("8. Async build batch:")
    users = await UserFactory.async_build_batch(3)
    print(f"   Built {len(users)} users:")
    for user in users:
        print(f"   - {user}")
    print()

    print("=" * 60)
    print("All examples completed successfully!")
    print("=" * 60)


if __name__ == '__main__':
    asyncio.run(main())

