import datetime
import enum

import faker.config

import factory
import factory.fuzzy


LANGS = sorted(locale[:2] for locale in faker.config.AVAILABLE_LOCALES)

# Helpers: we'll pretend this is a model.

class Model:
    def __init__(self, **kwargs):
        for field, value in kwargs.items():
            if not hasattr(self.__class__, field):
                raise ValueError("Class %s has no field %r" % (self.__class__, field))
            setattr(self, field, value)
            if isinstance(value, Model):
                value.add_relation(self.__class__, self)

    def add_relation(self, related_class, value):
        field_name = '%s_set' % related_class.__name__.lower()
        if not hasattr(self, field_name):
            setattr(self, field_name, [])
        getattr(self, field_name).append(value)

    def __str__(self):
        return '@%s' % id(self)

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, str(self))


def FakeField(*args, **kwargs):
    pass


BooleanField = FakeField
CharField = FakeField
DateField = FakeField
ForeignKey = FakeField
IntegerField = FakeField
TextField = FakeField


class Author(Model):
    fullname = TextField()

    birthdate = DateField()
    death = DateField(null=True)

    main_language = CharField(max_length=2)  # iso639-1 alpha-2 language code

    def __str__(self):
        return "{name} ({birth} - {death}) [{lang}]".format(
            name=self.fullname,
            birth=self.birthdate.isoformat(),
            death=self.death.isoformat() if self.death else '',
            lang=self.main_language,
        )


class BasicAuthorFactory(factory.Factory):
    fullname = factory.Faker('name')
    birthdate = factory.fuzzy.FuzzyDate(
        start_date=datetime.date(1, 1, 1),
        end_date=datetime.date.today() - datetime.timedelta(days=20 * 365),
    )
    death = None
    main_language = 'en'

    class Meta:
        model = Author



class MortalAuthorFactory(BasicAuthorFactory):
    @factory.lazy_attribute
    def death(self):
        cutoff = self.birthdate + datetime.timedelta(days=100 * 365)
        if cutoff < datetime.date.today():
            return cutoff
        else:
            # Too young to die
            return None



class UnluckyAuthorFactory(MortalAuthorFactory):
    class Params:
        death_age = factory.fuzzy.FuzzyInteger(20, 100)

    @factory.lazy_attribute
    def death(self):
        cutoff = self.birthdate + datetime.timedelta(days=self.death_age * 366)
        if cutoff < datetime.date.today():
            return cutoff
        else:
            # Too young to die
            return None


class Book(Model):
    title = TextField()
    summary = TextField()

    author = ForeignKey(Author)
    publication_date = DateField()
    language = CharField(max_length=2)

    def __str__(self):
        return """"{title}" by {author} (pub. {publication})""".format(
            title=self.title,
            author=self.author.fullname,
            publication=self.publication_date.isoformat(),
        )


class BasicBookFactory(factory.Factory):
    title = factory.Faker('catch_phrase')
    summary = factory.Faker('text', max_nb_chars=2000)

    author = factory.SubFactory(UnluckyAuthorFactory)

    publication_date = factory.fuzzy.FuzzyDate(
        start_date=datetime.date(1, 1, 1),
    )
    language = 'en'

    class Meta:
        model = Book


class AuthenticBookFactory(BasicBookFactory):
    class Params:
        min_publication_date = factory.LazyAttribute(
            lambda book: book.author.birthdate + datetime.timedelta(days=15 * 365),
        )
        max_publication_date = factory.LazyAttribute(
            lambda book: book.author.death or datetime.today(),
        )

    publication_date = factory.LazyResolver(
        factory.fuzzy.FuzzyDate,
        start_date=factory.SelfAttribute('..min_publication_date'),
        end_date=factory.SelfAttribute('..max_publication_date'),
    )


class Copy(Model):
    book = ForeignKey(Book)
    #: An identifier for a specific copy of the book
    material_number = IntegerField()

    # An Enum is great for pretty-printing options!
    class Condition(enum.Enum):
        PRISTINE = "Pristine"
        LIGHT_WEAR = "Light wear"
        USED = "Used"
        DAMAGED = "Damaged"

    condition = CharField(choices=[(c.name, c.value) for c in Condition])

    def __str__(self):
        return """"{b.title}" by {b.author.fullname} [#{nb}, {cond}]""".format(
            b=self.book,
            nb=self.material_number,
            cond=self.condition.value,
        )


class CopyFactory(factory.Factory):
    book = factory.SubFactory(AuthenticBookFactory)
    material_number = factory.Sequence(lambda n: n)
    condition = factory.fuzzy.FuzzyChoice(Copy.Condition)

    class Meta:
        model = Copy


class PhysicalBookFactory(AuthenticBookFactory):
    copy = factory.RelatedFactory(CopyFactory, 'book')


class IndestructibleBookFactory(PhysicalBookFactory):
    copy = factory.RelatedFactory(
        CopyFactory, 'book',
        condition=Copy.Condition.PRISTINE,
    )


class UltraSolidBookFactory(PhysicalBookFactory):
    copy__condition = Copy.Condition.PRISTINE


class MultiConditionBookFactory(PhysicalBookFactory):

    @factory.post_generation
    def ensure_pristine_copy(self, create, override, **extra):
        while not any(
                copy.condition is Copy.Condition.PRISTINE
                for copy in self.copy_set
                ):
            CopyFactory(book=self)


class Patron(Model):
    name = TextField()


class Loan(Model):
    # FIXME: Copy?
    book = ForeignKey(Book)
    borrower = ForeignKey(Patron)

    start = DateField()
    due = DateField()
    returned_on = DateField()

