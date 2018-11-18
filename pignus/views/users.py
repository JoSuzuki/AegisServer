from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from pignus.models import User, XGBoostModel, Session, Probability

@csrf_exempt
def users(request):
  print("users request")
  users = list(User.objects.all().values())

  users = list(map((lambda x: x["login"]), users))
  return JsonResponse(users, safe=False)