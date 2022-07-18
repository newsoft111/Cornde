"""core URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path,include
from django.conf import settings
from django.conf.urls.static import static
from .sitemaps import *
from django.contrib.sitemaps.views import sitemap

sitemaps = {
	'static':StaticViewSitemap,
	"campaign":CampaignSitemap
}


urlpatterns = [
    path('', include('main.urls')),
		path('account/', include('account.urls')),
		path('gig/', include('gig.urls')),
		path('payment/', include('payment.urls')),
		path('support/', include('support.urls')),
		path('util/', include('util.urls')),
		path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

]

if settings.DEBUG:
	urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

