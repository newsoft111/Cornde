from django.shortcuts import redirect, render,get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.db.models import Q, Case, When
from gig.models import GigCampaign,GigCampaignOffer,GigCampaignReview
from django.core.paginator import Paginator
from account.views import user_login, user_profile
from main.views import index
from datetime import datetime, timedelta
import random
import re
from util.views import AddUserPointLog,MessageSender,SmsSender
from payment.views import payment_refund,payment_check, payment_data
from account.models import UserShippingAddress
from django.shortcuts import resolve_url
from django.contrib.auth.decorators import login_required
import xlwt
import urllib

def campaign_list(request):
	seo = {
		'title': "캠페인 리스트 - 콘디",
	}
	
	category_list = [
		'코스메틱', 
		'미용', 
		'음식',
		'패션/잡화',
		'식품', 
		'생활용품', 
		'출산/육아', 
		'디지털/가전', 
		'스포츠/건강', 
		'반려동물', 
		'맛집', 
		'여행/숙박', 
		'지역/문화', 
		'기타'
	]
	channel_list = ["네이버블로그", "인스타그램", "유튜브", "카페", "네이버포스트", "기타"]
	type_list = ['배송형', '방문형', '기자단','구매형']
	
	q = Q()
	q &= Q(is_paid = True)
	q &= Q(finished_at__gte=datetime.now())
	if request.GET.get("category"):
		q &= Q(category = category_list[int(request.GET.get("category"))])
	if request.GET.get("channel"):
		q &= Q(channel__contains = channel_list[int(request.GET.get("channel"))])
	if request.GET.get("type"):
		q &= Q(campaign_type = type_list[int(request.GET.get("type"))])
	if request.GET.get("keyword"):
		q &= Q(subject__icontains = request.GET.get("keyword"))
	
	

	campaign_list =  GigCampaign.objects.filter(q).order_by(
		Case(
			When(pk=132),
			When(pk=117), 
			When(pk=129), 
			When(pk=124), 
			When(pk=103), 
			When(pk=97), 
		default=0),
		'-is_item', 
		"-id",
	)
	page        = int(request.GET.get('p', 1))
	pagenator   = Paginator(campaign_list, 16)
	campaign_list = pagenator.get_page(page)
	return render(request, 'gig/campaign/campaign_list.html' ,{
		"seo":seo,
		"campaign_list":campaign_list,
		"category_list":category_list,
		"channel_list":channel_list,
		"type_list":type_list,
	})


@login_required(login_url=user_login)
def campaign_write(request):
	seo = {
		'title': "체험단 모집 - 콘디",
	}

	if request.method == 'POST':
		campaign_type = request.POST.get("campaign_type")
		category = request.POST.get("category")
		thumbnail = request.FILES['campaign_img']
		subject = request.POST.get("subject")
		provide = request.POST.get("provide")
		guide_line = request.POST.get("guide_line")
		keyword = request.POST.get("keyword")
		product_url = request.POST.get("product_url")
		channel = ",".join(request.POST.getlist("channel[]"))
		limit_offer = request.POST.get("limit_offer")
		finished_at = request.POST.get("finished_at")
		item = request.POST.get("item")
		company_address = request.POST.get("company_address")
		company_name = request.POST.get("company_name")
		if request.user.plan_at > datetime.now():
			reward = 0
		else:
			reward = re.sub(r'[^0-9]', '', request.POST.get('reward'))
		

		item_price = 0
		if item != 'default':
			item_price = item_price+10000
			if item == 'recommend':
				item_price = item_price+20000
				
		
		pay_amount = (int(finished_at)-3)*2000+(int(limit_offer)*5000)+(int(reward)*int(limit_offer))+int(item_price)+100
		
		try:
			campaign = GigCampaign()
			campaign.campaign_type = campaign_type
			campaign.category = category
			campaign.subject = subject
			campaign.channel = channel
			campaign.thumbnail = thumbnail
			campaign.provide = provide
			campaign.guide_line = guide_line
			campaign.keyword = keyword
			if product_url is not None:
				campaign.product_url = product_url
			campaign.limit_offer = limit_offer
			if company_address is not None:
				campaign.company_address = company_address
			if request.user.plan_type != 0 and request.user.plan_at > datetime.now():
				campaign.is_paid = True
				campaign.pay_amount = 0
			else:
				campaign.pay_amount = pay_amount
			campaign.finished_at = datetime.now() + timedelta(days=int(finished_at))
			campaign.reward = reward
			campaign.user = request.user
			campaign.merchant_uid = None
			campaign.company_name = company_name
		

			if request.user.plan_type != 0 and request.user.plan_at > datetime.now():
				if request.user.plan_type == 1:
					campaign.is_item = True
				elif request.user.plan_type == 2:
					campaign.is_item = True
					campaign.is_recommend = True
			else:
				if item != 'default':
					campaign.is_item = True
					if item == 'recommend':
						campaign.is_recommend = True
			campaign.save()
	
			campaign = GigCampaign.objects.get(pk=campaign.pk)
			campaign.merchant_uid = str(datetime.now().strftime('%Y%m%d')) + str(campaign.pk) + str(random.randint(10000,99999))
			campaign.save()

			if request.user.is_superuser:
				shipping_address = UserShippingAddress.objects.get(pk=1)

				for i in range(random.randrange(50)):
					campaign_offer = GigCampaignOffer()
					campaign_offer.campaign = campaign
					campaign_offer.user = request.user
					campaign_offer.shipping_address = shipping_address
					campaign_offer.appeal = 'appeal'
					campaign_offer.sns_url = 'sns_url'
					campaign_offer.save()
			if request.user.plan_at > datetime.now():
				result = '200'
				result_text = "등록이 완료되었습니다."
				next_url = resolve_url('UserCampaign')
			else:
				result = '200'
				result_text = "등록이 완료되었습니다.<br>결제창으로 이동합니다."
				next_url = resolve_url('CampaignPay', campaign.pk)
		except Exception as e:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
			next_url = ''

		result = {'result': result, 'result_text': result_text, "next_url":next_url}
		return JsonResponse(result)
	else:
		if not request.user.full_name or request.user.birth_year is None or not request.user.phone_number:
			message = "모집 시 이름, 나이, 전화번호 정보가 필요합니다.<br>정보 수정 후 다시 시도해 주세요."
			next_url = resolve_url(user_profile)
		else:
			message = None
			next_url = None

		if request.user.plan_type != 0 and request.user.plan_at < datetime.now():
			request.user.plan_type = 0
			request.user.save()

		channel_list = ["네이버블로그", "인스타그램", "유튜브", "카페", "네이버포스트", "기타"]

		return render(request, 'gig/campaign/campaign_write.html',{"seo":seo, "channel_list":channel_list, "message":message, "next_url":next_url})


@login_required(login_url=user_login)
def campaign_pay(request, campaign_id):
	try:
		before_pay_campaign = GigCampaign.objects.get(pk=campaign_id)
	except:
		return redirect("Index")

	if request.method == "POST":
		merchant_uid = request.POST.get("merchant_uid")
		pay_method = request.POST.get("pay_method")
		use_point = int(re.sub(r'[^0-9]', '', str(request.POST.get('use_point'))))

		payment_json_data = payment_data(merchant_uid)


		if before_pay_campaign.merchant_uid == merchant_uid:
			pay_amount = before_pay_campaign.pay_amount - use_point

				
			if payment_json_data["amount"] == pay_amount:
				if AddUserPointLog(request.user, '캠페인 등록', -use_point):
					if payment_check(merchant_uid, pay_amount):
						result = '200'
						result_text = "결제가 완료되었습니다."
						MessageSender(request.user, f"캠페인 등록이 완료되었습니다.",resolve_url('CampaignDetail', campaign_id))
					elif pay_method == 'vbank':
						
						vbank_holder = payment_json_data["vbank_holder"]
						vbank_name = payment_json_data["vbank_name"]
						vbank_num = payment_json_data["vbank_num"]
						SmsSender(
							phone_number = request.user.phone_number,
							type = 'LMS',
							content = f'[콘디]\n국내 1위 체험단 리뷰 서비스 콘디를 이용해주셔서 감사합니다.\n\n요청하신 전용 입금계좌 안내해드립니다.\n\n예금주:{vbank_holder}\n은행:{vbank_name}\n계좌번호:{vbank_num}\n금액:{pay_amount}원\n\n감사합니다.'
						)
						result = '200'
						result_text = "입금계좌번호를 등록하신 연락처와 쪽지로 보내드렸습니다.<br>입금 기간내에 입금 바랍니다."
						MessageSender(request.user, f"입금계좌안내 {vbank_holder} / {vbank_name} / {vbank_num}", None)
					else:
						result = '200'
						result_text = "결제요청이 완료되었습니다.<br>결제를 완료해주세요."
						MessageSender(request.user, f"결제요청이 완료되었습니다. 결제를 완료해주세요.", None)
						
					result = {'result': result, 'result_text': result_text, "next_url":resolve_url("UserCampaign")}
					return JsonResponse(result)

				else:
					result = '201'
					result_text = "알수없는 오류입니다. 다시시도 해주세요."
			else:
				result = '201'
				result_text = "알수없는 오류입니다. 다시시도 해주세요."
		else:
			result = '201'
			result_text = "알수없는 오류입니다. 다시시도 해주세요."


		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	
	else:
		seo = {
			'title': "결제하기 - 콘디",
		}
		
		item_price = 0
		if before_pay_campaign.is_item:
			item_price = item_price+10000
			if before_pay_campaign.is_recommend:
				item_price = item_price+20000

		recruit_day = (before_pay_campaign.finished_at - before_pay_campaign.started_at).days
		return render(request, 'gig/campaign/campaign_pay.html',{"seo":seo,"before_pay_campaign":before_pay_campaign, "item_price":item_price,"recruit_day":recruit_day})


@login_required(login_url=user_login)
def campaign_update(request, campaign_id):
	seo = {
		'title': "캠페인 수정 - 콘디",
	}

	try:
		campaign = GigCampaign.objects.get(pk=campaign_id, user=request.user)
	except:
		return redirect(user_login)

	if request.method == 'POST':
		campaign_type = request.POST.get("campaign_type")
		category = request.POST.get("category")
		try:
			thumbnail = request.FILES['campaign_img']
		except:
			thumbnail = None
		subject = request.POST.get("subject")
		provide = request.POST.get("provide")
		guide_line = request.POST.get("guide_line")
		keyword = request.POST.get("keyword")
		product_url = request.POST.get("product_url")
		channel = ",".join(request.POST.getlist("channel[]"))
			
		try:
			campaign.campaign_type = campaign_type
			campaign.category = category
			campaign.subject = subject
			campaign.channel = channel
			if thumbnail is not None:
				campaign.thumbnail = thumbnail
			campaign.provide = provide
			campaign.guide_line = guide_line
			campaign.keyword = keyword
			campaign.product_url = product_url
			campaign.save()
			result = '200'
			result_text = '수정이 완료되었습니다.'
		except:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		channel_list = ["네이버블로그", "인스타그램", "유튜브", "카페", "네이버포스트", "기타"]
		return render(request, 'gig/campaign/campaign_update.html', {"seo":seo,"channel_list":channel_list, "campaign_update":campaign})


def campaign_detail(request, campaign_id):
	try:
		campaign = GigCampaign.objects.get(pk=campaign_id)
	except:
		return redirect('/')

	seo = {
		'title': f"{campaign.subject} - 콘디",
		'description': f"{campaign.subject},{campaign.provide[0:60]}",
	}

	try:
		campaign_offer = GigCampaignOffer.objects.get(campaign=campaign_id, user=request.user)
	except:
		campaign_offer = None
	
	q = Q()
	q &= Q(is_paid = True)
	q &= Q(is_item = True)
	q &= Q(is_recommend = True)
	q &= Q(finished_at__gte=datetime.now())
	recommend_campaign_list =  GigCampaign.objects.filter(q).order_by(
		Case(
			When(pk=132),
			When(pk=117), 
			When(pk=129), 
			When(pk=124), 
			When(pk=103), 
		default=0),
		"-id",
	)

	try:
		campaign_offer_picked = GigCampaignOffer.objects.get(campaign=campaign_id, user=request.user)
	except:
		campaign_offer_picked = None

	q = Q()
	q &= Q(campaign_id = campaign_id)
	q &= Q(is_picked = True)
	campaign_picked_count = GigCampaignOffer.objects.filter(q).count()


	return render(request, 'gig/campaign/campaign_detail.html', {"seo":seo, "campaign_detail":campaign, "campaign_offer":campaign_offer, "recommend_campaign_list":recommend_campaign_list, "campaign_offer_picked":campaign_offer_picked, "campaign_picked_count":campaign_picked_count})


@login_required(login_url=user_login)
def campaign_delete(request, campaign_id):
	try:
		campaign = GigCampaign.objects.get(pk=campaign_id, user=request.user)
	except:
		campaign = None

	if campaign is not None:
		if payment_refund(campaign.merchant_uid,'캠페인 환불 요청'):
			campaign.delete()
			MessageSender(request.user, f"캠페인 환불이 완료되었습니다..",resolve_url("Index"))
			result = '200'
			result_text = '삭제가 완료되었습니다.'
		else:
			result = '201'
			result_text = '관리자에게 문의바랍니다.'
	else:
		result = '201'
		result_text = '알수없는 오류입니다. 다시시도 해주세요.'

	result = {'result': result, 'result_text': result_text}
	return JsonResponse(result)


@login_required(login_url=user_login)
def campaign_offer(request,campaign_id):
	if request.method == 'POST':
		shipping_address_id = request.POST.get("shipping_address")
		appeal = request.POST.get("appeal")
		sns_url = request.POST.get("sns_url")

		try:
			shipping_address = UserShippingAddress.objects.get(pk=shipping_address_id)
		except:
			shipping_address = None

		try:
			campaign = GigCampaign.objects.get(pk=campaign_id)
		except:
			campaign = None

		if campaign is not None:
			if request.user in campaign.offer_user.all():
				campaign.offer_user.remove(request.user)
				result = '200'
				result_text = "캠페인 신청 취소가 완료되었습니다."
			else:
				if shipping_address is not None:
					campaign_offer = GigCampaignOffer()
					campaign_offer.campaign = campaign
					campaign_offer.user = request.user
					campaign_offer.shipping_address = shipping_address
					campaign_offer.appeal = appeal
					campaign_offer.sns_url = sns_url
					campaign_offer.save()

					MessageSender(campaign_offer.campaign.user, f"{campaign_offer.campaign.subject} 에 새로운 체험단 요청이 있습니다.",resolve_url("CampaignDetail", campaign_offer.campaign.id))
					if campaign_offer.campaign.user.is_superuser:
						admin_campaign_list = [132, 129, 124, 117]
						if campaign_offer.campaign.id in admin_campaign_list:
							SmsSender(
								phone_number = campaign_offer.campaign.user.phone_number,
								type = 'LMS',
								content = f'[콘디]\n국내 1위 체험단 리뷰 서비스 콘디를 이용해주셔서 감사합니다.\n\n"{campaign_offer.campaign.subject}" 에 새로운 체험단 요청이 있습니다.\n\n감사합니다.'
							)
					else:
						SmsSender(
							phone_number = campaign_offer.campaign.user.phone_number,
							type = 'LMS',
							content = f'[콘디]\n국내 1위 체험단 리뷰 서비스 콘디를 이용해주셔서 감사합니다.\n\n"{campaign_offer.campaign.subject}" 에 새로운 체험단 요청이 있습니다.\n\n감사합니다.'
						)

					result = '200'
					result_text = "캠페인 신청이 완료되었습니다."
				else:
					result = '201'
					result_text = '배송지를 추가해주세요.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)
	


def campaign_favorite(request):
	if not request.user.is_authenticated: #로그인 상태면
		result = '201'
		result_text = '로그인이 필요합니다.'
		
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)   
	if request.method == 'POST':
		try:
			campaign = GigCampaign.objects.get(id=request.POST.get("campaign_id"))
		except:
			campaign = None

		
		if campaign is not None:
			if request.user in campaign.favorite_user.all():
				campaign.favorite_user.remove(request.user)
				result = '200'
				result_text = False #좋아요 삭제
			else:
				campaign.favorite_user.add(request.user)
				result = '200'
				result_text = True #좋아요 추가
				request.user.blog_count += 1
				request.user.save()
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		
	else:
		result = '201'
		result_text = '알수없는 오류입니다. 다시시도 해주세요.'
	result = {'result': result, 'result_text': result_text}
	return JsonResponse(result)

@login_required(login_url=user_login)
def campaign_pick(request, campaign_id):
	seo = {
		'title': "체험단 선정 - 콘디",
	}
	q = Q()
	q &= Q(campaign_id = campaign_id)
	campaign_offer_list = GigCampaignOffer.objects.filter(q).order_by("-is_picked","-id")
	q &= Q(is_picked = True)
	campaign_picked_count = GigCampaignOffer.objects.filter(q).count()

	try:
		is_mine = campaign_offer_list[0].campaign.user
	except:
		is_mine = None

	if is_mine != request.user:
		return redirect(index)

	if request.method == 'POST':
		offer_id = request.POST.get("offer_id")

		try:
			campaign_offer = GigCampaignOffer.objects.get(id=offer_id)
		except:
			campaign_offer = None
		
		if campaign_offer is not None:
			if campaign_picked_count < campaign_offer.campaign.limit_offer:
				try:
					if campaign_offer.is_picked:
						campaign_offer.is_picked = False
						campaign_offer.save()
						MessageSender(campaign_offer.user, f"{campaign_offer.campaign.subject} 선정된 체험단에서 취소되었습니다.",resolve_url("CampaignDetail", campaign_offer.campaign.id))
						print(campaign_offer.campaign)
						SmsSender(
							phone_number = campaign_offer.user.phone_number,
							type = 'LMS',
							content = f'[콘디]\n국내 1위 체험단 리뷰 서비스 콘디를 이용해주셔서 감사합니다.\n\n"{campaign_offer.campaign.subject}" 선정된 체험단에서 취소되었습니다.\n\n감사합니다.'
						)
						result = '200'
						result_text = '체험단 취소가 완료되었습니다.'
					else:
						campaign_offer.is_picked = True
						campaign_offer.save()
						MessageSender(campaign_offer.user, f"{campaign_offer.campaign.subject} 체험단에 선정되었습니다.",resolve_url("CampaignDetail", campaign_offer.campaign.id))
						print(campaign_offer.campaign)
						SmsSender(
							phone_number = campaign_offer.user.phone_number,
							type = 'LMS',
							content = f'[콘디]\n국내 1위 체험단 리뷰 서비스 콘디를 이용해주셔서 감사합니다.\n\n"{campaign_offer.campaign.subject}" 체험단에 선정되었습니다.\n담당자와 연락후 리뷰작성 바랍니다.\n담당자 연락처 : {campaign_offer.campaign.user.phone_number}\n\n감사합니다.'
						)
						result = '200'
						result_text = '체험단 선정이 완료되었습니다.'
				except Exception as e:
					print(e)
					result = '201'
					result_text = '알수없는 오류입니다. 다시시도 해주세요.'
			else:
				result = '201'
				result_text = '더이상 선정할수 없습니다.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return render(request, 'gig/campaign/campaign_pick.html',{"seo":seo, "campaign_offer_list":campaign_offer_list,"campaign_picked_count":campaign_picked_count})


@login_required(login_url=user_login)
def campaign_pick_export(request, campaign_id):
	q = Q()
	q &= Q(campaign_id = campaign_id)
	campaign_offer_list = GigCampaignOffer.objects.filter(q).values_list('user__nickname', 'appeal', 'sns_url', 'is_picked').order_by("-is_picked","-id")

	try:
		campaign = GigCampaign.objects.get(pk=campaign_id, user=request.user)
	except:
		campaign = None

	if campaign is None:
		return redirect(index)

	file_name = urllib.parse.quote(str(f"{campaign.subject} 체험단 리스트 ").encode('utf-8'))

	response = HttpResponse(content_type="application/vnd.ms-excel")
	response["Content-Disposition"] = f'attachment;filename*=UTF-8\'\'{file_name}.xls' 
	wb = xlwt.Workbook(encoding='ansi') #encoding은 ansi로 해준다.
	ws = wb.add_sheet('신청자') #시트 추가
	
	row_num = 0
	col_names = ['닉네임', '각오', 'SNS주소', '선정여부']
	
	#열이름을 첫번째 행에 추가 시켜준다.
	for idx, col_name in enumerate(col_names):
		ws.write(row_num, idx, col_name)
			
	
	#유저정보를 한줄씩 작성한다.
	for campaign_offer in campaign_offer_list:
		row_num +=1
		for col_num, attr in enumerate(campaign_offer):
			ws.write(row_num, col_num, attr)
					
	wb.save(response)
	
	return response

	
@login_required(login_url=user_login)
def campaign_review(request,campaign_id):
	try:
		campaign_offer = GigCampaignOffer.objects.get(user=request.user,campaign=campaign_id,is_picked=True)
	except:
		campaign_offer = None
	
	if campaign_offer is not None:
		review_url = request.POST.get("review_url")
		try:
			campaign_review = GigCampaignReview()
			campaign_review.offer = campaign_offer
			campaign_review.review_url = review_url
			campaign_review.save()
			MessageSender(campaign_offer.campaign.user, f"{campaign_offer.campaign.subject} 리뷰가 등록되었습니다.",resolve_url("CampaignPick", campaign_offer.campaign.id))
			SmsSender(
				phone_number = campaign_offer.campaign.user.phone_number,
				type = 'LMS',
				content = f'[콘디]\n국내 1위 체험단 리뷰 서비스 콘디를 이용해주셔서 감사합니다.\n\n"{campaign_offer.campaign.subject}" 리뷰가 등록되었습니다.\n확인후 컨펌바랍니다.\n\n닉네임 : {campaign_offer.user.nickname}\n\n감사합니다.'
			)
			result = '200'
			result_text = '리뷰등록이 완료되었습니다.'
		except Exception as e:
			print(e)
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect(index)

@login_required(login_url=user_login)
def campaign_confirm(request,review_id):
	try:
		campaign_review = GigCampaignReview.objects.get(pk=review_id)
	except:
		campaign_review = None

	if campaign_review.offer.campaign.user == request.user:
		try:
			campaign_review.is_confirm = True
			campaign_review.save()
			if campaign_review.offer.campaign.reward > 0:
				if campaign_review.offer.campaign.id != 132:
					reward = campaign_review.offer.campaign.reward * 0.8
					AddUserPointLog(campaign_review.offer.user, f"{campaign_review.offer.campaign.subject}의 리워드", reward)
			MessageSender(campaign_review.offer.user, f"{campaign_review.offer.campaign.subject} 리뷰 확인이 완료되었습니다.",resolve_url("CampaignDetail", campaign_review.offer.campaign.id))
			MessageSender(campaign_review.offer.campaign.user, f"{campaign_review.offer.campaign.subject} 리뷰 확인이 완료되었습니다.",resolve_url("CampaignDetail", campaign_review.offer.campaign.id))
			result = '200'
			result_text = '리뷰 확인이 완료되었습니다.'
		except Exception as e:
			print(e)
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
	else:
		result = '201'
		result_text = '알수없는 오류입니다. 다시시도 해주세요.'

	result = {'result': result, 'result_text': result_text}
	return JsonResponse(result)