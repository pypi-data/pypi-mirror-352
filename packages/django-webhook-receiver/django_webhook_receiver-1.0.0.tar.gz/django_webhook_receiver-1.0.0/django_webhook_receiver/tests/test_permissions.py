from django.test import TestCase

from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from django_webhook_receiver import permissions, models
from .factories import WebhookConfigFactory, WebhookPermissionFactory


WEBHOOK_URL = '/api/webhook/'


class WebhookPermissionTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.permission = permissions.WebhookPermission()
        self.view = APIView()

        # creating test webhooks
        self.config = WebhookConfigFactory(
            secret='config-secret',
        )
        self.webhook_permission = WebhookPermissionFactory(
            configuration=self.config,
            source='ModelName',
            signal_type='created',
            allowed_methods='POST',
            url_pattern='/api/webhook/',
        )

    def test_permission_checks_auth_not_user(self):
        request = self.factory.post('/api/webhook/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = {
            'webhook_config': self.config,
            'secret': 'config-secret',
            'event_signal': 'created',
            'source': 'ModelName',
        }

        self.assertTrue(self.permission.has_permission(request, self.view))

    def test_permission_without_auth_info(self):
        request = self.factory.post('/api/webhook/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = None

        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_without_webhook_config(self):
        request = self.factory.post('/api/webhook/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = {
            'webhook_config': None,
            'secret': 'config-secret',
            'event_signal': 'created',
            'source': 'ModelName',
        }
        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_with_invalid_event_signal(self):
        request = self.factory.post('/api/webhook/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = {
            'webhook_config': self.config,
            'secret': 'config-secret',
            'event_signal': 'invalid-signal',
            'source': 'ModelName',
        }

        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_with_invalid_model(self):
        request = self.factory.post('/api/webhook/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = {
            'webhook_config': self.config,
            'secret': 'config-secret',
            'event_signal': 'created',
            'source': 'InvalidModel',
        }

        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_with_invalid_url(self):
        request = self.factory.post('invalid-url/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = {
            'webhook_config': self.config,
            'secret': 'config-secret',
            'event_signal': 'created',
            'source': 'ModelName',
        }

        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_with_invalid_method(self):
        request = self.factory.post('/api/webhook/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = {
            'webhook_config': self.config,
            'secret': 'config-secret',
            'event_signal': 'created',
            'source': 'ModelName',
        }

        # Simulate a GET request
        request.method = 'GET'

        self.assertFalse(self.permission.has_permission(request, self.view))

    def test_permission_with_url_pattern_regex(self):
        request = self.factory.post('/api/webhook/')
        request.user = models.WebhookConfiguration.get_webhook_user()
        request.auth = {
            'webhook_config': self.config,
            'secret': 'config-secret',
            'event_signal': 'created',
            'source': 'ModelName',
        }

        # Update the URL pattern to a regex
        self.webhook_permission.url_pattern = r'^/api/webhook/$'
        self.webhook_permission.save()

        self.assertTrue(self.permission.has_permission(request, self.view))
