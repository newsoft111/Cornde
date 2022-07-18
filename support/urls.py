from django.urls import include, path
from . import views

urlpatterns = [
	path(
		"faq/",
		include(
			[
				path('', views.faq, name='FaqList'),
				path('update/<int:faq_id>/', views.faq_update, name='FaqUpdate'),
			]
		)
	),
	path(
		"qna/",
		include(
			[
				path('', views.qna, name='QnaList'),
			]
		)
	),
	path('price/', views.price, name='Price'),
]