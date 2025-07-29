from django.test import TestCase

from rest_framework.test import APIRequestFactory

from django_webhook_receiver import authentication, models


WEBHOOK_URL = '/api/webhook/'


class WebhookAuthenticationTests(TestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.auth = authentication.WebhookAuthentication()

        # creating test webhooks
        self.webhook1 = models.WebhookConfiguration.objects.create(
            name='Test Webhook 1',
            secret='webhook-secret-1',
        )
        # creating test webhooks
        self.webhook2 = models.WebhookConfiguration.objects.create(
            name='Test Webhook 2',
            secret='webhook-secret-2',
        )

    def test_authentication_returns_same_user_different_auth(self):
        request1 = self.factory.post(
            WEBHOOK_URL,
            HTTP_X_SECRET=self.webhook1.secret,
        )
        request1.data = {'event_signal': 'created', 'source': 'ModelName'}
        request2 = self.factory.post(
            WEBHOOK_URL,
            HTTP_X_SECRET=self.webhook2.secret,
        )
        request2.data = {'event_signal': 'updated', 'source': 'ModelName'}

        # Authenticate both requests
        result1 = self.auth.authenticate(request1)
        result2 = self.auth.authenticate(request2)

        # Both should return the same user
        self.assertIsNotNone(result1)
        self.assertIsNotNone(result2)
        self.assertEqual(result1[0], result2[0])  # user should be the same
        self.assertNotEqual(result1[1], result2[1])  # auth should be different

    def test_authenticate_without_secret(self):
        request = self.factory.post(
            WEBHOOK_URL,
            data={'event_signal': 'created', 'source': 'ModelName'},
        )
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_with_empty_secret(self):
        request = self.factory.post(
            WEBHOOK_URL,
            data={'event_signal': 'created', 'source': 'ModelName'},
            HTTP_X_SECRET='',
        )
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_preserves_request_data(self):
        original_data = {
            'event_signal': 'created',
            'source': 'ModelName',
            'fields': {
                'field1': 'value1',
                'field2': 'value2',
            },
        }
        request = self.factory.post(
            WEBHOOK_URL,
            HTTP_X_SECRET=self.webhook1.secret,
        )
        request.data = original_data

        # Store the original data
        original_signal = request.data.get('event_signal')
        original_model = request.data.get('source')
        original_fields = request.data.get('fields')

        self.auth.authenticate(request)

        # Verify that the original data is preserved
        self.assertEqual(request.data.get('event_signal'), original_signal)
        self.assertEqual(request.data.get('source'), original_model)
        self.assertEqual(request.data.get('fields'), original_fields)

    def test_authenticate_without_webhook_configuration(self):
        request = self.factory.post(
            WEBHOOK_URL,
            data={'event_signal': 'deleted', 'source': 'ModelName1'},
            HTTP_X_SECRET='invalid-secret',
        )
        result = self.auth.authenticate(request)
        self.assertIsNone(result)

    def test_authenticate_object_contains_webhook_identification(self):
        request = self.factory.post(
            WEBHOOK_URL,
            HTTP_X_SECRET='webhook-secret-1',
        )
        request.data = {
            'event_signal': 'created',
            'source': 'ModelName',
        }

        # Attempt authentication
        user, auth = self.auth.authenticate(request)

        # Verify the auth object has all identification fields
        self.assertIn('webhook_config', auth)
        self.assertIn('config_id', auth)
        self.assertIn('config_name', auth)
        self.assertIn('secret', auth)
        self.assertIn('event_signal', auth)
        self.assertIn('source', auth)

        # Verify the values are correct
        self.assertEqual(auth['config_id'], self.webhook1.id)
        self.assertEqual(auth['config_name'], self.webhook1.name)
        self.assertEqual(auth['secret'], 'webhook-secret-1')
        self.assertEqual(auth['event_signal'], 'created')
        self.assertEqual(auth['source'], 'ModelName')

    def test_authenticate__authenticate_header(self):
        request = self.factory.post(WEBHOOK_URL)
        header = self.auth.authenticate_header(request)
        self.assertEqual(header, 'X-Secret')
