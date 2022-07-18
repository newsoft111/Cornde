from django.urls import reverse
from django.contrib.sitemaps import Sitemap
from gig.models import GigCampaign

class StaticViewSitemap(Sitemap):
	priority = 0.5
	changefreq = 'daily'
	
	def items(self):
		return [
			'Index',
			'CampaignList',
			"FaqList",
			"CheckNblog",
			"Price",
		]
		
	def location(self, item):
		return reverse(item)


class CampaignSitemap(Sitemap):
	changefreq = 'daily'
	priority = 1

	def items(self):
			return GigCampaign.objects.all().filter(is_paid=True).order_by('-id')
	def lastmod(self, obj):
			return obj.started_at