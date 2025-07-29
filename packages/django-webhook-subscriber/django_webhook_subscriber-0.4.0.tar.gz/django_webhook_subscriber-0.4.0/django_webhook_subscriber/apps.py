"""Django Webhook Subscriber App Configuration."""

from django.apps import AppConfig
from django.conf import settings

from django_webhook_subscriber.signals import register_webhooks_from_settings
from django_webhook_subscriber.utils import unregister_webhook_signals


class WebhookSubscriberConfig(AppConfig):
    name = 'django_webhook_subscriber'
    verbose_name = 'Django Webhook Subscriber'

    def ready(self):
        """This method is called when the app is ready."""

        # Unregister all webhooks first (to clean up any existing signals)
        unregister_webhook_signals()

        # Only register webhooks if not disabled in settings
        if not getattr(settings, 'DISABLE_WEBHOOKS', False):
            # Registering webhooks from WEBHOOK_SUBSCRIBER['WEBHOOK_MODELS']
            register_webhooks_from_settings()
