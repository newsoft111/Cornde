import re, random
from numpy import PINF
from django.shortcuts import render, redirect, resolve_url
from django.http import JsonResponse
from django.contrib import auth
from .models import *
from util.views import EmailSender, AddUserPointLog, SmsSender,MessageSender
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .tokens import account_activation_token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.hashers import check_password
from django.urls import reverse
from django.db.models import Q
from django.core.paginator import Paginator
from django.core.files.base import ContentFile
import base64
from random import randint
from django.contrib.auth.decorators import login_required
from gig.models import GigCampaign,GigCampaignFavorite,GigCampaignOffer
from datetime import datetime, timedelta
from django.conf import settings
from payment.views import payment_refund,payment_check, payment_data
# Create your views here.

def user_login(request):
	seo = {
		'title': "로그인 - 콘디",
	}
	if request.user.is_authenticated: #로그인 상태면
		return redirect("Index")
	if request.method == 'POST':
		email=request.POST.get('email')
		password=request.POST.get('password')

		user = auth.authenticate(request, email=email, password=password)
		print(user)
		if user is not None:
			if user.is_verify:
				if user.is_active:
					auth.login(request, user)
					
					if request.user.plan_type != 0 and request.user.plan_at < datetime.now():
						request.user.plan_type = 0
						request.user.save()
					result = '200'
					result_text = '로그인 성공'
				else:
					result = '201'
					result_text = '탈퇴한 계정입니다.'	
			else:
				verify_email_url = reverse('VerifyEmail')
				result = '201'
				result_text = f"이메일 인증을 완료해주세요.<a href='{verify_email_url}' class='w-100 btn btn-primary mt-3'>인증메일 다시받기</a>"
		else:
			result = '201'
			result_text = '아이디와 비밀번호를 정확히 입력해 주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)        
	else:
		return render(request, 'account/login.html',{"seo":seo})

def user_logout(request):
	auth.logout(request)
	return redirect("Index")

def user_join(request):
	seo = {
		'title': "회원가입 - 콘디",
	}
	if request.user.is_authenticated:
		return redirect("Index")
	if request.method == 'POST':
		email=request.POST.get('email')
		nickname=request.POST.get('nickname')
		password=request.POST.get('password')

		try:
			_email = User.objects.get(email=email)
		except:
			_email = None
		try:
			_nickname = User.objects.get(nickname=nickname)
		except:
			_nickname = None

		if _email is None:
			if _nickname is None:
				if request.POST['password'] ==request.POST['password2']:
					user = User.objects.create_user(
																		email=email,
																		nickname=nickname,
																		password=password,
																	)
					
					if send_auth_mail(email):
						result = '200'
						result_text = "회원가입이 완료되었습니다.<br>가입하신 이메일 주소로 인증 메일을 보내드렸습니다.<br>이메일 인증을 한 후에 정상적인 서비스 이용이 가능합니다."
						MessageSender(user, f"콘디 회원이 되셨습니다.",resolve_url("CampaignWrite"))
					else:
						result = '201'
						result_text = '알수없는 오류입니다.<br>다시시도 해주세요.'
				else:
					result = '201'
					result_text = '비밀번호가 일치하지 않습니다.'
			else:
				result = '201'
				result_text = '입력한 닉네임은 이미 사용 중입니다.'
		else:
			result = '201'
			result_text = '입력한 이메일은 이미 사용 중입니다.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)

	else:
		return render(request, 'account/join.html', {"seo":seo})

def join_confirm(request, uidb64, token):
	try:
			uid = force_str(urlsafe_base64_decode(uidb64))
			user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
			user = None

	if user is not None:
		if account_activation_token.check_token(user, token):
			user.is_verify = True
			user.save()
			auth.login(request, user)
			message = "인증이 완료되었습니다."
		else:
			message = "이미 인증을 완료했습니다."
	else:
		message = "알수없는 오류입니다. 다시시도 해주세요."
	return render(request, 'main/index.html', {"message":message})


def verify_email(request):
	if request.user.is_authenticated:
		return redirect("Index")
	if request.method == 'POST':
		email=request.POST.get('email')

		try:
			_email = User.objects.get(email=email, is_verify=False)
		except:
			_email = None

		if _email is not None and send_auth_mail(email):
			result = '200'
			result_text = f"{email}로 인증 메일을 보내드렸습니다.<br>이메일 인증을 한 후에 정상적인 서비스 이용이 가능합니다."
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)

	else:
		return render(request, 'account/verify_email.html')


def find_passwd(request):
	seo = {
		'title': "비밀번호 재설정 - 콘디",
	}
	if request.user.is_authenticated: #로그인 상태면
		return redirect("Index")
	if request.method == 'POST':
		email = request.POST.get('email')
		try:
			user = User.objects.get(email = email)
		except:
			user = None

		if user is not None:
			emailContent = render_to_string('email/reset_password.html',{
					'user': user,
					'domain': settings.CURRENT_URL,
					'uid': urlsafe_base64_encode(force_bytes(user.pk)),
					'token': PasswordResetTokenGenerator().make_token(user),
			})

			_result = EmailSender(
				email              = email,
				subject = '[콘디] 비밀번호 재설정 안내 메일입니다.',
				message = emailContent,
				mailType = 'html'
			)
			
			if _result == '200':
				result = '200'
				result_text = '비밀번호 재설정 메일이 전송되었습니다.<br>메일함을 확인해주세요.'
			else:
				result = '201'
				result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		else:
			result = '201'
			result_text = '등록되지 않은 이메일 입니다.'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)   
	else:
		return render(request, 'account/find_passwd.html', {"seo":seo})



def reset_passwd(request, uidb64, token):
	try:
		uid = force_str(urlsafe_base64_decode(uidb64))
		user = User.objects.get(pk=uid)
	except(TypeError, ValueError, OverflowError, User.DoesNotExist):
		user = None

	if user is not None:
		if PasswordResetTokenGenerator().check_token(user, token):
			if request.method == 'POST':
				new_password = request.POST.get("password")
				password_confirm = request.POST.get("password2")
				if new_password == password_confirm:
					user.set_password(new_password)
					user.save()
					result = '200'
					result_text = '비밀번호 변경이 완료되었습니다.<br>변경하신 비밀번호로 다시 로그인 해주시기 바랍니다.'
				else:
					result = '201'
					result_text = '입력하신 비밀번호가 동일하지 않습니다.'

				result = {'result': result, 'result_text': result_text}
				return JsonResponse(result)
			else:
				return render(request, 'account/reset_passwd.html')
		else:
			return render(request, 'main/index.html', {"message":"이미 사용된 인증메일 입니다."})
	else:
		return render(request, 'main/index.html', {"message":"알수없는 오류입니다. 다시시도 해주세요."})



def send_auth_mail(email):
	try:
		user = User.objects.get(email=email)
	except:
		user = None
	
	if user is not None:
		message = render_to_string('email/auth_email.html', {
			'user': user,
			'domain': settings.CURRENT_URL,
			'uid': urlsafe_base64_encode(force_bytes(user.pk)),
			'token': account_activation_token.make_token(user),
		})

		EmailSender(
			email              = email,
			subject = '[콘디] 이메일 주소 인증을 완료해 주세요.',
			message = message,
			mailType = 'html'
		)
		return True
	else:
		return False


@login_required(login_url=user_login)
def user_profile(request):
	seo = {
		'title': "개인정보 수정 - 콘디",
	}
	if request.method == 'POST':
		full_name = request.POST.get("full_name")
		birth_year = request.POST.get("birth_year")
		try:
			if full_name:
				request.user.full_name = full_name
			if birth_year:
				request.user.birth_year = birth_year
			request.user.save()
			result = '200'
			result_text = '변경이 완료되었습니다.'
		except:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요..'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		q = Q()
		q &= Q(user = request.user)
		shipping_address_lsit =  UserShippingAddress.objects.filter(q).order_by('-is_default', '-id')
		return render(request, 'account/mypage/user_profile.html', {"seo":seo, "shipping_address_lsit":shipping_address_lsit})


@login_required(login_url=user_login)
def change_passwd(request):
	if request.method == 'POST':
		current_password = request.POST.get("current_password")
		user = request.user
		if check_password(current_password,user.password):
			new_password = request.POST.get("password")
			password_confirm = request.POST.get("password2")
			if new_password == password_confirm:
				user.set_password(new_password)
				user.save()
				result = '200'
				result_text = '비밀번호 변경이 완료되었습니다.<br>변경하신 비밀번호로 다시 로그인 해주시기 바랍니다.'
				auth.logout(request)
			else:
				result = '201'
				result_text = '입력하신 비밀번호가 동일하지 않습니다.'
		else:
			result = '201'
			result_text = '현재 비밀번호가 옳바르지 않습니다.'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect("Index")


@login_required(login_url=user_login)
def add_shipping_address(request):
	if request.method == 'POST':
		address_name = request.POST.get("address_name")
		receiver = request.POST.get("receiver")
		zipcode = request.POST.get("zipcode")
		base_address = request.POST.get("base_address")
		detail_address = request.POST.get("detail_address")
		phone_number = request.POST.get("phone_number")
		is_default = request.POST.get("is_default")

		shipping_address = UserShippingAddress() #출금 내역 추가
		shipping_address.user = request.user
		shipping_address.address_name = address_name
		shipping_address.receiver = receiver
		shipping_address.zipcode = zipcode
		shipping_address.base_address = base_address
		shipping_address.detail_address = detail_address
		shipping_address.detail_address = detail_address
		shipping_address.phone_number = phone_number
		
		try:
			q = Q()
			q &= Q(user = request.user)
			shipping_address_list = UserShippingAddress.objects.filter(q)

			if shipping_address_list.count() < 1:
				is_default = True
			if is_default:
				shipping_address_list.update(is_default=False)
				shipping_address.is_default = True

			shipping_address.save()

			result = '200'
			result_text = '배송지 추가가 완료되었습니다.'
		except:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect("Index")


@login_required(login_url=user_login)
def del_shipping_address(request):
	if request.method == 'POST':
		address_id = request.POST.get("address_id")
		
		try:
			shipping_address = UserShippingAddress.objects.get(id=address_id)
		except:
			shipping_address = None
		
		if shipping_address is not None:
			shipping_address.delete()
			result = '200'
			result_text = '배송지 삭제가 완료되었습니다.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'
		
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect("Index")


@login_required(login_url=user_login)
def user_delete(request):
	seo = {
		'title': "회원탈퇴 - 콘디",
	}
	if request.method == 'POST':
		password = request.POST.get("password")
		try:
			user = User.objects.get(email=request.user.email)
		except:
			user = None

		if user is not None:
			if check_password(password,user.password):
				user.is_active = False
				user.save()
				result = '200'
				result_text = '회원탈퇴가 완료되었습니다.<br>이용해주셔서 감사합니다.'
				auth.logout(request)
			else:
				result = '200'
				result_text = '비밀번호를 정확히 입력해 주세요.'
		else:
			result = '201'
			result_text = '알수없는 오류입니다. 다시시도 해주세요.'


		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return render(request, 'account/mypage/user_delete.html', {"seo":seo})



@login_required(login_url=user_login)
def user_point(request):
	seo = {
		'title': "나의 포인트 - 콘디",
	}
	q = Q()
	q &= Q(user = request.user)
	point_list =  UserPoint.objects.filter(q).order_by('-id')
	page        = int(request.GET.get('p', 1))
	pagenator   = Paginator(point_list, 10)
	point_list = pagenator.get_page(page)

	bank_list = settings.CURRENT_BANK
	return render(request, 'account/mypage/user_point.html', {"seo":seo,"point_list":point_list, "bank_list":bank_list})


@login_required(login_url=user_login)
def user_withdraw(request):
	seo = {
		'title': "나의 포인트 - 콘디",
	}
	if request.method == 'POST':
		bank_name = request.POST.get("bank_name")
		bank_number = request.POST.get("bank_number")
		user_name = request.POST.get("user_name")

		user = request.user
		if user.point>9999:
			if bank_name and bank_number and user_name:
				withdraw_log = UserWithdraw() #출금 내역 추가
				withdraw_log.user = user
				withdraw_log.bank_account = f"{bank_name}|{bank_number}|{user_name}"
				withdraw_log.amount = -user.point
				withdraw_log.save()

				AddUserPointLog(user, '출금신청', -user.point)

				user.point = 0
				user.save()

				
				result = '200'
				result_text = '출금신청이 완료되었습니다.'
			else:
				result = '201'
				result_text = '은행정보를 입력해주세요.'
		else:
			result = '201'
			result_text = '출금은 10,000원 이상 부터 가능합니다.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		q = Q()
		q &= Q(user = request.user)
		withdraw_list =  UserWithdraw.objects.filter(q).order_by('-id')
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(withdraw_list, 10)
		withdraw_list = pagenator.get_page(page)

		point_list =  UserPoint.objects.filter(q).order_by('-id')
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(point_list, 10)
		point_list = pagenator.get_page(page)

		bank_list = settings.CURRENT_BANK
		return render(request, 'account/mypage/user_withdraw.html', {"seo":seo, "withdraw_list":withdraw_list, "point_list":point_list, "bank_list":bank_list})


@login_required(login_url=user_login)
def user_message(request):
	seo = {
		'title': "받은 메시지 - 콘디",
	}
	if request.method == 'POST':
		message_id = request.POST.get("message_id")
		try:
			message = UserMessage.objects.get(id=message_id)
		except:
			message = None

		if message is not None:
			message.is_read = True
			message.save()

		
			result = '200'
			result_text = '성공'
		else:
			result = '201'
			result_text = '잘못된 요청입니다.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		q = Q()
		q &= Q(user = request.user)
		message_list =  UserMessage.objects.filter(q).order_by('-id')
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(message_list, 10)
		message_list = pagenator.get_page(page)

		return render(request, 'account/mypage/user_message.html', {"seo":seo, "message_list":message_list})


@login_required(login_url=user_login)
def reset_user_message(request):
	if request.method == 'POST':
		try:
			q = Q()
			q &= Q(user = request.user)
			UserMessage.objects.filter(q).update(is_read=True)

			result = '200'
			result_text = '처리완료 되었습니다.'
		except:
			result = '201'
			result_text = '잘못된 요청입니다.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect("Index")


@login_required(login_url=user_login)
def change_user_avater(request):
	if request.method == 'POST':
		avater = request.POST.get('avater')

		format, imgstr = avater.split(';base64,') 
		ext = format.split('/')[-1] 
		rand_number = str(randint(100000, 999999))
		data = ContentFile(base64.b64decode(imgstr), name=rand_number + '.' + ext) # You can save this as file instance.

		try:
			request.user.avater = data
			request.user.save()
			result = '200'
			result_text = '이미지 변경이 완료되었습니다.'
		except:
			result = '201'
			result_text = '잘못된 요청입니다.'
		
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)

	else:
		return redirect("Index")


@login_required(login_url=user_login)
def user_campaign(request):
	seo = {
		'title': "나의 캠페인 - 콘디",
	}
	type = request.GET.get('type')
	if type == "1" or type is None:
		q = Q()
		q &= Q(user = request.user)
		my_campaign_list = GigCampaign.objects.filter(q).order_by("-id")
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(my_campaign_list, 9)
		my_campaign_list = pagenator.get_page(page)

		return render(request, 'account/mypage/user_my_campaign.html', {"seo":seo, "my_campaign_list":my_campaign_list})
	elif type == "2":
		q = Q()
		q &= Q(user = request.user)
		offer_campaign_list = GigCampaignOffer.objects.filter(q).order_by("-id")
		page        = int(request.GET.get('p', 1))
		pagenator   = Paginator(offer_campaign_list, 9)
		offer_campaign_list = pagenator.get_page(page)

		return render(request, 'account/mypage/user_offer_campaign.html', {"seo":seo, "offer_campaign_list":offer_campaign_list})
	else:
		return redirect("Index")



@login_required(login_url=user_login)
def user_favorite(request):
	seo = {
		'title': "관심 캠페인 - 콘디",
	}
	q = Q()
	q &= Q(user = request.user)
	favorite_campaign_list = GigCampaignFavorite.objects.filter(q).order_by("-id")
	print(favorite_campaign_list)
	page        = int(request.GET.get('p', 1))
	pagenator   = Paginator(favorite_campaign_list, 10)
	favorite_campaign_list = pagenator.get_page(page)

	return render(request, 'account/mypage/user_favorite.html', {"seo":seo, "favorite_campaign_list":favorite_campaign_list})


@login_required(login_url=user_login)
def user_plan(request):
	if request.method == 'POST':
		merchant_uid = request.POST.get("merchant_uid")
		pay_method = request.POST.get("pay_method")
		plan_type = request.POST.get("plan_type")

		payment_json_data = payment_data(merchant_uid)
		if plan_type == "1":
			pay_amount = 49900
		elif plan_type == "2":
			pay_amount = 99900
		else:
			pay_amount = "0"


		if payment_json_data["amount"] == pay_amount:
			if payment_check(merchant_uid, pay_amount):
				result = '200'
				result_text = "결제가 완료되었습니다."
				MessageSender(request.user, f"플랜 결제가 완료되었습니다.", None)

				request.user.plan_type = plan_type
				request.user.plan_at = datetime.now()+timedelta(days=32)
				request.user.save()
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
				MessageSender(request.user, f"입금계좌안내 예금주 : {vbank_holder} / 은행 : {vbank_name} / 계좌번호 : {vbank_num}", None)
			else:
				result = '200'
				result_text = "결제요청이 완료되었습니다.<br>결제를 완료해주세요."
				MessageSender(request.user, f"결제요청이 완료되었습니다. 결제를 완료해주세요.", None)
		else:
			result = '201'
			result_text = "알수없는 오류입니다. 다시시도 해주세요."
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		seo = {
			'title': "나의 플랜 - 콘디",
		}
		merchant_uid = str(datetime.now().strftime('%Y%m%d')) + str(request.user.pk) + str(random.randint(10000,99999))
		return render(request, 'account/mypage/user_plan.html', {"seo":seo, "merchant_uid":merchant_uid})



def user_review(request):
	seo = {
		'title': "나의 리뷰 - 콘디",
	}
	q = Q()
	q &= Q(user = request.user)
	q &= Q(is_picked = True)
	q &= ~Q(gigcampaignreview__review_url = None)
	my_review_list = GigCampaignOffer.objects.filter(q).order_by("-id")
	page        = int(request.GET.get('p', 1))
	pagenator   = Paginator(my_review_list, 10)
	my_review_list = pagenator.get_page(page)

	return render(request, 'account/mypage/user_my_review.html', {"seo":seo, "my_review_list":my_review_list})



def sms_code_send(request):
	if request.method == 'POST':
		try:
			phone_number = request.POST.get('phone_number')
			# 6자리 인증번호 랜덤 생성
			auth_number = str(randint(100000, 999999))
			# 같은 휴대전화 번호로 여러 번 인증할 수 있는데,
			# 이때마다 새로운 row를 생성해서 저장하면 안 되므로
			# 휴대전화 번호가 존재하는지 여부를 확인해서 존재한다면 update로 처리해 인증번호만 갈아끼워 저장한다.
			AuthMobile.objects.update_or_create(
					phone_number = phone_number,
					defaults     = {
							'phone_number'        : phone_number,
							'auth_number' : auth_number
					}
			)
			# 휴대전화번호와 인증번호를 담아 같은 클래스 내 send_verification 메소드를 호출한다.
			# member_phone과 verification_number가 send_verification 메소드의 인자가 된다.
			_result = SmsSender(
				phone_number = phone_number,
				type = 'SMS',
				content = f'[콘디]\n인증번호 [{auth_number}] 를 입력해주세요.'
			)

			if _result == '200':
				result = '200'
				result_text = '인증번호를 발송하였습니다.'
			else:
				result = '201'
				result_text = '알수없는 오류입니다.'

			result = {'result': result, 'result_text': result_text}
			return JsonResponse(result)
		except KeyError:
			return JsonResponse({'result': '201'})
	else:
		return redirect("Index")

	
def sms_code_check(request):
	if request.method == 'POST':
		phone_number = request.POST.get('phone_number')
		auth_number = re.sub(r'[^0-9]', '', request.POST.get('auth_code'))

		queryset = AuthMobile.objects.filter(phone_number=phone_number, auth_number=auth_number)
		count = queryset.count()
		if count > 0:
			request.user.phone_number = phone_number
			request.user.save()
			result = '200'
			result_text = '인증을 완료했습니다.'
		else:
			result = '201'
			result_text = '인증번호가 일치하지 않습니다.'
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return redirect("Index")
