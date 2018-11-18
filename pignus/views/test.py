from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from pignus import data_treatment

@csrf_exempt
def test(request):

  print('request.body' + str(request.body))
  print('request.POST' + str(request.POST))
  # a = json.loads(request.body)
  # print(a["login"])

  return JsonResponse({'auth': float(1)})