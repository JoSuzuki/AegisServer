from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
import pandas as pd
import xgboost as xgb
import os

from .models import User, XGBoostModel, Session, Probability

# Create your views here.
def single_request_login(request):
  directory_path = os.path.dirname(os.path.abspath(__file__))
  ai_models_path = directory_path + '/ai_models/'

  login = request.GET.get('login')

  user = get_object_or_404(User, login=login)

  clf = xgb.XGBClassifier(n_estimators=90, max_depth=4, random_state=31, colsample_bytree=0.5, colsample_bylevel=0.5, learning_rate=0.09, subsample=0.9) 
  clf.load_model(ai_models_path + user.xgboostmodel.file_path)
  x_train = pd.read_csv(ai_models_path + 'x_train.csv')
  to_drop = []
  x_train = x_train.set_index(["SessionID", 'WindowNumber']).drop(to_drop, axis=1)

  i_pred_proba = clf.predict_proba(x_train)
  print(i_pred_proba)
  mean_prob = i_pred_proba.mean()

  return JsonResponse({'auth': float(mean_prob)})