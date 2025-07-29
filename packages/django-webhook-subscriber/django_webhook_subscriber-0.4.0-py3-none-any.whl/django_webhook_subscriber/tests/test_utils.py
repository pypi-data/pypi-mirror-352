from unittest.mock import patch

from django.test import TestCase, override_settings
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType

from django_webhook_subscriber.models import WebhookRegistry
from django_webhook_subscriber.signals import register_webhook_signals
from django_webhook_subscriber.utils import (
    register_model_config,
    get_webhook_config,
    unregister_webhook_signals,
)


class WebhookRegistrationTests(TestCase):
    def test_register_model_config(self):

        # Register the User model with a serializer and events
        config = register_model_config(
            User,
            serializer='UserSerializer',
            events=['CREATE', 'UPDATE'],
        )

        # Check if the configuration is stored correctly
        self.assertEqual(config['serializer'], 'UserSerializer')
        self.assertEqual(config['events'], ['CREATE', 'UPDATE'])

    def test_register_model_config_default(self):

        # Register the User model with a serializer and events
        config = register_model_config(User)

        # Check if the configuration is stored correctly
        self.assertIsNone(config['serializer'])
        self.assertEqual(config['events'], ['CREATE', 'UPDATE', 'DELETE'])

    def test_get_webhook_config(self):
        # Register the User model with a serializer and events
        register_model_config(User, events=['CREATE', 'UPDATE'])

        # Retrieve the configuration for the User model
        config = get_webhook_config(User)
        self.assertIsNotNone(config)
        config = get_webhook_config('other_model')
        self.assertIsNone(config)

    @override_settings(WEBHOOK_SUBSCRIBER_MODELS={'auth.User': {}})
    @patch('django_webhook_subscriber.signals.process_webhook_event')
    def test_unregister_webhook_signals(self, mock_delivery):
        register_webhook_signals(WebhookRegistry)
        register_webhook_signals(User)

        # Disable all webhooks
        unregister_webhook_signals()

        # creating a user
        user = User.objects.create(username='testuser')
        mock_delivery.assert_not_called()

        # updating the user
        user.save()
        mock_delivery.assert_not_called()

        # deleting the user
        user.delete()
        mock_delivery.assert_not_called()

        # creating a webhook delivery log
        WebhookRegistry.objects.create(
            name='Test Webhook',
            content_type=ContentType.objects.get_for_model(User),
            event_signals=['CREATE', 'UPDATE'],
            endpoint='http://example.com/webhook/',
        )
        mock_delivery.assert_not_called()

    @override_settings(WEBHOOK_SUBSCRIBER_MODELS={'auth.User': {}})
    @patch('django_webhook_subscriber.signals.process_webhook_event')
    def test_unregister_webhook_signals_specific_model(self, mock_delivery):
        register_webhook_signals(User)
        register_webhook_signals(WebhookRegistry)

        # Disable all webhooks
        unregister_webhook_signals(model_class=User)

        # creating a user
        user = User.objects.create(username='testuser')
        mock_delivery.assert_not_called()

        # updating the user
        user.save()
        mock_delivery.assert_not_called()

        # deleting the user
        user.delete()
        mock_delivery.assert_not_called()

        # creating a webhook delivery log
        WebhookRegistry.objects.create(
            name='Test Webhook',
            content_type=ContentType.objects.get_for_model(User),
            event_signals=['CREATE', 'UPDATE'],
            endpoint='http://example.com/webhook/',
        )
        # Verify that the webhook delivery log signal is still connected
        mock_delivery.assert_called()
