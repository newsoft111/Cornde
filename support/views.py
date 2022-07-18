from django.shortcuts import redirect, render
from account.views import user_login
from .models import SupportFaq
from django.db.models import Q
from util.views import EmailSender
from django.http import JsonResponse,HttpResponse
from django.contrib.auth.decorators import login_required
# Create your views here.

def faq(request):
	if request.GET.get("type") == 'biz':
		category_list = [
			"비즈니스 이용방법",
			"프로젝트 등록",
			"리뷰어 모집",
			"리뷰어 선정",
			"결과물 제출 확인",
			"결제 관리",
			"계정 관리",
		]
	else: #리뷰어 카테고라
		category_list = [
			"리뷰어 이용방법",
			"리뷰어 신청",
			"리뷰어 선정",
			"결과물 작성",
			"결과물 제출",
			"포인트 관리",
			"계정 관리",
			"기타",
		]
		

	q = Q()
	if request.GET.get("keyword"):
		q &= Q(subject__icontains=request.GET.get("keyword"))
	else:
		if request.GET.get("type") == "biz":
			q &= Q(target = 2)
		else:
			q &= Q(target = 1)

		if request.GET.get("category"):
			q &= Q(category = category_list[int(request.GET.get("category"))])

	
	if request.GET.get("category") or request.GET.get("keyword"):
		faq_list =  SupportFaq.objects.filter(q).order_by('-id')
	else:
		faq_list =  SupportFaq.objects.filter(q).order_by('-hit')[0:5]

	seo = {
		'title': "자주묻는질문 - 콘디",
	}
	return render(request, 'support/faq.html' ,{"seo":seo, "faq_list":faq_list, "category_list":category_list})


@login_required(login_url=user_login)
def faq_update(request,faq_id):
	if not request.user.is_superuser:
		return HttpResponse('잘못된 요청입니다.')

	try:
		faq = SupportFaq.objects.get(id=faq_id)
	except:
		faq = None

	if request.method == 'POST':
		try:
			faq.content = request.POST.get("faq")
			faq.save()

			result = '200'
			result_text = "수정이 완료되었습니다."
		except:
			result = '200'
			result_text = "알수없는 오류입니다. 다시시도 해주세요."
		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)
	else:
		return render(request, 'support/faq_update.html',{"faq":faq})

def qna(request):
	if not request.user.is_authenticated: #로그인 상태면
		return redirect(user_login)

	if request.method == 'POST':
		type = request.POST.get("type")
		content = request.POST.get("content")

		message = f"문의유형: {type}\r문의내용: {content}"
		EmailSender(
			email              = "cornde@cornde.com",
			subject = f'[콘디] {request.user.nickname}의 문의',
			message = message,
			mailType = None
		)

		result = '200'
		result_text = "문의등록이 완료되었습니다.<br>가입하신 이메일로 답변이 발송됩니다."
		

		result = {'result': result, 'result_text': result_text}
		return JsonResponse(result)

	else:
		seo = {
			'title': "1대1 고객문의 - 콘디",
		}
		return render(request, 'support/qna.html' ,{"seo":seo})

	

def price(request):
	seo = {
		'title': "가격안내 - 콘디",
	}
	return render(request, 'support/price.html', {"seo":seo})
