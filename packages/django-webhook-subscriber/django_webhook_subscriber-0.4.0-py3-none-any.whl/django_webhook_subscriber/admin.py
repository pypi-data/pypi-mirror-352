"""Admin configuration for Django Webhook Subscriber."""

from django.contrib import admin
from django.forms import ModelForm
from django.utils.html import format_html
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from django_webhook_subscriber.models import (
    WebhookRegistry,
    WebhookDeliveryLog,
)
from django_webhook_subscriber.utils import _webhook_registry

# Limit the number of inline records to display
MAX_DISPLAYED_LOGS = 10


class WebhookRegistryDeliverLogInline(admin.TabularInline):
    """Inline admin for WebhookRegistryDeliveryLog model."""

    model = WebhookDeliveryLog
    extra = 0
    max_num = 10  # this doesn't limit the number of logs
    fields = ['created_at', 'event_signal', 'response_status', 'error_message']
    readonly_fields = [
        'created_at',
        'event_signal',
        'response_status',
        'error_message',
    ]
    can_delete = False
    verbose_name_plural = _('Recent Delivery Logs')

    def has_add_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        """Override get_queryset to limit the number of logs being
        displayed."""

        queryset = super().get_queryset(request)

        if not queryset.exists() or queryset.count() < MAX_DISPLAYED_LOGS:
            return queryset

        ids = queryset.order_by('-created_at').values('pk')[
            :MAX_DISPLAYED_LOGS
        ]

        qs = WebhookDeliveryLog.objects.filter(pk__in=ids).order_by('-id')
        return qs


class WebhookRegistryAdminForm(ModelForm):
    """Custom form for Webhook admin to validate allowed models for
    webhooks."""

    class Meta:
        model = WebhookRegistry
        fields = '__all__'

    def clean_content_type(self):
        content_type = self.cleaned_data.get('content_type')

        # If registry is empty, allow any content type
        if not _webhook_registry:
            return content_type

        # Check if model is registered in the webhook registry
        model_class = content_type.model_class()
        if model_class in _webhook_registry:
            return content_type

        # If model not found in registry, raise validation error
        raise ValidationError(
            _(
                'This model is not allowed for webhooks. Please add it to '
                'WEBHOOK_SUBSCRIBER["WEBHOOK_MODELS"] in settings.'
            )
        )

    def clean_event_signals(self):
        content_type = self.cleaned_data.get('content_type')
        event_signals = self.cleaned_data.get('event_signals')

        # If no event types are provided, raise a validation error
        if not event_signals:
            raise ValidationError(
                _('At least one event type must be selected.')
            )

        # Skip validation if content type is not valid
        if not content_type:
            return event_signals

        # Get model class and check registry
        model_class = content_type.model_class()
        if model_class not in _webhook_registry:
            # Skip validation if model not in registry
            return event_signals

        # Get allowed events for this model
        allowed_events = _webhook_registry[model_class].get('events', [])

        # Check if all selected event types are valid
        invalid_events = [e for e in event_signals if e not in allowed_events]
        if invalid_events:
            raise ValidationError(
                _(
                    'The following event types are not allowed for this model:'
                    ' %(events)s'
                )
                % {'events': ', '.join(invalid_events)}
            )

        return event_signals


@admin.register(WebhookRegistry)
class WebhookRegistryAdmin(admin.ModelAdmin):
    """Admin configuration for WebhookRegistry model."""

    form = WebhookRegistryAdminForm
    list_display = [
        'id',
        'name',
        'content_type',
        'event_signals_display',
        'endpoint',
        'is_active',
        'status_indicator',
        'webhooks_sent',
        'use_async',
    ]
    list_display_links = [
        'id',
        'name',
        'content_type',
        'event_signals_display',
    ]
    list_filter = ['is_active', 'content_type', 'created_at']
    search_fields = ['name', 'endpoint']
    readonly_fields = [
        'created_at',
        'updated_at',
        'last_success',
        'last_failure',
        'last_response',
    ]

    # Detail Page Configuration
    fieldsets = [
        (
            None,
            {
                'fields': [
                    'name',
                    'content_type',
                    'event_signals',
                    'endpoint',
                    'is_active',
                ]
            },
        ),
        (_('Authentication'), {'fields': ['secret']}),
        (
            _('Advanced'),
            {
                'fields': [
                    'headers',
                    'keep_last_response',
                    'use_async',
                    'max_retries',
                    'retry_delay',
                ],
                'classes': ['collapse'],
            },
        ),
        (
            _('Status'),
            {'fields': ['last_success', 'last_failure', 'last_response']},
        ),
        (_('Metadata'), {'fields': ['created_at', 'updated_at']}),
    ]
    inlines = [WebhookRegistryDeliverLogInline]

    def event_signals_display(self, obj):
        return ', '.join(obj.event_signals) if obj.event_signals else '-'

    event_signals_display.short_description = _('Event Types')

    def status_indicator(self, obj):
        if (
            obj.last_response
            and obj.last_success
            and (not obj.last_failure or obj.last_success > obj.last_failure)
        ):
            return format_html('<span style="color: green;">●</span> Success')
        elif obj.last_failure:
            return format_html('<span style="color: red;">●</span> Failed')
        else:
            return format_html('<span style="color: gray;">●</span> No data')

    status_indicator.short_description = _('Status')

    def webhooks_sent(self, obj):
        """Return the number of webhooks sent for this registry."""
        return obj.delivery_logs.count()

    webhooks_sent.short_description = _('Log Count')

    actions = ['=activate_webhooks', 'deactivate_webhooks']

    @admin.action(description=_('Activate selected webhooks'))
    def activate_webhooks(self, request, queryset):
        """Action to activate selected webhooks."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} webhook(s) activated.')

    @admin.action(description=_('Deactivate selected webhooks'))
    def deactivate_webhooks(self, request, queryset):
        """Action to deactivate selected webhooks."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} webhook(s) deactivated.')


@admin.register(WebhookDeliveryLog)
class WebhookDeliveryLogAdmin(admin.ModelAdmin):
    """Admin configuration for WebhookDeliveryLog model."""

    list_display = [
        'webhook',
        'event_signal',
        'created_at',
        'response_status',
        'has_error',
    ]
    list_filter = ['webhook', 'event_signal', 'response_status', 'created_at']
    search_fields = [
        'webhook__name',
        'webhook__endpoint',
        'error_message',
        'payload',
    ]
    readonly_fields = [
        'webhook',
        'event_signal',
        'payload',
        'response_status',
        'response_body',
        'error_message',
        'created_at',
    ]

    def has_error(self, obj):
        return bool(obj.error_message)

    has_error.boolean = True
    has_error.short_description = _('Error')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
