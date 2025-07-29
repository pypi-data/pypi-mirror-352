import factory


class WebhookConfigFactory(factory.django.DjangoModelFactory):

    name = factory.Faker('name')
    secret = factory.Faker('sha256')
    is_active = factory.Faker('boolean')
    description = factory.Faker('text', max_nb_chars=200)

    class Meta:

        model = 'django_webhook_receiver.WebhookConfiguration'
        django_get_or_create = ('secret',)


class WebhookPermissionFactory(factory.django.DjangoModelFactory):

    configuration = factory.SubFactory(WebhookConfigFactory)
    signal_type = factory.Faker('word')
    source = factory.Faker('word')
    url_pattern = factory.Faker('url')
    allowed_methods = factory.Faker('word')

    class Meta:
        model = 'django_webhook_receiver.WebhookPermission'
