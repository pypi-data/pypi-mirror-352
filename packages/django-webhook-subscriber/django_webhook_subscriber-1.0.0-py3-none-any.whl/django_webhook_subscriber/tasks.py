"""Tasks for Django Webhook Subscriber."""

from celery import shared_task


@shared_task(
    bind=True,
    max_retries=3,  # Default to 3 retries
    default_retry_delay=60,  # Wait 60 seconds between retries
    autoretry_for=(Exception,),  # Retry for any exception
    retry_backoff=True,  # Use exponential backoff
)
def async_deliver_webhook(self, webhook_id, payload, event_signal):
    """Asynchronously deliver a webhook.

    This task is designed to be called when a webhook delivery fails.
    It will retry the delivery based on the webhook's settings.
    The task will also respect the retry settings defined in the
    WebhookRegistry model.
    If the webhook has been deactivated, the task will not attempt
    to deliver the webhook again.
    """

    from django_webhook_subscriber.models import WebhookRegistry
    from django_webhook_subscriber.delivery import deliver_webhook

    try:
        webhook = WebhookRegistry.objects.get(pk=webhook_id)

        # Override the retry settings if specified in the webhook
        if webhook.max_retries:
            self.max_retries = webhook.max_retries
        if webhook.retry_delay:
            self.default_retry_delay = webhook.retry_delay

        # Skip delivery if webhook has been deactivated since the task was
        # queued
        if not webhook.is_active:
            return None

        delivery_log = deliver_webhook(webhook, payload, event_signal)

        return delivery_log.id

    except WebhookRegistry.DoesNotExist:
        # Webhook was deleted, no need to retry
        return None
    except Exception as exc:
        # For any other exception, rely on Celery's retry mechanism
        raise self.retry(exc=exc)


@shared_task
def process_webhook_batch(webhook_ids, payload, event_signal):
    """Process a batch of webhooks.

    This task is designed to be called when a batch of webhooks needs
    to be delivered. It will create a group of tasks for each webhook
    and deliver them asynchronously.
    """

    from celery import group

    tasks = [
        async_deliver_webhook.s(webhook_id, payload, event_signal)
        for webhook_id in webhook_ids
    ]

    # Execute tasks in parallel
    if tasks:
        return group(tasks).apply_async()

    return None
