from unittest.mock import patch, MagicMock

from django.test import TestCase, override_settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from django_webhook_subscriber.models import (
    WebhookDeliveryLog,
    WebhookRegistry,
)
from django_webhook_subscriber.delivery import (
    get_webhook_for_model,
    process_and_deliver_webhook,
    prepare_headers,
    deliver_webhook,
)


@override_settings(WEBHOOK_SUBSCRIBER={'DEFAULT_USE_ASYNC': False})
class WebhookDeliveryTests(TestCase):
    def setUp(self):
        # Create a content type for the WebhookDeliveryLog model
        self.example_content_type = ContentType.objects.get_for_model(
            WebhookDeliveryLog
        )
        # Create test webhook registry
        self.webhook = WebhookRegistry.objects.create(
            name='Test Webhook',
            content_type=self.example_content_type,
            event_signals=['CREATE', 'UPDATE'],
            endpoint='http://example.com/webhook/',
            secret='test-secret-key',
        )

        # Create test log
        self.log = WebhookDeliveryLog.objects.create(
            webhook=self.webhook,
            event_signal='created',
            payload={'key': 'value'},
        )

    def test_get_webhook_for_model(self):
        # get_webhook for the model instance
        webhooks = get_webhook_for_model(self.log)
        self.assertEqual(len(webhooks), 1)
        self.assertEqual(webhooks[0], self.webhook)
        # get webhook for a different model instance
        user = User.objects.create(username='testuser')
        user_webhooks = get_webhook_for_model(user)
        self.assertEqual(len(user_webhooks), 0)

    def test_prepare_headers(self):
        headers = prepare_headers(self.webhook)
        self.assertEqual(headers['Content-Type'], 'application/json')
        self.assertEqual(headers['X-Secret'], 'test-secret-key')

    def test_prepare_headers_with_custom_headers(self):
        self.webhook.headers = {
            'X-Custom': 'custom-value',
            'Content-Type': 'text/plain',
        }
        self.webhook.save()

        headers = prepare_headers(self.webhook)
        self.assertEqual(headers['Content-Type'], 'text/plain')
        self.assertEqual(headers['X-Secret'], 'test-secret-key')
        self.assertEqual(headers['X-Custom'], 'custom-value')

    @patch('django_webhook_subscriber.delivery.deliver_webhook')
    def test_process_and_deliver_webhook(self, mock_deliver_webhook):
        # Create a second webhook with a non-matching event type
        non_matching_webhook = WebhookRegistry.objects.create(
            name='Non-Matching Webhook',
            content_type=self.example_content_type,
            event_signals=['DELETE'],
            endpoint='http://example.com/non-matching-webhook/',
            secret='non-matching-secret-key',
        )

        # Create a third webhook that is inactive
        inactive_webhook = WebhookRegistry.objects.create(
            name='Inactive Webhook',
            content_type=self.example_content_type,
            event_signals=['CREATE'],
            endpoint='http://example.com/inactive-webhook/',
            secret='inactive-secret-key',
            is_active=False,
        )

        # Call the function to process and deliver webhooks
        payload = {'key': 'value'}
        event_signal = 'created'
        process_and_deliver_webhook(self.log, event_signal, payload)

        # Verify that deliver_webhook was called only for the matching, active
        # webhook
        mock_deliver_webhook.assert_called_once_with(
            self.webhook,
            payload,
            event_signal,
        )

        # Ensure non-matching and inactive webhooks were not processed
        self.assertNotIn(
            non_matching_webhook, mock_deliver_webhook.call_args_list
        )
        self.assertNotIn(inactive_webhook, mock_deliver_webhook.call_args_list)

    @patch('requests.post')
    def test_deliver_webhook_success(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True  # TODO check without this
        mock_response.content = '{"status": "ok"}'
        mock_post.return_value = mock_response

        # Test delivery
        payload = {'key': 'value'}
        log = deliver_webhook(self.webhook, payload, 'created')

        # Verify the request was made properly
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(args[0], self.webhook.endpoint)
        self.assertEqual(kwargs['json'], payload)
        self.assertEqual(kwargs['headers']['X-Secret'], self.webhook.secret)

        # Verify log was created
        self.assertEqual(log.webhook, self.webhook)
        self.assertEqual(log.event_signal, 'created')
        self.assertEqual(log.response_status, 200)
        self.assertEqual(log.response_body, '{"status": "ok"}')

        # Verify the webhook was updated
        self.webhook.refresh_from_db()
        self.assertEqual(self.webhook.last_response, '{"status": "ok"}')
        self.assertIsNotNone(self.webhook.last_success)

    @patch('requests.post')
    def test_deliver_webhook_response_error(self, mock_post):
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 400
        mock_response.content = '{"status": "error"}'
        mock_post.return_value = mock_response

        # Test delivery
        payload = {'key': 'value'}
        log = deliver_webhook(self.webhook, payload, 'created')

        # Verify log was created
        self.assertEqual(log.webhook, self.webhook)
        self.assertEqual(log.event_signal, 'created')
        self.assertEqual(log.response_status, 400)
        self.assertEqual(log.response_body, '{"status": "error"}')

        # Verify the webhook was updated
        self.webhook.refresh_from_db()
        self.assertEqual(self.webhook.last_response, '{"status": "error"}')
        self.assertIsNotNone(self.webhook.last_failure)

    @patch('requests.post')
    def test_deliver_webhook_keep_response_false(self, mock_post):
        self.webhook.keep_last_response = False
        # Mock successful response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.ok = True  # TODO check without this
        mock_response.content = '{"status": "ok"}'
        mock_post.return_value = mock_response

        # Test delivery
        payload = {'key': 'value'}
        deliver_webhook(self.webhook, payload, 'created')

        # Verify the webhook was updated
        self.webhook.refresh_from_db()
        self.assertIsNone(self.webhook.last_response)
        self.assertIsNotNone(self.webhook.last_success)

    @patch('requests.post')
    def test_deliver_webhook_failure(self, mock_post):
        # Mock successful response
        mock_post.side_effect = Exception("Connection error")

        # Test delivery
        payload = {'key': 'value'}
        log = deliver_webhook(self.webhook, payload, 'created')

        # Verify log was created with error
        self.assertEqual(log.error_message, "Connection error")
        self.assertIsNone(log.response_status)

        # Verify webhook was updated
        self.webhook.refresh_from_db()
        self.assertIsNotNone(self.webhook.last_failure)
