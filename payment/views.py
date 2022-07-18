from django.shortcuts import resolve_url
from iamport import Iamport
from django.http import JsonResponse,HttpResponse
from .models import Payment
from account.models import User
import json
from gig.models import GigCampaign
from django.db.models import Q
from util.views import AddUserPointLog,MessageSender,GetClientIp
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import re
from datetime import datetime, timedelta
# Create your views here.

iamport = Iamport(
	imp_key='', 
	imp_secret=''
)


def payment_data(merchant_uid):
	response = json.dumps(iamport.find(merchant_uid=merchant_uid))
	return json.loads(response)


@csrf_exempt
def pyment_webhook(request):
	merchant_uid = request.POST.get("merchant_uid")
	status = request.POST.get("status")
	white_list = ["52.78.100.19","52.78.48.223"]
	if not GetClientIp(request) in white_list:
		return HttpResponse("fuck you")

	try:
		payment_json_data = payment_data(merchant_uid)
	except:
		return HttpResponse("json 데이터 가져오기 오류")

	try:
		user = User.objects.get(email=payment_json_data['buyer_email'])
	except:
		user = None

	if user is not None:
		try:
			payment = Payment.objects.get(merchant_uid = merchant_uid)
		except:
			payment = None
		

		if payment is not None:
			if payment.pay_method == 'vbank' and payment.status == 'ready' :

				#가상계좌 입금들어온거 확인하는것
				if status == 'paid':
					payment.status = status
					payment.save()

					if json.loads(payment_json_data['custom_data'])["referral"] == "plan":

						if payment_json_data['amount'] == 49900:
							plan_type = 1
						elif payment_json_data['amount'] == 99900:
							plan_type = 2
						else:
							plan_type = 0

						user.plan_type = plan_type
						user.plan_at = datetime.now()+timedelta(days=32)
						user.save()

						
					elif json.loads(payment_json_data['custom_data'])["referral"] == "campaign":
						try:
							campaign = GigCampaign.objects.get(merchant_uid = merchant_uid)
						except:
							campaign = None

						if campaign is not None:
							campaign.is_paid = True
							campaign.save()

			else:
				Payment.objects.update_or_create(
					merchant_uid = merchant_uid,
					defaults     = {
							'user' : user,
							"pay_method" : payment_json_data['pay_method'],
							"pg": payment_json_data['pg_provider'],
							"paid_amount": payment_json_data['amount'],
							"merchant_uid": payment_json_data['merchant_uid'],
							"imp_uid": payment_json_data['imp_uid'],
							"pg_tid": payment_json_data['pg_tid'],
							"status": status,
							"referral": json.loads(payment_json_data['custom_data'])["referral"],
							"use_point": int(re.sub(r'[^0-9]', '', str(json.loads(payment_json_data['custom_data'])["use_point"]))),
					}
				)

		else:
			payment = Payment()
			payment.user = user
			payment.pay_method = payment_json_data['pay_method']
			payment.pg = payment_json_data['pg_provider']
			payment.paid_amount = payment_json_data['amount']
			payment.merchant_uid = payment_json_data['merchant_uid']
			payment.imp_uid = payment_json_data['imp_uid']
			payment.pg_tid = payment_json_data['pg_tid']
			payment.status = status
			payment.referral = json.loads(payment_json_data['custom_data'])["referral"]
			payment.use_point = int(re.sub(r'[^0-9]', '', str(json.loads(payment_json_data['custom_data'])["use_point"])))
			payment.save()

	return HttpResponse("성공")



def payment_check(merchant_uid, product_price):
	is_paid = iamport.is_paid(product_price, merchant_uid=merchant_uid)
	return is_paid


def payment_refund(merchant_uid, memo):
	try:
		iamport.cancel(memo, merchant_uid=merchant_uid)
		result = True
	except Iamport.ResponseError as e:
		print(e.code)
		print(e.message)  # 에러난 이유를 알 수 있음
		result = False
	except Iamport.HttpError as http_error:
		print(http_error.code)
		print(http_error.reason) # HTTP not 200 에러난 이유를 알 수 있음
		result = False

	return result
