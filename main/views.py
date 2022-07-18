from ast import expr_context
from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.conf import settings
from gig.models import GigCampaign
from django.db.models import Q, Case, When
from .models import *
import os
from django.http import JsonResponse
from bs4 import BeautifulSoup
import json
from datetime import datetime, timedelta
from django.contrib.auth.decorators import login_required
from multiprocessing import Process, Value
import requests
from urllib.parse import quote
from threading import Thread

def index(request):
	q = Q()
	q &= Q(is_paid = True)
	q &= Q(finished_at__gte=datetime.now())
	new_campaign_list =  GigCampaign.objects.filter(q).order_by(
		'-is_item', 
		"-id",
	)[0:4]

	q = Q()
	q &= Q(is_paid = True)
	q &= Q(is_recommend = True)
	q &= Q(finished_at__gte=datetime.now())
	recommend_campaign_list =  GigCampaign.objects.filter(q).order_by(
		Case(
			When(pk=132),
			When(pk=117), 
			When(pk=129), 
			When(pk=124), 
			When(pk=103), 
			When(pk=97), 
		default=0),
		"-id",
	)[0:16]

	q = Q()
	q &= Q(is_paid = True)
	q &= Q(is_item = True)
	q &= Q(finished_at__gte=datetime.now())
	top_campaign_list =  GigCampaign.objects.filter(q).order_by(
		Case(
			When(pk=132),
		default=0),
		"-id",
	)[0:3]


	return render(request, 'main/index.html' ,{"new_campaign_list":new_campaign_list, "recommend_campaign_list":recommend_campaign_list, "top_campaign_list":top_campaign_list})


def short_url(request,num):
	return redirect(index)



def robots(request):
	f = open(os.path.join(settings.BASE_DIR, 'robots.txt'), 'r')
	file_content = f.read()
	f.close()
	
	return HttpResponse(file_content, content_type="text/plain")



def privacy(request):
	seo = {
		'title': "개인정보 처리방침 - 콘디",
	}
	return render(request, 'main/privacy.html', {"seo":seo})


def terms_of_service(request):
	seo = {
		'title': "이용약관 - 콘디",
	}
	return render(request, 'main/terms_of_service.html', {"seo":seo})



@login_required(login_url=settings.LOGIN_URL)
def check_nblog(request):
	if request.method == 'POST':
		if request.user.blog_count >= 1 or request.user.plan_type != 0:
			nid = request.POST.get("nid")
			try:
				blog_info_res = requests.get(f"https://rss.blog.naver.com/{nid}.xml")
				content = blog_info_res.content
				
				soup = BeautifulSoup(content, "xml")
				blog_name = soup.find("title").get_text()
				blog_link = soup.find("link").get_text()
				blog_items = soup.find_all("item")
			except:
				result = '201'
				result_text = u'알수없는 오류입니다.<br>다시시도 해주세요.'

				result = {'result': result, 'result_text': result_text}
				return JsonResponse(result)


			try:
				nblog = BlogRank.objects.get(blog_link=blog_link)
			except:
				nblog = None
		
			if nblog is None or nblog.created_at < datetime.now()-timedelta(days=3):
				try:
					if len(blog_items) < 50:
						total_search_rank = Value('i',(50 - len(blog_items)) * 31)
					else:
						total_search_rank = Value('i', 0)

					procs = []
					for blog_item in blog_items:
						proc = Process(target=thread, args=(total_search_rank,blog_item,blog_link))
						procs.append(proc)
						proc.start()
					
					for proc in procs:
						proc.join()

					

					if total_search_rank.value < 1000:
						blog_rank = '최적'
					elif total_search_rank.value < 1500:
						blog_rank = '준최'
					else:
						blog_rank = '일반'

					result = '200'
					result_text = {
						"blog_rank": blog_rank,
						"search_rank": total_search_rank.value,
						"blog_name": blog_name,
						"blog_link": blog_link,
					}

					BlogRank.objects.update_or_create(
						blog_link = blog_link,
						defaults     = {
								'blog_name' : blog_name,
								'blog_rank' : blog_rank,
								'search_rank' : total_search_rank.value,
								'blog_link' : blog_link,
								'created_at' : datetime.now()
						}
					)

					if request.user.plan_type == 0:
						request.user.blog_count -= 1
						request.user.save()
					
				except Exception as e:
					print(e)
					result = '201'
					result_text = u'알수없는 오류입니다.<br>다시시도 해주세요.'
			else:
				result = '200'
				result_text = {
					"blog_rank": nblog.blog_rank,
					"search_rank": nblog.search_rank,
					"blog_name": nblog.blog_name,
					"blog_link": nblog.blog_link,
				}
		else:
			result = '201'
			result_text = u'이용가능 횟수가 없습니다.<br>캠페인에 좋아요를 눌러주시거나 이용플랜을 결제해주세요.'

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		seo = {
			'title': u"블로그진단 - 콘디",
			'description': f"블로그지수확인, 블로그 최적화 확인, 블로그 랭킹 확인, 블로그 검색 노출, 네이버 블로그 최적화",
		}

		if request.user.plan_type != 0 and request.user.plan_at < datetime.now():
			request.user.plan_type = 0
			request.user.save()

		return render(request, 'main/nblog_check.html', {"seo":seo})


def thread(total_search_rank, blog_item, blog_link):
	th1 = Thread(target=f, args=(total_search_rank, blog_item, blog_link))
	th1.start()
	th1.join()


def f(total_search_rank, blog_item, blog_link):
	keyword_list = blog_item.find("tag").text.split(",")

	for keyword in keyword_list:
		data = {
			"keyword" : keyword,
		}

		url = "https://newsoft.kr/keyword.php?action=c"
		res = requests.post(url, data=data)
		res.raise_for_status() # 문제시 프로그램 종료

	keyword = keyword_list[0]
	search_rank = 31

	if keyword is not None:
		url = "https://search.naver.com/search.naver?where=view&sm=tab_jum&query=" + quote(keyword)
		headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"}
		res = requests.get(url, headers=headers)
		res.raise_for_status() # 문제시 프로그램 종료
		soup = BeautifulSoup(res.text, "lxml") 

		posts = soup.find_all("li", attrs={"class":"bx _svp_item"})
		
		for search_rank, post in enumerate(posts,1):
			try:
				if post.find("a", class_=["sub_txt","sub_name"])["href"] == blog_link:
					break
			except:
				pass

	total_search_rank.value += search_rank