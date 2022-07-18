from django.urls import path, include
from . import views

urlpatterns = [
	path('webhook/', views.pyment_webhook, name='PymentWebhook'),
]
