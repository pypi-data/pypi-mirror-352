"""Models for Django Webhook Subscriber."""

import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.models import ContentType

from django_webhook_subscriber import managers


class WebhookRegistry(models.Model):
    """Webhook model to store webhook configurations.

    This represents a webhook registration in the system, including the
    associated model, event types, endpoint URL, authentication details,
    and response handling settings. The model uses Django's content types
    framework to allow association with any model in the system.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        max_length=255,
        help_text=_('Name of this webhook'),
    )

    # Model reference
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        help_text=_('The model this webhook is associated with'),
    )
    event_signals = models.JSONField(
        default=list,
        help_text=_(
            'Event types that trigger this webhook (e.g., CREATE, UPDATE,'
            ' DELETE)'
        ),
    )

    # Webhook delivery settings
    endpoint = models.CharField(
        max_length=255,
        help_text=_('URL to send the webhook to'),
    )
    secret = models.CharField(
        max_length=64,
        default=uuid.uuid4,
        help_text=_(
            'Secret key for webhook authentication via X-Secret header'
        ),
    )
    # Later on this would be a multiselect field
    headers = models.JSONField(
        default=dict,
        blank=True,
        help_text=_(
            'Additional headers to send with the webhook (JSON format)'
        ),
    )

    # Response handling
    keep_last_response = models.BooleanField(
        default=True,
        help_text=_('Whether to store the last response received'),
    )
    last_response = models.TextField(
        blank=True,
        null=True,
        help_text=_('Last response received from the webhook endpoint'),
    )
    last_success = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Timestamp of last successful delivery'),
    )
    last_failure = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_('Timestamp of last failed delivery'),
    )

    # Async delivery settings
    max_retries = models.PositiveIntegerField(
        default=3,
        null=True,
        blank=True,
        help_text=_('Maximum number of delivery attempts'),
    )
    retry_delay = models.PositiveIntegerField(
        default=60,
        null=True,
        blank=True,
        help_text=_('Seconds to wait between retry attempts'),
    )
    use_async = models.BooleanField(
        default=None,
        null=True,
        blank=True,
        help_text=_(
            'Whether to use async delivery (None = use system default)'
        ),
    )

    # Metadata
    is_active = models.BooleanField(
        default=True,
        help_text=_('Whether this webhook is active'),
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        db_table = 'django_webhook_subscriber_webhook_registry'
        verbose_name = _('Webhook')
        verbose_name_plural = _('Webhooks')

    def __str__(self):
        return f'{self.name} - {self.endpoint}'


class WebhookDeliveryLog(models.Model):
    """Webhook delivery log model to store delivery attempts and responses.

    This model records each delivery attempt made to a webhook endpoint,
    including the payload sent, the response received, and any errors
    encountered. It is useful for debugging and monitoring webhook
    performance.
    """

    id = models.AutoField(primary_key=True)
    webhook = models.ForeignKey(
        WebhookRegistry,
        on_delete=models.CASCADE,
        related_name='delivery_logs',
        help_text=_('The webhook that was delivered'),
    )
    # Later on this could be a choice field
    event_signal = models.CharField(
        max_length=255,
        help_text=_('The event type that triggered this delivery'),
    )

    # Delivery details
    payload = models.JSONField(help_text=_('The payload that was sent'))

    # Delivery status
    response_status = models.IntegerField(
        null=True,
        blank=True,
        help_text=_('HTTP status code of the response'),
    )
    response_body = models.TextField(
        null=True,
        blank=True,
        help_text=_('The body of the response received'),
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        help_text=_('Error message if the delivery failed'),
    )

    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)

    # Manager
    objects = managers.WebhookDeliveryLogManager()

    class Meta:
        ordering = ['-created_at']
        db_table = 'django_webhook_subscriber_webhook_delivery_log'
        verbose_name = _('Webhook Delivery Log')
        verbose_name_plural = _('Webhook Delivery Logs')

    def __str__(self):
        return (
            f'{self.webhook} - {self.event_signal} - '
            f'{self.response_status or "Failed"}'
        )
