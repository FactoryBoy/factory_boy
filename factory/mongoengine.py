# Copyright: See the LICENSE file.


"""factory_boy extensions for use with the mongoengine library (pymongo wrapper)."""


from . import base


class MongoEngineFactory(base.Factory):
    """Factory for mongoengine objects."""

    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        return model_class(*args, **kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        instance = model_class(*args, **kwargs)
        if instance._is_document:
            instance.save()
        return instance

    @classmethod
    async def _async_create(cls, model_class, *args, **kwargs):
        """Create an instance asynchronously.

        By default, this calls the synchronous _create() method.
        Override this method if you're using motor or another async MongoDB driver.

        Example with motor:
            @classmethod
            async def _async_create(cls, model_class, *args, **kwargs):
                instance = model_class(*args, **kwargs)
                if instance._is_document:
                    await instance.async_save()  # motor's async save
                return instance
        """
        return cls._create(model_class, *args, **kwargs)
