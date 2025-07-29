"""Testing utilities for Django Webhook Subscriber."""

from django.test.utils import override_settings

# Context manager for disabling webhooks in tests
disabled_webhooks = override_settings(DISABLE_WEBHOOKS=True)


# Function to use in setUp methods
def disable_webhooks_for_testing():
    """Disable webhooks for test purposes by unregistering all signals."""
    from django_webhook_subscriber.utils import unregister_webhook_signals

    unregister_webhook_signals()
