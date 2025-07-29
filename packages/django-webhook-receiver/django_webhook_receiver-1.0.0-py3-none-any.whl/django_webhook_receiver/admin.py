"""Admin configuration for the django_webhook_receiver app."""

from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from django_webhook_receiver import models


class WebhookPermissionInline(admin.TabularInline):
    """Inline admin for webhook permissions."""

    model = models.WebhookPermission
    extra = 1  # Show one empty form for adding new permissions

    fields = ['signal_type', 'source', 'url_pattern', 'allowed_methods']
    classes = ['collapse']


@admin.register(models.WebhookConfiguration)
class WebhookConfigurationAdmin(admin.ModelAdmin):
    """Admin configuration for the :class:`WebhookConfiguration` model."""

    # Control which fields are displayed in the list view
    list_display = [
        'name',
        'secret_preview',
        'is_active_display',
        'permission_count',
        'created_at',
        'updated_at',
    ]
    list_filters = ['is_active', 'created_at', 'updated_at']
    search_fields = ['name', 'description']

    # Add helpful actions
    actions = ['activate_webhooks', 'deactivate_webhooks', 'rotate_secrets']

    # Group related fields
    fieldsets = (
        (
            'Webhook Configuration',
            {
                'fields': ('name', 'secret', 'is_active'),
            },
        ),
        (
            'Meta',
            {
                'fields': ('created_at', 'updated_at', 'description'),
                'classes': ('collapse',),
            },
        ),
    )
    readonly_fields = ['created_at', 'updated_at']
    inlines = [WebhookPermissionInline]

    def secret_preview(self, obj):
        """Show only the first 8 characters of the secret."""
        if obj.secret:
            return f'{obj.secret[:12]}...'
        return ''

    secret_preview.short_description = 'Secret'

    def is_active_display(self, obj):
        """
        Display active status with color coding.

        This makes it easy to see at a glance which webhooks are active.
        """
        if obj.is_active:
            return format_html('<span style="color: green;">✓ Active</span>')
        return format_html('<span style="color: red;">✗ Inactive</span>')

    is_active_display.short_description = 'Status'

    def permission_count(self, obj):
        """
        Show how many permissions this webhook has.

        Includes a link to view/edit permissions.
        """
        count = obj.permissions.count()
        url = (
            reverse(
                'admin:django_webhook_receiver_webhookpermission_changelist'
            )
            + f'?configuration__id__exact={obj.id}'
        )
        return format_html('<a href="{}">{} permission(s)</a>', url, count)

    permission_count.short_description = 'Permissions'

    def activate_webhooks(self, request, queryset):
        """Action to activate selected webhooks."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} webhook(s) activated.')

    activate_webhooks.short_description = 'Activate selected webhooks'

    def deactivate_webhooks(self, request, queryset):
        """Action to deactivate selected webhooks."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} webhook(s) deactivated.')

    deactivate_webhooks.short_description = 'Deactivate selected webhooks'

    def rotate_secrets(self, request, queryset):
        """Action to rotate secrets for selected webhooks."""
        count = 0
        for webhook in queryset:
            webhook.rotate_secret()
            count += 1
        self.message_user(
            request,
            f'{count} secret(s) rotated. New secrets have been generated.',
        )

    rotate_secrets.short_description = 'Rotate secrets for selected webhooks'


@admin.register(models.WebhookPermission)
class WebhookPermissionAdmin(admin.ModelAdmin):
    list_display = [
        'configuration',
        'signal_type',
        'source',
        'url_pattern',
        'allowed_methods',
        'created_at',
    ]
    list_filter = ['configuration', 'signal_type', 'source']
    search_fields = [
        'configuration__name',
        'signal_type',
        'source',
        'url_pattern',
    ]

    # Group related fields
    fieldsets = (
        ('Webhook Configuration', {'fields': ('configuration',)}),
        (
            'Permission Details',
            {'fields': ('signal_type', 'source', 'url_pattern')},
        ),
        (
            'Access Control',
            {
                'fields': ('allowed_methods',),
                'description': (
                    'Comma-separated list of allowed HTTP methods '
                    '(e.g., GET, POST)'
                ),
            },
        ),
        (
            'Meta',
            {
                'fields': ('created_at',),
                'classes': ('collapse',),
            },
        ),
    )
    raw_id_fields = ['configuration']
    readonly_fields = ['created_at']
