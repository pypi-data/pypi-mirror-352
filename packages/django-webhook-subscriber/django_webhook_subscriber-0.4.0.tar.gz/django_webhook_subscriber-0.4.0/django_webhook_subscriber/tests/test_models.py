from django.test import TestCase
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.contrib.auth.models import User

from django_webhook_subscriber import models


class WebhookModelTests(TestCase):

    def setUp(self):
        # Get content type for User model for testing
        self.user_content_type = ContentType.objects.get_for_model(User)

        # Create a basic webhook for testing
        self.webhook = models.WebhookRegistry.objects.create(
            name='Test Webhook',
            content_type=self.user_content_type,
            endpoint='https://example.com/webhook',
        )

    def test_webhook_creation(self):
        self.assertEqual(self.webhook.name, 'Test Webhook')
        self.assertEqual(self.webhook.content_type, self.user_content_type)
        self.assertEqual(self.webhook.endpoint, 'https://example.com/webhook')
        self.assertEqual(self.webhook.event_signals, [])
        self.assertTrue(self.webhook.is_active)
        self.assertTrue(self.webhook.secret)
        self.assertEqual(self.webhook.headers, {})

    def test_webhook_string_representation(self):
        self.assertEqual(
            str(self.webhook), 'Test Webhook - https://example.com/webhook'
        )

    def test_webhook_with_headers(self):
        custom_headers = {'Authorization': 'Bearer token123'}
        webhook = models.WebhookRegistry.objects.create(
            name='Webhook with Headers',
            content_type=self.user_content_type,
            event_signals=['DELETE'],
            endpoint='https://example.com/webhook2',
            headers=custom_headers,
        )
        self.assertEqual(webhook.headers, custom_headers)

    def test_event_signals_jsonfield(self):
        # Test with a single event type
        webhook = models.WebhookRegistry.objects.create(
            name='Single Event Webhook',
            content_type=self.user_content_type,
            event_signals=['CREATE'],
            endpoint='https://example.com/create-only',
        )
        self.assertEqual(webhook.event_signals, ['CREATE'])

        # Test with multiple event types
        webhook = models.WebhookRegistry.objects.create(
            name='All Events Webhook',
            content_type=self.user_content_type,
            event_signals=['CREATE', 'UPDATE', 'DELETE'],
            endpoint='https://example.com/all-events',
        )
        self.assertEqual(webhook.event_signals, ['CREATE', 'UPDATE', 'DELETE'])

        # Test with empty list (should use default)
        webhook = models.WebhookRegistry.objects.create(
            name='Empty Events Webhook',
            content_type=self.user_content_type,
            endpoint='https://example.com/no-events',
        )
        self.assertEqual(webhook.event_signals, [])

    def test_updating_webhook(self):
        # Update several fields
        self.webhook.name = 'Updated Webhook'
        self.webhook.endpoint = 'https://updated-example.com/webhook'
        self.webhook.event_signals = ['CREATE', 'UPDATE']
        self.webhook.is_active = False
        self.webhook.save()

        # Retrieve the webhook from the database again to verify updates
        updated_webhook = models.WebhookRegistry.objects.get(
            pk=self.webhook.pk
        )

        self.assertEqual(updated_webhook.name, 'Updated Webhook')
        self.assertEqual(
            updated_webhook.endpoint,
            'https://updated-example.com/webhook',
        )
        self.assertEqual(
            updated_webhook.event_signals,
            ['CREATE', 'UPDATE'],
        )
        self.assertFalse(updated_webhook.is_active)

    def test_tracking_fields(self):
        # Initially, tracking fields should be None
        self.assertTrue(self.webhook.keep_last_response)
        self.assertIsNone(self.webhook.last_response)
        self.assertIsNone(self.webhook.last_success)
        self.assertIsNone(self.webhook.last_failure)

        # Update tracking fields
        now = timezone.now()
        self.webhook.last_response = 'Success: 200 OK'
        self.webhook.last_success = now
        self.webhook.save()

        # Retrieve the webhook and verify updates
        updated_webhook = models.WebhookRegistry.objects.get(
            pk=self.webhook.pk
        )
        self.assertEqual(updated_webhook.last_response, 'Success: 200 OK')
        self.assertEqual(updated_webhook.last_success.date(), now.date())
        self.assertIsNone(updated_webhook.last_failure)

        # Update failure tracking
        self.webhook.last_response = 'Error: 500 Internal Server Error'
        self.webhook.last_failure = now
        self.webhook.save()

        # Retrieve and verify again
        updated_webhook = models.WebhookRegistry.objects.get(
            pk=self.webhook.pk
        )
        self.assertEqual(
            updated_webhook.last_response,
            'Error: 500 Internal Server Error',
        )
        self.assertEqual(updated_webhook.last_failure.date(), now.date())

    def test_async_delivery_settings(self):
        # Default values
        self.assertEqual(self.webhook.max_retries, 3)
        self.assertEqual(self.webhook.retry_delay, 60)
        self.assertIsNone(self.webhook.use_async)

        # Update async settings
        self.webhook.max_retries = 5
        self.webhook.retry_delay = 120
        self.webhook.use_async = True
        self.webhook.save()

        # Retrieve and verify
        updated_webhook = models.WebhookRegistry.objects.get(
            pk=self.webhook.pk
        )
        self.assertEqual(updated_webhook.max_retries, 5)
        self.assertEqual(updated_webhook.retry_delay, 120)
        self.assertTrue(updated_webhook.use_async)


class WebhookDeliveryLogModelTests(TestCase):
    def setUp(self):
        # Get content type for User model for testing
        self.user_content_type = ContentType.objects.get_for_model(User)

        # Create a webhook for testing
        self.webhook = models.WebhookRegistry.objects.create(
            name='Test Webhook',
            content_type=self.user_content_type,
            event_signals=['CREATE', 'UPDATE'],
            endpoint='https://example.com/webhook',
        )

        # Create a successful log entry
        self.success_log = models.WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal='created',
            payload={'id': 1, 'username': 'testuser', 'event': 'created'},
            response_status=200,
            response_body='OK',
        )

        # Create a failed log entry
        self.failed_log = models.WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal='updated',
            payload={'id': 1, 'username': 'testuser', 'event': 'updated'},
            response_status=500,
            response_body='Internal Server Error',
            error_message='Server returned 500 status code',
        )

    def test_log_creation(self):
        # Verify the successful log entry
        self.assertEqual(self.success_log.webhook, self.webhook)
        self.assertEqual(self.success_log.event_signal, 'created')
        self.assertEqual(self.success_log.payload['username'], 'testuser')
        self.assertEqual(self.success_log.response_status, 200)
        self.assertEqual(self.success_log.response_body, 'OK')
        self.assertIsNone(self.success_log.error_message)

        # Verify the failed log entry
        self.assertEqual(self.failed_log.webhook, self.webhook)
        self.assertEqual(self.failed_log.event_signal, 'updated')
        self.assertEqual(self.failed_log.payload['username'], 'testuser')
        self.assertEqual(self.failed_log.response_status, 500)
        self.assertEqual(
            self.failed_log.response_body,
            'Internal Server Error',
        )
        self.assertEqual(
            self.failed_log.error_message,
            'Server returned 500 status code',
        )

    def test_string_representation(self):
        # For successful delivery
        expected_success_str = (
            f'{self.webhook} - {self.success_log.event_signal} - 200'
        )
        self.assertEqual(str(self.success_log), expected_success_str)

        # For failed delivery
        expected_failed_str = (
            f'{self.webhook} - {self.failed_log.event_signal} - 500'
        )
        self.assertEqual(str(self.failed_log), expected_failed_str)

        # For log with no status (completely failed)
        no_status_log = models.WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal='deleted',
            payload={'id': 1, 'username': 'testuser', 'event': 'deleted'},
            error_message='Connection refused',
        )
        expected_no_status_str = (
            f'{self.webhook} - {no_status_log.event_signal} - Failed'
        )
        self.assertEqual(str(no_status_log), expected_no_status_str)

    def test_json_payload_handling(self):
        # Test with an empty payload
        empty_payload_log = models.WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal='updated',
            payload={},
            response_status=200,
        )
        self.assertEqual(empty_payload_log.payload, {})

        # Test with a nested payload
        nested_payload_log = models.WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal='created',
            payload={
                'user': {
                    'id': 5,
                    'username': 'nesteduser',
                    'profile': {'age': 30, 'interests': ['python', 'django']},
                },
                'timestamp': '2023-01-01T12:00:00Z',
            },
            response_status=200,
        )

        # Verify nested data is preserved
        payload = nested_payload_log.payload
        self.assertEqual(payload['user']['username'], 'nesteduser')
        self.assertEqual(payload['user']['profile']['age'], 30)
        self.assertEqual(payload['user']['profile']['interests'][0], 'python')

        # Test with array in payload
        array_payload_log = models.WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal='created',
            payload=[
                {'id': 1, 'name': 'Item 1'},
                {'id': 2, 'name': 'Item 2'},
                {'id': 3, 'name': 'Item 3'},
            ],
            response_status=200,
        )

        # Verify array is preserved
        payload = array_payload_log.payload
        self.assertEqual(len(payload), 3)
        self.assertEqual(payload[0]['name'], 'Item 1')
        self.assertEqual(payload[2]['id'], 3)

    def test_multiple_logs_for_webhook(self):
        # Create several more logs for the same webhook
        for i in range(5):
            models.WebhookDeliveryLog.objects.create(
                webhook=self.webhook,
                event_signal='created',
                payload={'id': i + 10, 'name': f'User {i}'},
                response_status=200,
            )

        # Verify through the related_name
        webhook_logs = self.webhook.delivery_logs.all()

        # Should have 7 logs total (2 from setUp + 5 new ones)
        self.assertEqual(webhook_logs.count(), 7)

        # Verify newest log is first in the queryset
        self.assertEqual(webhook_logs.first().payload['id'], 14)
