"""Permissions for the django_webhook_receiver app."""

import re

from rest_framework import permissions


class WebhookPermission(permissions.BasePermission):
    """Permission class that validates webhook access based on their
    configuration.

    This permission class works alongside our WebhookAuthentication class, and
    ensures that the webhook request is authorized based on the provided
    configuration.
    """

    message = 'This webhook is not authorized to perform this action.'

    def has_permission(self, request, view):
        """Check if the webhook has permission to access this view.

        This method is called before the view executes. We need to verify:
        1. The request was authenticated with a webhook.
        2. The webhook has permission for this specific action.
        """

        # Ensuring we have webhook authentication
        if not hasattr(request, 'auth') or not isinstance(request.auth, dict):
            # No webhook authentication
            return False

        # Extract the webhook configuration
        webhook_config = request.auth.get('webhook_config')
        if not webhook_config:
            # No webhook configuration
            return False

        # Checking if the webhook can perform the action
        return self._check_webhook_permissions(request, webhook_config)

    def _check_webhook_permissions(self, request, webhook_config):
        """Determine if the webhook has the necessary permissions.

        This is where we implement our permission logic based on:
        - The signal type in the request
        - The source being affected
        - The URL being accessed
        - The HTTP method being used
        """

        # Extract information from the request
        event_signal = request.auth.get('event_signal')
        source = request.auth.get('source')
        url = request.path
        method = request.method

        # Query for matching permissions
        matching_permissions = webhook_config.permissions.filter(
            signal_type=event_signal,
            source=source,
        )
        # Check if any permission matches our URL and method
        for permission in matching_permissions:
            if self._url_matches(url, permission.url_pattern):
                return permission.allows_method(method)

        return False

    def _url_matches(self, request_url, pattern):
        """Check if the request URL matches the permission pattern."""

        # Simple exact match
        if request_url == pattern:
            return True
        # Regex match
        if pattern.startswith('^') and pattern.endswith('$'):
            return re.match(pattern, request_url) is not None
        # Fallback to simple substring match
        return pattern in request_url
