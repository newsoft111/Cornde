from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='Index'),
	path('terms-of-service/', views.terms_of_service, name='TermsOfService'),
	path('s/<int:num>/', views.short_url, name='ShortUrl'),
	path('privacy/', views.privacy, name='Privacy'),
	path('nblog/check/', views.check_nblog, name='CheckNblog'),
	path('robots.txt', views.robots),
]