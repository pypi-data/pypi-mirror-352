"""Managers for Django Webhook Subscriber."""

from django.db import models
from django.utils import timezone

from django_webhook_subscriber.conf import rest_webhook_settings


class WebhookDeliveryLogManager(models.Manager):
    """Custom manager for WebhookDeliveryLog model.

    This manager provides methods to filter logs based on their status,
    age, and to clean up old logs based on retention settings.
    """

    def cleanup_old_logs(self, webhook=None):
        """This method will cleanup old logs based on retention settings."""

        # Get retention period from settings
        days = getattr(rest_webhook_settings, 'LOG_RETENTION_DAYS')

        # Calculate cutoff date
        cutoff_date = timezone.now() - timezone.timedelta(days=days)

        # Build query
        query = self.filter(created_at__lt=cutoff_date)
        if webhook:
            # If a webhook is provided, filter by it
            query = query.filter(webhook=webhook)

        # Delete old logs
        query.delete()

    def create(self, **kwargs):
        """This method will create a new log entry, and proceed to cleanup
        old logs if necessary."""

        # create the log entry
        log = super().create(**kwargs)

        # Checking if AUTO_CLEANUP is set to True
        auto_cleanup = getattr(rest_webhook_settings, 'AUTO_CLEANUP')

        # cleanup old logs if necessary
        if auto_cleanup and kwargs['webhook']:
            # Using a try/except block to prevent any errors during cleanup
            # from affecting the log creation process
            try:
                self.cleanup_old_logs(webhook=kwargs['webhook'])
            except Exception:
                pass

        return log
