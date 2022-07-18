from django.urls import path, include
from . import views

urlpatterns = [
	path('login/', views.user_login, name='UserLogin'),
	path('logout/', views.user_logout, name='UserLogout'),
	path('join/', views.user_join, name='UserJoin'),
	path('confirm/<str:uidb64>/<str:token>/', views.join_confirm, name="JoinConfirm"),
	path('find/password/', views.find_passwd, name='FindPasswd'),
	path('reset/password/<str:uidb64>/<str:token>/', views.reset_passwd, name='ResetPasswd'),
	path('verify/email/', views.verify_email, name='VerifyEmail'),
	path('change/password', views.change_passwd, name='ChangePasswd'),
	path(
		"mypage/",
		include(
			[
				path('campaign/', views.user_campaign, name='UserCampaign'),
				path('plan/', views.user_plan, name='UserPlan'),
				path('favorite/', views.user_favorite, name='UserFavorite'),
				path('point/', views.user_point, name='UserPoint'),
				path('point/withdraw/', views.user_withdraw, name='UserWithdraw'),
				path('review/', views.user_review, name='UserReview'),
				path('profile/', views.user_profile, name='UserProfile'),
				path('add/address/', views.add_shipping_address, name='AddShippingAddress'),
				path('delete/address/', views.del_shipping_address, name='DelShippingAddress'),
				path('delete/account', views.user_delete, name='UserDelete'),
				path('message/', views.user_message, name='UserMessage'),
				path('reset/message/', views.reset_user_message, name='ResetUserMessage'),
				path('change/avater/', views.change_user_avater, name='ChangeUserAvater'),
			]
		)
	),
	path(
		"auth/sms/",
		include(
			[
				path('send/', views.sms_code_send, name='SmsCodeSend'),
				path('check/', views.sms_code_check, name='SmsCodeCheck'),
			]
		)
	),
]
