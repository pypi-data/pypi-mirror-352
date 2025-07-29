from unittest.mock import patch

# from django.contrib.auth.models import Group, User
from django.test import TestCase, override_settings
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from django_webhook_subscriber.utils import _webhook_registry
from django_webhook_subscriber.models import (
    WebhookDeliveryLog,
    WebhookRegistry,
)
from django_webhook_subscriber.signals import (
    register_webhook_signals,
    register_webhooks_from_settings,
    process_webhook_event,
    webhook_post_delete,
    webhook_post_save,
)


class CustomSerializer(serializers.Serializer):
    pass


class SignalTests(TestCase):
    def setUp(self):
        # Clear the registry before each test
        _webhook_registry.clear()

    @patch('django.db.models.signals.post_save.connect')
    @patch('django.db.models.signals.post_delete.connect')
    def test_register_all_events(self, mock_post_delete, mock_post_save):
        # Register with default (all) events
        register_webhook_signals(WebhookDeliveryLog)

        # Verify signals were connected
        mock_post_save.assert_called_once_with(
            webhook_post_save,
            sender=WebhookDeliveryLog,
            dispatch_uid=f'webhook_post_save_{WebhookDeliveryLog.__name__}',
        )
        mock_post_delete.assert_called_once_with(
            webhook_post_delete,
            sender=WebhookDeliveryLog,
            dispatch_uid=f'webhook_post_delete_{WebhookDeliveryLog.__name__}',
        )

        # Verify registry entry
        self.assertIn(WebhookDeliveryLog, _webhook_registry)
        self.assertIsNone(_webhook_registry[WebhookDeliveryLog]['serializer'])
        self.assertEqual(
            _webhook_registry[WebhookDeliveryLog]['events'],
            ['CREATE', 'UPDATE', 'DELETE'],
        )

    @patch('django.db.models.signals.post_save.connect')
    @patch('django.db.models.signals.post_delete.connect')
    def test_register_specific_events(self, mock_post_delete, mock_post_save):

        # Register with default (all) events
        register_webhook_signals(
            WebhookDeliveryLog,
            events=['create', 'update'],
            serializer=CustomSerializer,
        )

        # asserting that signals were connected
        mock_post_save.assert_called_once_with(
            webhook_post_save,
            sender=WebhookDeliveryLog,
            dispatch_uid=f'webhook_post_save_{WebhookDeliveryLog.__name__}',
        )
        mock_post_delete.assert_not_called()

        # asserting that user was added to _webhook_registry
        self.assertIn(WebhookDeliveryLog, _webhook_registry)
        # asserting custom values
        self.assertEqual(
            _webhook_registry[WebhookDeliveryLog]['serializer'],
            CustomSerializer,
        )
        self.assertEqual(
            _webhook_registry[WebhookDeliveryLog]['events'],
            ['CREATE', 'UPDATE'],
        )

    @override_settings(
        WEBHOOK_SUBSCRIBER={
            'WEBHOOK_MODELS': {
                'django_webhook_subscriber.WebhookDeliveryLog': {},
                'django_webhook_subscriber.WebhookRegistry': {
                    'serializer': (
                        'django_webhook_subscriber.tests.test_signals.'
                        'CustomSerializer'
                    ),
                    'events': ['CREATE', 'UPDATE'],
                },
            }
        }
    )
    @patch('django_webhook_subscriber.signals.register_webhook_signals')
    def test_register_from_settings(self, mock_register):
        # Register webhooks from settings
        register_webhooks_from_settings()

        # Verify register_webhook_signals was called with correct arguments
        self.assertEqual(mock_register.call_count, 2)
        mock_register.assert_called()
        mock_register.assert_called()
        call_args_list = mock_register.call_args_list

        # Check the first webhook model (Default values)
        args, kwargs = call_args_list[0]
        self.assertEqual(args[0], WebhookDeliveryLog)
        self.assertIsNone(kwargs['serializer'])
        self.assertEqual(kwargs['events'], None)

        # Check the second webhook model (Custom values)
        args, kwargs = call_args_list[1]
        self.assertEqual(args[0], WebhookRegistry)
        self.assertEqual(kwargs['serializer'], CustomSerializer)
        self.assertEqual(kwargs['events'], ['CREATE', 'UPDATE'])

    @override_settings(
        WEBHOOK_SUBSCRIBER={'WEBHOOK_MODELS': {'invalid.Model': {}}}
    )
    @patch('django_webhook_subscriber.signals.register_webhook_signals')
    def test_register_from_settings_invalid_model(self, mock_register):
        # Register webhooks from settings
        register_webhooks_from_settings()

        # Verify register_webhook_signals was not called
        mock_register.assert_not_called()

    @override_settings(
        WEBHOOK_SUBSCRIBER={
            'WEBHOOK_MODELS': {
                'django_webhook_subscriber.WebhookDeliveryLog': {
                    'serializer': 'invalid.Serializer'
                }
            }
        }
    )
    @patch('django_webhook_subscriber.signals.register_webhook_signals')
    def test_register_from_settings_invalid_serializer(self, mock_register):
        # Register webhooks from settings
        register_webhooks_from_settings()

        # Verify register_webhook_signals was not called
        mock_register.assert_called()
        args, kwargs = mock_register.call_args

        # Check the first webhook model (Default values)
        self.assertEqual(args[0], WebhookDeliveryLog)
        self.assertIsNone(kwargs['serializer'])
        self.assertEqual(kwargs['events'], None)

    @patch('django_webhook_subscriber.signals.register_webhook_signals')
    def test_register_from_settings_no_webhooks(self, mock_register):
        # Register webhooks from settings
        register_webhooks_from_settings()

        # Verify register_webhook_signals was not called
        mock_register.assert_not_called()

    @patch('django_webhook_subscriber.signals.process_and_deliver_webhook')
    @patch('django_webhook_subscriber.signals.serialize_instance')
    def test_process_webhook_event(self, mock_serializer, mock_delivery):
        event_signal = 'created'
        content_type = ContentType.objects.get_for_model(WebhookRegistry)
        instance = WebhookRegistry.objects.create(
            name='Test Webhook',
            endpoint='https://example.com/webhook',
            content_type=content_type,
        )

        # Register signals for the WebhookRegistry model
        register_webhook_signals(WebhookRegistry)

        # Mock the serializer to return a specific payload
        mock_serializer.return_value = 'serialized_data'

        # Call the function to process the webhook event
        process_webhook_event(instance=instance, event_signal=event_signal)

        # Check if mock_delivery was called
        mock_delivery.assert_called_once()

        # Get the call arguments
        args, kwargs = mock_delivery.call_args

        # Check the arguments
        self.assertEqual(args[0], instance)
        self.assertEqual(args[1], event_signal)
        self.assertEqual(kwargs['serialized_payload'], 'serialized_data')

    @patch('django_webhook_subscriber.delivery.process_and_deliver_webhook')
    def test_process_webhook_event_webhook_configurations(self, mock_delivery):
        event_signal = 'created'
        content_type = ContentType.objects.get_for_model(WebhookRegistry)
        instance = WebhookRegistry.objects.create(
            name='Test Webhook',
            endpoint='https://example.com/webhook',
            content_type=content_type,
        )

        # Call the function to process the webhook event
        process_webhook_event(instance=instance, event_signal=event_signal)

        mock_delivery.assert_not_called()

    @patch('django_webhook_subscriber.signals.process_webhook_event')
    def test_post_save_signal_create(self, mock_process):
        # Register signals for the WebhookRegistry model
        register_webhook_signals(WebhookRegistry)

        content_type = ContentType.objects.get_for_model(WebhookRegistry)
        webhook = WebhookRegistry.objects.create(
            name='Test Webhook',
            endpoint='https://example.com/webhook',
            content_type=content_type,
        )

        mock_process.assert_called_once()
        _, kwargs = mock_process.call_args
        self.assertEqual(kwargs['instance'], webhook)
        self.assertEqual(kwargs['event_signal'], 'created')

    @patch('django_webhook_subscriber.signals.process_webhook_event')
    def test_post_save_signal_update(self, mock_process):
        # Register signals for the WebhookRegistry model
        register_webhook_signals(WebhookRegistry)

        content_type = ContentType.objects.get_for_model(WebhookRegistry)
        webhook = WebhookRegistry.objects.create(
            name='Test Webhook',
            endpoint='https://example.com/webhook',
            content_type=content_type,
        )

        mock_process.reset_mock()
        webhook.name = 'Test'
        webhook.save()
        mock_process.assert_called_once()
        _, kwargs = mock_process.call_args
        self.assertEqual(kwargs['instance'], webhook)
        self.assertEqual(kwargs['event_signal'], 'updated')

    @patch('django_webhook_subscriber.signals.process_webhook_event')
    def test_post_delete_signal(self, mock_process):
        # Register signals for the WebhookRegistry model
        register_webhook_signals(WebhookRegistry)

        content_type = ContentType.objects.get_for_model(WebhookRegistry)
        webhook = WebhookRegistry.objects.create(
            name='Test Webhook',
            endpoint='https://example.com/webhook',
            content_type=content_type,
        )

        mock_process.reset_mock()
        webhook.delete()
        mock_process.assert_called_once()
        args, kwargs = mock_process.call_args
        self.assertEqual(kwargs['instance'].__class__, WebhookRegistry)
        self.assertEqual(kwargs['event_signal'], 'deleted')
