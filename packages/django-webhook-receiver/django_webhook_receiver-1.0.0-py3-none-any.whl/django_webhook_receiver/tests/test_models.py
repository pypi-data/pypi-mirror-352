from django.test import TestCase
from django.contrib.auth import get_user_model

from django_webhook_receiver import models
from .factories import WebhookConfigFactory, WebhookPermissionFactory


class WebhookConfigurationModelTests(TestCase):
    def test_webhook_configuration_is_created_successfully(self):
        webhook_config = models.WebhookConfiguration.objects.create(
            name='Test Webhook',
            secret='test-secret',
            is_active=True,
            description='Test description',
        )
        webhook_config.full_clean()  # Validate the model
        self.assertEqual(webhook_config.name, 'Test Webhook')
        self.assertEqual(webhook_config.secret, 'test-secret')
        self.assertTrue(webhook_config.is_active)
        self.assertEqual(webhook_config.description, 'Test description')
        self.assertIsNotNone(webhook_config.created_at)
        self.assertIsNotNone(webhook_config.updated_at)

    def test_webhook_configuration_str_method(self):
        webhook_config = WebhookConfigFactory.create(name='Test Webhook')
        self.assertEqual(str(webhook_config), 'Test Webhook')

    def test_single_webhook_user_exists(self):
        # Checking there are no users in the system
        self.assertEqual(get_user_model().objects.count(), 0)
        # Getting the single webhook user (is created)
        user1 = models.WebhookConfiguration.get_webhook_user()
        # Getting the single webhook user again (should be the same)
        user2 = models.WebhookConfiguration.get_webhook_user()
        self.assertEqual(user1, user2)
        # Checking that only one user exists
        self.assertEqual(get_user_model().objects.count(), 1)
        # Checking the user cannot log in
        self.assertFalse(user1.has_usable_password())

    def test_rotate_secret(self):
        webhook_config = WebhookConfigFactory.create(secret='old-secret')
        old_secret = webhook_config.secret
        webhook_config.rotate_secret()
        webhook_config.full_clean()
        self.assertNotEqual(webhook_config.secret, old_secret)
        old_secret = webhook_config.secret
        webhook_config.secret = models.WebhookConfiguration.generate_secret()
        webhook_config.full_clean()
        self.assertNotEqual(webhook_config.secret, old_secret)


class WebhookPermissionModelTests(TestCase):
    def setUp(self):
        self.webhook_config = WebhookConfigFactory.create()

    def test_webhook_permission_is_created_successfully(self):
        webhook_permission = models.WebhookPermission.objects.create(
            configuration=self.webhook_config,
            signal_type='updated',
            source='app_name.ModelName',
            url_pattern='/api/v1/webhook/',
            allowed_methods='POST, GET',
        )
        webhook_permission.full_clean()
        self.assertEqual(webhook_permission.configuration, self.webhook_config)
        self.assertEqual(webhook_permission.signal_type, 'updated')
        self.assertEqual(webhook_permission.source, 'app_name.ModelName')
        self.assertEqual(webhook_permission.url_pattern, '/api/v1/webhook/')
        self.assertEqual(webhook_permission.allowed_methods, 'POST, GET')
        self.assertIsNotNone(webhook_permission.created_at)
        self.assertIsNotNone(webhook_permission.updated_at)

    def test_webhook_permission_str_method(self):
        webhook_permission = WebhookPermissionFactory.create(
            configuration=self.webhook_config,
            signal_type='updated',
            source='ModelName',
        )
        self.assertEqual(
            str(webhook_permission),
            f'{self.webhook_config} - updated - ModelName',
        )

    def test_webhook_permission_allows_method(self):
        webhook_permission = WebhookPermissionFactory.create(
            allowed_methods=''
        )

        test_cases = [
            ('GET', True),
            ('POST', True),
            ('PUT', True),
            ('DELETE', True),
        ]

        for method, expected in test_cases:
            self.assertEqual(
                webhook_permission.allows_method(method),
                expected,
            )

        test_cases = [
            ('GET', True),
            ('PATCH', False),
            ('POST', True),
            ('OPTIONS', False),
            ('HEAD', False),
        ]
        webhook_permission.allowed_methods = 'GET, POST'

        for method, expected in test_cases:
            self.assertEqual(
                webhook_permission.allows_method(method),
                expected,
            )
