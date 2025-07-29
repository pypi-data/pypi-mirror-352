SECRET_KEY = 'test_secret_key'
INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'django.contrib.sessions',
    'django_webhook_subscriber',
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

USE_TZ = True

CELERY_TASK_ALWAYS_EAGER = True  # Celery executes tasks synchronously
CELERY_TASK_EAGER_PROPAGATES = True  # Propagate exceptions to the caller
