import requests
from django.core.mail import EmailMessage
from account.models import UserPoint, UserMessage
from django.shortcuts import render, redirect
from django.http import JsonResponse
from random import randint
from .models import *
# Create your views here.
import re

def EmailSender(email, subject, message, mailType):
	if email is not None:
			subject = subject
			message = message
			mail = EmailMessage(subject, message, to=[email])
			if mailType is not None:
				mail.content_subtype = mailType
			mail.send()
			result = '200'
	else:
			result = '201'
	return result


def SmsSender(phone_number,type, content):
	if phone_number is not None:
		url = 'https://api-sens.ncloud.com/v1/sms/services/ncp:sms:kr::/messages/'
		headers = {
				'Content-Type': 'application/json; charset=utf-8',
				'x-ncp-auth-key': '',
				'x-ncp-service-secret':'',
		}

		data = {
				'type':type,
				'contentType':'COMM',
				'countryCode':'82',
				'from':'',
				'to':[
						f'{phone_number}',
				],
				'content':content
		}
		requests.post(url, headers=headers, json=data)
		result = '200'
	else:
		result = '201'
	return result


def MessageSender(user,subject,next_url):
	user_message = UserMessage()
	user_message.user = user
	user_message.subject = subject
	user_message.next_url = next_url
	user_message.save()


def AddUserPointLog(user, place, amount):
	try:
		user.point = user.point + amount
		user.save()
		result = True
	except:
		result = False
	
	if result and amount != 0:
		point_log = UserPoint() #포인트 내역 추가
		point_log.user = user
		point_log.place = place
		point_log.amount = amount
		point_log.save()

	return result


def GetClientIp(request):
	x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
	if x_forwarded_for:
			ip = x_forwarded_for.split(',')[0]
	else:
			ip = request.META.get('REMOTE_ADDR')
	return ip
