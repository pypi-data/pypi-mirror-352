"""Serializers for Django Webhook Subscriber

This module contains serializers for handling webhook events in Django REST
Framework. It provides functionality to serialize model instances into a
format suitable for webhook payloads.
"""

from rest_framework import serializers


def serialize_webhook_instance(instance, field_serializer):
    """Default serializer for webhook events.

    This function receives an instance, and serializes all its fields into a
    dictionary using the provided serializer class. If the serializer class
    is not a subclass of Django REST Framework's Serializer, it raises a
    ValueError.
    """

    # Check that the field_serializer is a rest_framework serializer
    if not issubclass(field_serializer, serializers.Serializer):
        raise ValueError(
            'field_serializer must be a subclass of rest_framework.Serializer'
        )

    # Create an instance of the serializer
    serializer = field_serializer(instance=instance)
    # Serialize the instance
    serialized_data = serializer.data
    # Return the serialized data
    return serialized_data


def serialize_instance(instance, event_signal, field_serializer=None):
    """Serialize a model instance for a webhook event.

    This function takes a model instance, an event type, and an optional
    serializer class. It serializes the instance using the specified
    serializer class. If no serializer class is provided, it falls back to
    a default serializer that serializes all fields of the model instance.
    """

    class DefaultWebhookSerializer(serializers.ModelSerializer):
        """Default serializer class for webhook events.

        This class is used to serialize all fields of a model instance into a
        dictionary format. It is a subclass of Django REST Framework's
        ModelSerializer.
        """

        class Meta:
            model = instance.__class__
            fields = '__all__'

    # TODO: need to have this integrated with rest_framework serializers
    if field_serializer is None:
        field_serializer = DefaultWebhookSerializer

    # Get model metadata
    model_class = instance.__class__
    app_label = model_class._meta.app_label
    model_name = model_class._meta.model_name

    # Create the payload structure
    payload = {
        'pk': instance.pk,
        'source': f'{app_label}.{model_name}',
        'event_signal': event_signal,
        'fields': serialize_webhook_instance(
            instance,
            field_serializer=field_serializer,
        ),
    }

    return payload
