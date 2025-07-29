"""Authentication for the django_webhook_receiver app."""

from django_webhook_receiver import models


class WebhookAuthentication:
    """Authenticates webhooks based on X-Secret header.

    This authentication class:
    1. Extracts the X-Secret header from the request.
    2. Validates the secret against stored webhook configurations.
    3. Returns a user object and authenticated info.
    """

    def authenticate(self, request):
        """Authenticate the request and return a two-tuple of (user, auth), or
        None if authentication fails."""

        # Django converts custom headers to META keys with 'HTTP_' prefix
        # and converts to uppercase, so X-Secret becomes HTTP_X_SECRET
        secret = request.META.get('HTTP_X_SECRET')

        if not secret or not secret.strip():
            # By returning None, we're giving the chance for other
            # authentication classes to try and authenticate the request.
            return None

        # Remove any whitespace from the secret
        secret = secret.strip()

        return self._authenticate_secret(request, secret)

    def _authenticate_secret(self, request, secret):
        """Validate the secret and return a authentication result."""

        try:
            # Lookup the webhook configuration by secret
            webhook_config = models.WebhookConfiguration.objects.get(
                secret=secret,
                is_active=True,  # Only consider active webhooks
            )
        except models.WebhookConfiguration.DoesNotExist:
            # If the secret is not valid, return None
            return None

        # Get the single webhook user
        user = models.WebhookConfiguration.get_webhook_user()

        # Create the auth object with all relevant information
        auth_info = self._build_auth_info(request, webhook_config, secret)

        return (user, auth_info)

    def _build_auth_info(self, request, webhook_config, secret):
        """Build the authentication information dictionary."""

        # Safely get request data - it might not be parsed yet
        event_signal = None
        source = None

        if hasattr(request, 'data'):
            event_signal = request.data.get('event_signal')
            source = request.data.get('source')

        return {
            'secret': secret,
            'webhook_config': webhook_config,
            'config_id': webhook_config.id,
            'config_name': webhook_config.name,
            'event_signal': event_signal,
            'source': source,
        }

    def authenticate_header(self, request):
        """Returns the string to be used as the value of the `WWW-Authenticate`
        header in a `401 Unauthenticated` response."""

        return 'X-Secret'
