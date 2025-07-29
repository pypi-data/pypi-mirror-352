from django.test import TestCase
from django.contrib.contenttypes.models import ContentType

from rest_framework import serializers

from django_webhook_subscriber.serializers import serialize_instance
from django_webhook_subscriber.models import WebhookRegistry


class SerializersTests(TestCase):
    def setUp(self):
        self.webhook_content_type = ContentType.objects.get_for_model(
            WebhookRegistry
        )
        # creating a user instance
        self.webhook = WebhookRegistry.objects.create(
            name='Test Webhook',
            content_type=self.webhook_content_type,
            endpoint='https://example.com/webhook',
        )

    def test_default_serialization(self):
        # serializing the user instance
        data = serialize_instance(self.webhook, 'create')

        # Check that structure is correct
        self.assertEqual(data['pk'], self.webhook.pk)
        self.assertEqual(
            data['source'], 'django_webhook_subscriber.webhookregistry'
        )
        self.assertEqual(data['event_signal'], 'create')
        self.assertIn('fields', data)

        # Check that all fields are serialized
        self.assertEqual(data['fields']['name'], 'Test Webhook')
        self.assertEqual(
            data['fields']['endpoint'],
            'https://example.com/webhook',
        )
        self.assertEqual(
            data['fields']['content_type'],
            self.webhook_content_type.pk,
        )

    def test_serialization_with_custom_serializer(self):
        class CustomSerializer(serializers.ModelSerializer):
            class Meta:
                model = WebhookRegistry
                fields = ['endpoint', 'name']

        # Test with DRF serializer
        data = serialize_instance(
            self.webhook,
            event_signal='delete',
            field_serializer=CustomSerializer,
        )

        # Check the structure
        self.assertEqual(data['pk'], self.webhook.pk)
        self.assertEqual(
            data['source'], 'django_webhook_subscriber.webhookregistry'
        )
        self.assertEqual(data['event_signal'], 'delete')
        self.assertIn('fields', data)

        # Check the fields
        self.assertEqual(data['fields']['name'], 'Test Webhook')
        self.assertEqual(
            data['fields']['endpoint'],
            'https://example.com/webhook',
        )
        self.assertNotIn('content_type', data['fields'])

    def test_serialization_with_invalid_serializer(self):
        class InvalidSerializer:
            pass

        # Test with invalid serializer
        msg = (
            'field_serializer must be a subclass of rest_framework.Serializer'
        )
        with self.assertRaisesMessage(ValueError, msg):
            serialize_instance(
                self.webhook,
                event_signal='create',
                field_serializer=InvalidSerializer,
            )
