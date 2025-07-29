"""Utility functions for Django Webhook Subscriber."""

# Dictionary to store model -> configuration mappings
_webhook_registry = {}


def get_webhook_config(model_class):
    """Retrieve the webhook configuration for a model class.

    If no configuration is found, return None.
    """
    return _webhook_registry.get(model_class, None)


def register_model_config(model_class, serializer=None, events=None):
    """Register a model class with its configuration.

    Stores the model class and its configuration in the global
    registry - _webhook_registry.
    """

    # If signal_events is None, set it to all events
    if events is None:
        events = list(['CREATE', 'UPDATE', 'DELETE'])
    else:
        # Normalize signal events to uppercase
        events = [event.upper() for event in events]

    # Store the configuration in the registry
    _webhook_registry[model_class] = {
        'serializer': serializer,
        'events': events,
    }

    return _webhook_registry[model_class]


def unregister_webhook_signals(model_class=None):
    """Disable webhooks by disconnecting all signals.

    If a specific model class is provided as an argument, only that model's
    signals will be disconnected. If no model class is provided, all signals
    will be disconnected.
    This function is useful for disabling webhooks in tests or when
    reconfiguring the webhook system.
    """

    from django_webhook_subscriber.signals import (
        webhook_post_save,
        webhook_post_delete,
    )
    from django.db.models.signals import post_save, post_delete

    if model_class:
        # If a specific model class is provided, remove its entry from the
        # registry
        if model_class in _webhook_registry:
            post_save.disconnect(
                webhook_post_save,
                sender=model_class,
                dispatch_uid=f'webhook_post_save_{model_class.__name__}',
            )
            post_delete.disconnect(
                webhook_post_delete,
                sender=model_class,
                dispatch_uid=f'webhook_post_delete_{model_class.__name__}',
            )
        return _webhook_registry

    # Disconnect all signals
    for model_class in _webhook_registry.keys():
        # Disconnect signals for the model class
        post_save.disconnect(
            webhook_post_save,
            sender=model_class,
            dispatch_uid=f'webhook_post_save_{model_class.__name__}',
        )
        post_delete.disconnect(
            webhook_post_delete,
            sender=model_class,
            dispatch_uid=f'webhook_post_delete_{model_class.__name__}',
        )

    return _webhook_registry
