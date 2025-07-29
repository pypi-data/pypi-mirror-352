"""Django Webhooks Receiver App Configuration."""

from django.apps import AppConfig


class WebhooksReceiverConfig(AppConfig):
    name = 'django_webhook_receiver'
    verbose_name = 'Django Webhooks Receiver'
    default_auto_field = 'django.db.models.BigAutoField'
