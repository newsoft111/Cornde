from account.models import UserMessage
from django.db.models import Q

def check_new_message(request):
	try:
		q = Q()
		q &= Q(user = request.user)
		q &= Q(is_read = False)
		unread_message =  UserMessage.objects.filter(q).count()
	except:
		unread_message = None
		
	return {'unread_message': unread_message}
	