from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django_webhook_subscriber.models import WebhookRegistry
from django_webhook_subscriber.tasks import (
    async_deliver_webhook,
    process_webhook_batch,
)


class AsyncWebhookTaskTests(TestCase):
    def setUp(self):
        # Create a content type for the User model
        self.example_content_type = ContentType.objects.get_for_model(User)

        # Create test webhooks
        self.webhook = WebhookRegistry.objects.create(
            name='Test Webhook',
            content_type=self.example_content_type,
            event_signals=['CREATE', 'UPDATE'],
            endpoint='https://example.com/webhook',
            secret='test-secret-key',
        )

        # Create test payload
        self.payload = {
            'pk': 1,
            'model': 'auth.user',
            'event_signal': 'created',
            'fields': {'username': 'testuser', 'email': 'test@example.com'},
        }

        self.event_signal = 'created'

    @patch('django_webhook_subscriber.delivery.deliver_webhook')
    def test_async_deliver_webhook_success(self, mock_deliver):
        # Mock delivery to return a log object
        mock_log = MagicMock(id=1)
        mock_deliver.return_value = mock_log

        # Call the task function
        result = async_deliver_webhook(
            self.webhook.id, self.payload, self.event_signal
        )

        # Verify the delivery was attempted
        mock_deliver.assert_called_once_with(
            self.webhook,
            self.payload,
            self.event_signal,
        )

        # Verify the result is the log object
        self.assertEqual(result, 1)

    @patch('django_webhook_subscriber.delivery.deliver_webhook')
    def test_async_deliver_inactive_webhook(self, mock_deliver):
        # Set webhook to inactive
        self.webhook.is_active = False
        self.webhook.save()

        # Call the task function
        result = async_deliver_webhook(
            self.webhook.id,
            self.payload,
            self.event_signal,
        )

        # Verify no delivery was attempted
        mock_deliver.assert_not_called()

        # Verify the result is None
        self.assertIsNone(result)

    @patch('django_webhook_subscriber.delivery.deliver_webhook')
    def test_async_deliver_nonexistent_webhook(self, mock_deliver):
        # Use a non-existent webhook ID
        non_existent_id = 999

        # Call the task function
        result = async_deliver_webhook(
            non_existent_id,
            self.payload,
            self.event_signal,
        )

        # Verify no delivery was attempted
        mock_deliver.assert_not_called()

        # Verify the result is None
        self.assertIsNone(result)

    @patch('django_webhook_subscriber.tasks.async_deliver_webhook')
    def test_process_webhook_batch(self, mock_async_task):
        # Create a second webhook
        second_webhook = WebhookRegistry.objects.create(
            name='Second Webhook',
            content_type=self.example_content_type,
            event_signals=['CREATE'],
            endpoint='https://example2.com/webhook',
            secret='test-secret-key-2',
        )

        # Mock the group object and its apply_async method
        mock_group = MagicMock()
        mock_group.apply_async.return_value = 'group-result'

        # Create a mock for the signature function returned by .s()
        mock_signature = MagicMock()
        mock_async_task.s.return_value = mock_signature

        # Mock the group constructor
        with patch(
            'celery.group', return_value=mock_group
        ) as mock_group_constructor:
            # Call the batch processing task
            webhook_ids = [self.webhook.id, second_webhook.id]
            result = process_webhook_batch(
                webhook_ids,
                self.payload,
                self.event_signal,
            )

            # Verify signatures were created for each webhook
            self.assertEqual(mock_async_task.s.call_count, 2)

            # Verify the group was created with the signatures
            mock_group_constructor.assert_called_once()
            args = mock_group_constructor.call_args[0][0]
            self.assertEqual(len(args), 2)
            self.assertEqual(args[0], mock_signature)
            self.assertEqual(args[1], mock_signature)

            # Verify apply_async was called
            mock_group.apply_async.assert_called_once()

            # Verify the result is the group result
            self.assertEqual(result, 'group-result')

    @patch('django_webhook_subscriber.tasks.async_deliver_webhook')
    def test_process_webhook_batch_empty(self, mock_async_task):
        # Mock the group constructor
        with patch('celery.group') as mock_group_constructor:
            # Call with empty webhook IDs
            result = process_webhook_batch([], self.payload, self.event_signal)

            # Verify no signatures were created
            mock_async_task.s.assert_not_called()

            # Verify no group was created
            mock_group_constructor.assert_not_called()

            # Verify the result is None
            self.assertIsNone(result)

    @patch('django_webhook_subscriber.tasks.async_deliver_webhook')
    def test_process_webhook_batch_integration(self, mock_async_task):
        # Create multiple test webhooks
        webhooks = [
            self.webhook,  # Already created in setUp
            WebhookRegistry.objects.create(
                name='Second Webhook',
                content_type=self.example_content_type,
                event_signals=['CREATE'],
                endpoint='https://example2.com/webhook',
                secret='test-secret-key-2',
            ),
            WebhookRegistry.objects.create(
                name='Third Webhook',
                content_type=self.example_content_type,
                event_signals=['UPDATE'],  # Doesn't match our test event
                endpoint='https://example3.com/webhook',
                secret='test-secret-key-3',
            ),
            WebhookRegistry.objects.create(
                name='Inactive Webhook',
                content_type=self.example_content_type,
                event_signals=['CREATE'],
                endpoint='https://example4.com/webhook',
                secret='test-secret-key-4',
                is_active=False,
            ),
        ]

        # Mock the signature function
        mock_signature = MagicMock()
        mock_async_task.s.return_value = mock_signature

        # Mock the group and its apply_async
        mock_group_result = MagicMock()
        mock_group = MagicMock()
        mock_group.apply_async.return_value = mock_group_result

        # Run the test
        with patch('celery.group', return_value=mock_group):
            # Get IDs of all webhooks
            webhook_ids = [webhook.id for webhook in webhooks]

            # Call the batch function
            result = process_webhook_batch(
                webhook_ids, self.payload, self.event_signal
            )

            # Verify the result matches the expected group result
            self.assertEqual(result, mock_group_result)

            # Verify signatures were created for each webhook
            self.assertEqual(mock_async_task.s.call_count, len(webhook_ids))

            # Verify the correct arguments were passed to each signature
            calls = mock_async_task.s.call_args_list
            for i, call in enumerate(calls):
                args = call[0]
                self.assertEqual(args[0], webhook_ids[i])
                self.assertEqual(args[1], self.payload)
                self.assertEqual(args[2], self.event_signal)
