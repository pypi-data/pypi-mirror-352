"""Delivery functions for Django Webhook Subscriber."""

import requests

from django.utils import timezone

from django_webhook_subscriber.conf import rest_webhook_settings
from django_webhook_subscriber.tasks import (
    async_deliver_webhook,
    process_webhook_batch,
)


def prepare_headers(webhook):
    """Prepare headers for the webhook request."""

    headers = webhook.headers.copy() if webhook.headers else {}

    # Add content type header if not present
    if 'Content-Type' not in headers:
        headers['Content-Type'] = 'application/json'

    # Add secret key authentication header
    headers['X-Secret'] = webhook.secret

    return headers


def deliver_webhook(webhook, payload, event_signal):
    """Deliver the webhook to the specified endpoint."""

    from django_webhook_subscriber.models import WebhookDeliveryLog

    # Create delivery log
    delivery_log = WebhookDeliveryLog.objects.create(
        webhook=webhook,
        event_signal=event_signal,
        payload=payload,
    )

    try:
        # Prepare request parameters
        headers = prepare_headers(webhook)
        timeout = getattr(rest_webhook_settings, 'REQUEST_TIMEOUT')

        # Send the request
        response = requests.post(
            webhook.endpoint,
            json=payload,
            headers=headers,
            timeout=timeout,
        )

        # Update delivery log with response
        delivery_log.response_status = response.status_code
        delivery_log.response_body = response.content
        delivery_log.save()

        # Update webhook with response info
        if webhook.keep_last_response:
            webhook.last_response = response.content

        # Update success/failure timestamps
        now = timezone.now()
        if 200 <= response.status_code < 300:
            # if response.ok:
            webhook.last_success = now
        else:
            webhook.last_failure = now

        webhook.save()

    except Exception as e:
        # Handle errors
        delivery_log.error_message = str(e)
        delivery_log.save()

        # Update webhook failure timestamp
        webhook.last_failure = timezone.now()
        webhook.save()

    return delivery_log


def get_webhook_for_model(model_instance):
    """Get all active webhooks for a model instance."""

    from django.contrib.contenttypes.models import ContentType

    model_class = model_instance.__class__
    content_type = ContentType.objects.get_for_model(model_class)

    from django_webhook_subscriber.models import WebhookRegistry

    # Get al active webhooks for this content type
    return WebhookRegistry.objects.filter(
        content_type=content_type,
        is_active=True,
    )


def get_async_setting(webhook, system_default):
    """Determine if the webhook should use async delivery."""

    # If webhook has specific setting, use it
    if webhook.use_async is not None:
        return webhook.use_async

    # Otherwise, use system default
    return system_default


def process_and_deliver_webhook(
    instance,
    event_signal,
    serialized_payload=None,
    async_delivery=False,
    serializer=None,
):
    """Process and deliver the webhook for a given instance and event type.

    This function checks the event type and the model class of the instance in
    the registry. If the event type is registered, it serializes the instance
    using the specified serializer (if any) and calls the delivery function to
    send the webhook.
    If the webhook is configured for async delivery, it will be processed
    asynchronously using Celery tasks. If the webhook is configured for
    synchronous delivery, it will be processed immediately.
    """

    # Determine system default for async delivery
    system_default = getattr(rest_webhook_settings, 'DEFAULT_USE_ASYNC')

    # If specific async_delivery is specified, override the system default
    if async_delivery is not None:
        system_default = async_delivery

    # If no payload is provided, serialize the instance
    if serialized_payload is None:
        from django_webhook_subscriber.serializers import serialize_instance

        serialized_payload = serialize_instance(
            instance,
            event_signal,
            field_serializer=serializer,
        )

    # Get all active webhooks for this model
    webhooks = get_webhook_for_model(instance)
    delivery_logs = []

    # Filter webhooks for this model
    sync_webhooks = []
    async_webhooks = []

    for webhook in webhooks:
        # Map event type to registry format
        event_mapping = {
            'created': 'CREATE',
            'updated': 'UPDATE',
            'deleted': 'DELETE',
        }
        registry_event = event_mapping.get(event_signal, event_signal)

        # Skip if this webhook isn't configured for this event type
        if registry_event not in webhook.event_signals:
            continue

        # Check if this webhook should use async delivery
        if get_async_setting(webhook, system_default):
            async_webhooks.append(webhook)
        else:
            sync_webhooks.append(webhook)

    # Process async webhooks
    tasks_ids = []
    if async_webhooks:
        try:
            # If we only have one webhook, we'll process it directly
            if len(async_webhooks) == 1:
                webhook = async_webhooks[0]
                task_id = async_deliver_webhook.delay(
                    webhook.id,
                    serialized_payload,
                    event_signal,
                )
                tasks_ids.append(task_id.id)
            else:
                # Otherwise, we'll process them in a batch
                webhook_ids = [w.id for w in async_webhooks]
                batch_task = process_webhook_batch.delay(
                    webhook_ids,
                    serialized_payload,
                    event_signal,
                )
                tasks_ids.append(batch_task.id)
        except ImportError:
            # Celery is not installed, fall back to synchronous delivery
            sync_webhooks.extend(async_webhooks)

    # Process sync webhooks
    for webhook in sync_webhooks:
        delivery_log = deliver_webhook(
            webhook, serialized_payload, event_signal
        )
        delivery_logs.append(delivery_log)

    return delivery_logs + tasks_ids
