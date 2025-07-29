"""Clean up old webhook delivery logs."""

from django.core.management.base import BaseCommand
from django.utils import timezone
from django.conf import settings
from datetime import timedelta


class Command(BaseCommand):
    """Clean up old webhook delivery logs.

    This command deletes webhook delivery logs older than a specified
    number of days. If no number of days is specified, it defaults to
    the value set in the WEBHOOK_SUBSCRIBER_LOG_RETENTION_DAYS setting.

    Usage:
        python manage.py clean_webhook_logs --days 30
        python manage.py clean_webhook_logs --dry-run
    """

    help = 'Clean up old webhook delivery logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Delete logs older than this many days',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Only print what would be deleted without actually deleting',
        )

    def handle(self, *args, **options):
        # Get retention period from command line or settings
        days = options['days']
        if days is None:
            days = getattr(
                settings, 'WEBHOOK_SUBSCRIBER_LOG_RETENTION_DAYS', 30
            )

        # Calculate cutoff date
        cutoff_date = timezone.now() - timedelta(days=days)

        # Get logs to delete
        from django_webhook_subscriber.models import WebhookDeliveryLog

        logs_to_delete = WebhookDeliveryLog.objects.filter(
            created_at__lt=cutoff_date
        )
        count = logs_to_delete.count()

        if options['dry_run']:
            self.stdout.write(
                f'Would delete {count} logs older than {cutoff_date}'
            )
        else:
            logs_to_delete.delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f'Deleted {count} logs older than {cutoff_date}'
                )
            )
