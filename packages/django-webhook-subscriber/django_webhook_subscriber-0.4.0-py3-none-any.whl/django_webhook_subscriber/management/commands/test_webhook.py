"""Test a webhook by sending a test payload to the specified endpoint."""

import json

from django.core.management.base import BaseCommand, CommandError

from django_webhook_subscriber.delivery import deliver_webhook


class Command(BaseCommand):
    """Test a webhook by sending a test payload to the specified endpoint.

    This command sends a test payload to the specified webhook endpoint
    and displays the response status and body. It can be used to verify
    that the webhook is correctly configured and that the endpoint is
    reachable.

    Usage:
        python manage.py test_webhook <webhook_id> --event <event_signal>
        python manage.py test_webhook <webhook_id> --payload <custom_payload>
    """

    help = 'Test a webhook by sending a test payload'

    def add_arguments(self, parser):
        parser.add_argument(
            'webhook_id', type=int, help='The ID of the webhook to test'
        )
        parser.add_argument(
            '--event',
            type=str,
            default='test',
            help='Event type to use (test, created, updated, deleted)',
        )
        parser.add_argument(
            '--payload',
            type=str,
            help='Custom payload to send (as JSON string)',
        )

    def handle(self, *args, **options):
        webhook_id = options['webhook_id']
        event_signal = options['event']
        custom_payload = options['payload']

        from django_webhook_subscriber.models import WebhookRegistry

        try:
            webhook = WebhookRegistry.objects.get(pk=webhook_id)
        except WebhookRegistry.DoesNotExist:
            raise CommandError(f'Webhook with ID {webhook_id} does not exist')

        # Prepare payload
        if custom_payload:
            try:
                # Use provided payload
                payload = custom_payload
                # Validate it's valid JSON
                json.loads(payload)
            except json.JSONDecodeError:
                raise CommandError('The provided payload is not valid JSON')
        else:
            # Generate a test payload
            model_name = webhook.content_type.model
            app_label = webhook.content_type.app_label

            payload = json.dumps(
                {
                    'event': event_signal,
                    'model': f'{app_label}.{model_name}',
                    'test': True,
                    'message': f'Test webhook for {webhook.name}',
                }
            )

        # Deliver the webhook
        self.stdout.write(f'Sending test webhook to {webhook.endpoint}...')
        log = deliver_webhook(webhook, payload, event_signal)

        # Display results
        if log.error_message:
            self.stdout.write(self.style.ERROR(f'Error: {log.error_message}'))
        elif log.response_status and 200 <= log.response_status < 300:
            self.stdout.write(
                self.style.SUCCESS(
                    f'Success! Status code: {log.response_status}'
                )
            )
            self.stdout.write(f'Response: {log.response_body}')
        else:
            self.stdout.write(
                self.style.WARNING(
                    f'Received status code: {log.response_status}'
                )
            )
            self.stdout.write(f'Response: {log.response_body}')
