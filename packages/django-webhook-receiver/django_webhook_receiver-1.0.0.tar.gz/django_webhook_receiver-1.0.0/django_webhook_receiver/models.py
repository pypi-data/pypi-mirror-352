"""Models for the django_webhook_receiver app."""

import secrets
import string

from django.db import models
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _


class WebhookConfiguration(models.Model):
    """Stores webhook configuration and secrets.

    Each configuration represents a different webhook client that can
    authenticate with our system.
    """

    id = models.AutoField(primary_key=True)
    name = models.CharField(
        _('name'),
        max_length=255,
        help_text=_('Descriptive name for this webhook'),
    )
    secret = models.CharField(
        _('secret'),
        max_length=255,
        unique=True,
        help_text=_('Secret used to authenticate this webhook'),
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_('Is this webhook configuration active?'),
    )

    # Meta fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this webhook configuration was created'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('When this webhook configuration was last updated'),
    )
    description = models.TextField(
        blank=True,
        help_text=_('Description of this webhook configuration (Optional)'),
    )

    class Meta:
        ordering = ['-id']
        db_table = 'django_webhook_receiver_webhook_configuration'
        verbose_name = _('Webhook Configuration')
        verbose_name_plural = _('Webhook Configurations')

    def __str__(self):
        return self.name

    @classmethod
    def get_webhook_user(self):
        """Get or create the single user for all webhooks.

        This method ensures we only have one webhook user in the system.
        """

        user, created = get_user_model().objects.get_or_create(
            username='webhook_system',
            defaults={
                'is_active': True,
                'is_staff': False,
            },
        )

        if created:
            # Ensuring the user cannot log in (safety measure)
            user.set_unusable_password()
            user.save()

        return user

    @classmethod
    def generate_secret(cls):
        """
        Generate a cryptographically secure secret.

        Returns a 32-character string using letters and digits.
        """
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))

    def rotate_secret(self):
        """Generate a new secret for this webhook."""

        self.secret = self.generate_secret()
        self.save()
        return self.secret


class WebhookPermission(models.Model):
    """Defines what a webhook configuration is allowed to do.

    This creates a flexible permission system where each webhook can have
    different access rights.
    """

    configuration = models.ForeignKey(
        WebhookConfiguration,
        related_name='permissions',
        on_delete=models.CASCADE,
        help_text=_('Webhook configuration this permission belongs to'),
    )
    signal_type = models.CharField(
        _('signal type'),
        max_length=255,
        help_text=_('Type of signal this permission applies to'),
    )
    source = models.CharField(
        _('source'),
        max_length=255,
        help_text=_('Name of the model (source) this permission applies to'),
    )
    url_pattern = models.CharField(
        _('URL pattern'),
        max_length=255,
        help_text=_('URL pattern this permission applies to'),
    )
    allowed_methods = models.CharField(
        _('allowed methods'),
        max_length=255,
        blank=True,
        help_text=_('HTTP methods allowed for this permission (Optional)'),
    )

    # Meta fields
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_('When this permission was created'),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_('When this permission was last updated'),
    )

    class Meta:
        ordering = ['-id']
        db_table = 'django_webhook_receiver_webhook_permission'
        verbose_name = _('Webhook Permission')
        verbose_name_plural = _('Webhook Permissions')

    def __str__(self):
        return f'{self.configuration} - {self.signal_type} - {self.source}'

    def allows_method(self, method):
        allowed = [m.strip().upper() for m in self.allowed_methods.split(',')]
        return method.upper() in allowed if self.allowed_methods else True
