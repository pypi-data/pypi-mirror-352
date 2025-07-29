"""Check the status of recent webhook deliveries."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q


class Command(BaseCommand):
    """Check the status of recent webhook deliveries.

    This command checks the status of recent webhook deliveries and
    provides a summary of successful and failed deliveries. It can be
    filtered to show only failed deliveries or all deliveries within a
    specified time period.

    Usage:
        python manage.py check_webhook_tasks --hours 24
        python manage.py check_webhook_tasks --failed-only
        python manage.py check_webhook_tasks --hours 48 --failed-only
    """

    help = 'Check status of recent webhook deliveries'

    def add_arguments(self, parser):
        parser.add_argument(
            '--hours',
            type=int,
            default=24,
            help='Hours to look back for delivery logs',
        )
        parser.add_argument(
            '--failed-only',
            action='store_true',
            help='Show only failed deliveries',
        )

    def handle(self, *args, **options):
        hours = options['hours']
        failed_only = options['failed_only']

        cutoff = timezone.now() - timezone.timedelta(hours=hours)

        from django_webhook_subscriber.models import WebhookRegistry

        # Get webhooks with delivery status
        webhooks = WebhookRegistry.objects.all()

        for webhook in webhooks:
            # Get recent delivery logs
            logs = webhook.delivery_logs.filter(created_at__gte=cutoff)

            if failed_only:
                logs = logs.filter(
                    Q(error_message__isnull=False)
                    | Q(response_status__lt=200)
                    | Q(response_status__gte=300)
                )

            if not logs.exists():
                if not failed_only:
                    self.stdout.write(f'Webhook: {webhook.name}')
                    self.stdout.write(
                        '  No deliveries in the specified time period.'
                    )
                continue
            self.stdout.write(f'Webhook: {webhook.name} ({webhook.endpoint})')
            self.stdout.write(f'  Total deliveries: {logs.count()}')

            # Count successes and failures
            successes = logs.filter(
                error_message__isnull=True,
                response_status__gte=200,
                response_status__lt=300,
            ).count()

            failures = logs.count() - successes

            if successes > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'  Successful: {successes}')
                )

            if failures > 0:
                self.stdout.write(self.style.ERROR(f'  Failed: {failures}'))

                # Show most recent failure
                if failures > 0:
                    most_recent = (
                        logs.filter(
                            Q(error_message__isnull=False)
                            | Q(response_status__lt=200)
                            | Q(response_status__gte=300)
                        )
                        .order_by('-created_at')
                        .first()
                    )

                    self.stdout.write(
                        f'  Most recent failure at: {most_recent.created_at}'
                    )
                    if most_recent.error_message:
                        self.stdout.write(
                            f'  Error: {most_recent.error_message}'
                        )
                    else:
                        self.stdout.write(
                            f'  Status: {most_recent.response_status}'
                        )
                        self.stdout.write(
                            f'  Response: {most_recent.response_body[:100]}...'
                        )

            self.stdout.write('')
