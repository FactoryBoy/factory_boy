from abc import abstractmethod

from faker.proxy import Faker


class ISequenceGenerator:

    @abstractmethod
    def initialize(self, seed):
        pass

    @abstractmethod
    def next(self, *args, **kwargs):
        pass

    @abstractmethod
    def reset(self):
        pass


class _Counter(ISequenceGenerator):
    """Simple, naive counter.

    Attributes:
        for_class (obj): the class this counter related to
        seq (int): the next value
    """

    def __init__(self, seq):
        self.seq = seq

    def initialize(self, seed):
        pass

    def next(self, *args, **kwargs):
        value = self.seq
        self.seq += 1
        return value

    def reset(self, next_value=0):
        self.seq = next_value


class _UniqueStore(ISequenceGenerator):

    def __init__(self, locale=None, custom_providers=None):
        self.faker_instance = Faker(
            locale=locale, includes=custom_providers
        )

    def initialize(self, seed):
        self.faker_instance.seed(seed)

    def next(self, *args, **kwargs):
        if len(args) == 0:
            raise ValueError("No provider passed in parameters.")
        provider = args[0]
        faker_provider_func = getattr(self.faker_instance.unique, provider, None)
        if faker_provider_func is None:
            raise ValueError(f"Faker provider {provider} is not available.")
        return faker_provider_func(*args[1:], **kwargs)

    def reset(self):
        self.faker_instance.unique.clear()
