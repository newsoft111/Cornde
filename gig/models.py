from django.db import models
from django.conf import settings
from datetime import datetime
from imagekit.models import ProcessedImageField
from imagekit.processors import ResizeToFill
from account.models import UserShippingAddress
from django.urls import reverse



def upload_to(instance, filename):
	nowDate = datetime.now().strftime("%Y/%m/%d")
	return '/'.join([str(instance.user.id), instance.folder , nowDate, filename])

class GigCampaign(models.Model):
	user = models.ForeignKey(
				settings.AUTH_USER_MODEL,
				on_delete=models.CASCADE
	)
	subject = models.CharField(max_length=255)
	keyword = models.CharField(max_length=255)
	product_url = models.CharField(max_length=255,blank=True)
	provide = models.CharField(max_length=255)
	guide_line = models.TextField()
	limit_offer = models.IntegerField()
	company_name = models.CharField(max_length=255)
	company_address = models.CharField(max_length=255, blank=True)
	reward = models.IntegerField(default=0)
	category = models.CharField(max_length=255)
	campaign_type = models.CharField(max_length=255)
	channel = models.CharField(max_length=255)
	finished_at = models.DateTimeField()
	started_at = models.DateTimeField(default=datetime.now)
	merchant_uid = models.CharField(max_length=255, null=True)
	is_paid=models.BooleanField(default=False)
	is_item=models.BooleanField(default=False)
	pay_amount = models.IntegerField()
	

	is_recommend=models.BooleanField(default=False)
	favorite_user = models.ManyToManyField(
				settings.AUTH_USER_MODEL,
				related_name="favorite_user_set",
				blank=True,
				through='GigCampaignFavorite'
	)
	offer_user = models.ManyToManyField(
				settings.AUTH_USER_MODEL,
				related_name="offer_user_set",
				blank=True,
				through='GigCampaignOffer'
	)
	folder = 'campaign'
	thumbnail = ProcessedImageField(
				upload_to=upload_to,
				processors=[ResizeToFill(800, 800)],
	)

	def set_foo(self, x):
		self.foo = json.dumps(x)

	def get_foo(self):
		return json.loads(self.foo)

	def get_absolute_url(self):
		return reverse('CampaignDetail', args=[self.pk])

	class Meta:
		managed = True
		db_table = 'gig_campaign'


class GigCampaignFavorite(models.Model):
	user = models.ForeignKey(
			settings.AUTH_USER_MODEL,
			on_delete=models.CASCADE
	)
	campaign = models.ForeignKey(
			GigCampaign,
			on_delete=models.CASCADE
	)
	favorite_at = models.DateTimeField(default=datetime.now)


	class Meta:
		managed = True
		db_table = 'gig_campaign_favorite'


class GigCampaignOffer(models.Model):
	user = models.ForeignKey(
			settings.AUTH_USER_MODEL,
			on_delete=models.CASCADE
	)
	campaign = models.ForeignKey(
			GigCampaign,
			on_delete=models.CASCADE
	)
	appeal = models.CharField(max_length=255)
	sns_url = models.CharField(max_length=255)
	shipping_address = models.ForeignKey(
			UserShippingAddress,
			on_delete=models.CASCADE
	)
	offer_at = models.DateTimeField(default=datetime.now)
	is_picked=models.BooleanField(default=False)

	class Meta:
		managed = True
		db_table = 'gig_campaign_offer'


class GigCampaignReview(models.Model):
	offer = models.ForeignKey(
			GigCampaignOffer,
			on_delete=models.CASCADE
	)
	review_url = models.CharField(max_length=255)
	created_at = models.DateTimeField(default=datetime.now)
	is_confirm = models.BooleanField(default=False)

	class Meta:
		managed = True
		db_table = 'gig_campaign_review'