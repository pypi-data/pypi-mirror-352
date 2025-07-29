from django.urls import path
from django.http import JsonResponse


# Simple view function for testing
def webhook_test_view(request):
    return JsonResponse({'status': 'success'})


# URL patterns for testing
urlpatterns = [
    path('api/webhook/', webhook_test_view),
    path('api/webhook/<int:id>/', webhook_test_view),
]
