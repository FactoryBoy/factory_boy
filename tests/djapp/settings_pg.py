# Copyright: See the LICENSE file.

"""Settings for factory_boy/Django tests."""

import os

from .settings import *  # noqa: F401, F403

try:
    # pypy does not support `psycopg2` or `psycopg2-binary`
    # This is a package that only gets installed with pypy, and it needs to be
    # initialized for it to work properly. It mimic `psycopg2` 1-to-1
    from psycopg2cffi import compat
    compat.register()
except ImportError:
    pass

postgres_user = os.environ.get('POSTGRES_USER', 'postgres')
postgres_name = os.environ.get('POSTGRES_DATABASE', 'factory_boy_test')
postgres_password = os.environ.get('POSTGRES_PASSWORD', 'password')
postgres_host = os.environ.get('POSTGRES_HOST', 'localhost')
postgres_port = os.environ.get('POSTGRES_PORT', '5432')

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': postgres_name,
        'USER': postgres_user,
        'PASSWORD': postgres_password,
        'HOST': postgres_host,
        'PORT': postgres_port,
    },
    'replica': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': postgres_name + '_rp',
        'USER': postgres_user,
        'PASSWORD': postgres_password,
        'HOST': postgres_host,
        'PORT': postgres_port,
    }
}
