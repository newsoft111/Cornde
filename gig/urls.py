from django.urls import include, path
from .views import campaign

urlpatterns = [
	path(
		"campaign/",
		include(
			[
				path('', campaign.campaign_list, name='CampaignList'),
				path('write/', campaign.campaign_write, name='CampaignWrite'),
				path('delete/<int:campaign_id>/', campaign.campaign_delete, name='CampaignDelete'),
				path('pay/<int:campaign_id>/', campaign.campaign_pay, name='CampaignPay'),
				path('update/<int:campaign_id>/', campaign.campaign_update, name='CampaignUpdate'),
				path('<int:campaign_id>/', campaign.campaign_detail, name='CampaignDetail'),
				path('favorite/', campaign.campaign_favorite, name='CampaignFavorite'),
				path('offer/<int:campaign_id>/', campaign.campaign_offer, name='CampaignOffer'),
				path('pick/<int:campaign_id>/', campaign.campaign_pick, name='CampaignPick'),
				path('pick/export/<int:campaign_id>/', campaign.campaign_pick_export, name='CampaignPickExport'),
				path('review/<int:campaign_id>/', campaign.campaign_review, name='CampaignReview'),
				path('confirm/<int:review_id>/', campaign.campaign_confirm, name='CampaignConfirm'),
			]
		)
	),
]