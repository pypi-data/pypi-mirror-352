from django.test import TestCase, override_settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

from django_webhook_subscriber.models import (
    WebhookRegistry,
    WebhookDeliveryLog,
)


class WebhookDeliveryLogManagerTests(TestCase):
    def setUp(self):
        # Get content type for User model
        self.user_content_type = ContentType.objects.get_for_model(User)

        # Create a webhook
        self.webhook = WebhookRegistry.objects.create(
            name="Test Webhook",
            content_type=self.user_content_type,
            event_signals=["CREATE", "UPDATE"],
            endpoint="https://example.com/webhook",
        )

    def _create_log_entry(self, event_signal='created', payload={}, **kwargs):
        created_at = kwargs.pop('created_at', None)

        log = WebhookDeliveryLog.objects.create(
            webhook=kwargs.get('webhook', self.webhook),
            event_signal=event_signal,
            payload=payload,
            **kwargs,
        )

        # setting created_at if provided
        if created_at:
            log.created_at = created_at
            log.save()

        return log

    def test_create_log_entry(self, event_signal='created'):
        log = WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal=event_signal,
            payload={"key": "value"},
            created_at=timezone.now(),
        )
        self.assertEqual(WebhookDeliveryLog.objects.count(), 1)
        self.assertEqual(log.webhook, self.webhook)

    @override_settings(WEBHOOK_SUBSCRIBER={'LOG_RETENTION_DAYS': 1})
    def test_cleanup_old_logs_deletes_old_entries(self):

        self._create_log_entry(created_at=timezone.now() - timedelta(days=2))
        self._create_log_entry()

        WebhookDeliveryLog.objects.cleanup_old_logs()

        self.assertEqual(WebhookDeliveryLog.objects.count(), 1)

    @override_settings(WEBHOOK_SUBSCRIBER={'LOG_RETENTION_DAYS': 1})
    def test_create_triggers_cleanup(self):
        # Create an old log
        old_log = self._create_log_entry(
            created_at=timezone.now() - timedelta(days=2),
        )
        # Manually update created_at to simulate old timestamp
        WebhookDeliveryLog.objects.filter(pk=old_log.pk).update(
            created_at=timezone.now() - timedelta(days=2)
        )

        # Create new log, triggering auto-cleanup
        self._create_log_entry()

        # Only one (new) log should remain
        self.assertEqual(WebhookDeliveryLog.objects.count(), 1)

    @override_settings(WEBHOOK_SUBSCRIBER={'AUTO_CLEANUP': False})
    def test_auto_cleanup_respects_setting(self):
        self._create_log_entry(created_at=timezone.now() - timedelta(days=40))
        self._create_log_entry(created_at=timezone.now())

        # Cleanup should not run because AUTO_CLEANUP is False
        self.assertEqual(WebhookDeliveryLog.objects.count(), 2)

    def test_auto_cleanup_respects_setting_default_values(self):
        self._create_log_entry(created_at=timezone.now() - timedelta(days=40))
        self._create_log_entry(created_at=timezone.now())

        # Cleanup should have run because AUTO_CLEANUP is True
        self.assertEqual(WebhookDeliveryLog.objects.count(), 1)
