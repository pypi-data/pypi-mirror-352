from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from copy import deepcopy

DEFAULTS = {
    'WEBHOOK_MODELS': {},
    'LOG_RETENTION_DAYS': 30,  # Number of days to keep logs
    'AUTO_CLEANUP': True,  # Automatically clean up old logs
    'DEFAULT_USE_ASYNC': True,  # Use async delivery by default
    'DEFAULT_MAX_RETRIES': 3,  # Default max retries for webhook delivery
    'DEFAULT_RETRY_DELAY': 60,  # Default delay between retries in seconds
    'REQUEST_TIMEOUT': 30,  # Default timeout for webhook requests
}

USER_SETTINGS = getattr(settings, 'WEBHOOK_SUBSCRIBER', {})


# Merge user settings with defaults
class Settings:
    def __init__(self, user_settings, defaults):
        self._user_settings = user_settings
        self._defaults = defaults

    def __getattr__(self, attr):
        if attr not in self._defaults:
            raise AttributeError(f"Invalid setting: '{attr}'")

        val = self._user_settings.get(attr, deepcopy(self._defaults[attr]))

        if attr in [
            'LOG_RETENTION_DAYS',
            'REQUEST_TIMEOUT',
            'DEFAULT_MAX_RETRIES',
            'DEFAULT_RETRY_DELAY',
        ]:
            if not isinstance(val, int) or val <= 0:
                raise ImproperlyConfigured(
                    f"Invalid value for '{attr}': {val}. It should be a "
                    "positive integer."
                )

        if attr == 'WEBHOOK_MODELS':
            if not isinstance(val, dict):
                raise ImproperlyConfigured(
                    f"Invalid value for '{attr}': {val}. It should be a "
                    "dictionary."
                )

        return val


# rest_webhook_settings = Settings(USER_SETTINGS, DEFAULTS)


# Lazy loading of settings
# This allows settings to be accessed without importing them directly
# from the settings module. This is useful for testing and other
# scenarios where the settings module may not be available.
class LazySettings:
    def __getattr__(self, attr):
        from django.conf import settings

        user_settings = getattr(settings, 'WEBHOOK_SUBSCRIBER', {})
        _settings = Settings(user_settings, DEFAULTS)
        return getattr(_settings, attr)


rest_webhook_settings = LazySettings()
