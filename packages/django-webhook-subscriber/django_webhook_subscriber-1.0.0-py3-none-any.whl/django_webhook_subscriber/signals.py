"""Signal handlers for processing webhooks.

It includes functions to register models, connect signals, and process webhook
events.
"""

from django.apps import apps
from django.conf import settings
from django.utils.module_loading import import_string
from django.db.models.signals import post_save, post_delete

from django_webhook_subscriber.delivery import process_and_deliver_webhook
from django_webhook_subscriber.serializers import serialize_instance
from django_webhook_subscriber.utils import (
    get_webhook_config,
    register_model_config,
)


def process_webhook_event(instance, event_signal, **kwargs):
    """Process a webhook event by serializing the instance and delivering the
    webhook.

    This function checks the event type and the model class of the instance in
    the registry. If the event type is registered, it serializes the instance
    using the specified serializer (if any) and calls the delivery function to
    send the webhook.
    """

    # Skip if webhooks are disabled in settings
    if getattr(settings, 'DISABLE_WEBHOOKS', False):
        return

    model_class = instance.__class__

    # Get the webhook configuration for this model
    config = get_webhook_config(model_class)

    event_mappings = {
        'created': 'CREATE',
        'updated': 'UPDATE',
        'deleted': 'DELETE',
    }
    if config and event_mappings[event_signal] in config.get('events', []):
        # Get the serializer if configured, otherwise None (default will be
        # used)
        serializer = config.get('serializer')

        # Serialize the instance using either custom or default serializer
        payload = serialize_instance(
            instance,
            event_signal,
            field_serializer=serializer,
        )

        # Deliver webhooks
        process_and_deliver_webhook(
            instance,
            event_signal,
            serialized_payload=payload,
        )


def register_webhook_signals(model_class, serializer=None, events=None):
    """Register webhook signals for a specific model class."""

    # Register the configuration
    config = register_model_config(
        model_class,
        serializer=serializer,
        events=events,
    )

    # Connect signals based on requested events with a unique identifier
    if 'CREATE' in config['events'] or 'UPDATE' in config['events']:
        post_save.connect(
            webhook_post_save,
            sender=model_class,
            dispatch_uid=f'webhook_post_save_{model_class.__name__}',
        )

    if 'DELETE' in config['events']:
        post_delete.connect(
            webhook_post_delete,
            sender=model_class,
            dispatch_uid=f'webhook_post_delete_{model_class.__name__}',
        )


def webhook_post_save(sender, instance, created, **kwargs):
    """Handle post_save signals for webhook processing."""

    event_signal = 'created' if created else 'updated'
    process_webhook_event(
        instance=instance, event_signal=event_signal, **kwargs
    )


def webhook_post_delete(sender, instance, **kwargs):
    """Handle post_delete signals for webhook processing."""

    process_webhook_event(instance=instance, event_signal='deleted', **kwargs)


def register_webhooks_from_settings():
    """Register webhooks based on settings configuration.

    This function is called in AppConfig.ready() to ensure that webhooks are
    registered when the application starts.
    """

    from django.conf import settings

    # Skip registration if webhooks are disabled
    if getattr(settings, 'DISABLE_WEBHOOKS', False):
        return

    # Check if WEBHOOK_SUBSCRIBER is defined in settings
    if not hasattr(settings, 'WEBHOOK_SUBSCRIBER'):
        return

    # Getting WEBHOOKS_MODELS from settings
    webhook_settings = settings.WEBHOOK_SUBSCRIBER
    webhook_models = webhook_settings.get('WEBHOOK_MODELS', {})

    for model_path, config in webhook_models.items():
        # Split the model path into app_label and model_name
        try:
            app_label, model_name = model_path.split('.')
            model_class = apps.get_model(app_label, model_name)
        except Exception:
            # If model path is invalid or model doesn't exist, skip it
            continue

        # Get serializer if specified
        field_serializer = None
        if 'serializer' in config:
            try:
                field_serializer = import_string(config['serializer'])
            except ImportError:
                # If serializer import fails, skip it
                pass

        # Get events
        events = config.get('events', None)

        # Register the webhook
        register_webhook_signals(
            model_class,
            serializer=field_serializer,
            events=events,
        )
