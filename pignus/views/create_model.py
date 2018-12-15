from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
import os
import pandas as pd
import xgboost as xgb
import re
from django.shortcuts import get_object_or_404

from pignus.models import User, XGBoostModel, Session, Probability

@csrf_exempt
def create_model(request):
  print("create model request")
  directory_path = os.path.dirname(os.path.abspath(__file__))
  ai_models_path = directory_path + '/../ai_models/'

  login = request.GET.get('login')

  user = get_object_or_404(User, login=login)

  user_file_path = directory_path + '/../login_data/' + login + '/'
  list_of_files = get_csv_files(user_file_path)

  user_data_df = pd.DataFrame()

  for file in list_of_files:
    user_data_df = user_data_df.append(pd.read_csv(user_file_path+file),ignore_index=True)

  file_name = '10secs_aggregated_features'
  our_data_file_name = 'our_data_aggregated_features'
  our_test_data_file_name = 'aggregated_test_data'
  to_drop = []
  df = pd.read_csv(directory_path + '/../' + file_name + '.csv')
  our_data_df = pd.read_csv(directory_path + '/../' + our_data_file_name + '.csv')
  our_new_data_df = pd.read_csv(directory_path + '/../' + our_test_data_file_name + '.csv')

  our_data_df = our_data_df.append(our_new_data_df, ignore_index=True)
  our_data_df = our_data_df.append(user_data_df,ignore_index=True)
  df = df.append(our_data_df,ignore_index=True)

  makeUserTarget(df, login)

  to_drop = ['Subject', 'Mag_Z_mean','Mag_X_mean','Mag_Y_mean','Mag_Y_std','Mag_Z_std','Mag_X_std','Contact_size_mean','Pressure_mean','Pressure_std','Contact_size_std']

  clf = xgb.XGBClassifier(n_estimators=90, max_depth=9, random_state=31, colsample_bytree=0.6, colsample_bylevel=0.5, learning_rate=0.11, subsample=0.9)
  df = df.set_index(["SessionID", 'WindowNumber']).drop(to_drop, axis=1)
  df = df[sorted(list(df.columns))]
  x_train, y_train = df.drop("target", axis=1), df["target"]


  clf.fit(x_train, y_train)

  model_file_name = login + '.model.bin'
  clf.save_model(ai_models_path + model_file_name)

  xgboostmodel = XGBoostModel(user=user, file_path= model_file_name)
  xgboostmodel.save()

  return JsonResponse({'model_path': xgboostmodel.file_path, 'user_login': user.login})

def get_csv_files(path):
  list_aux = []
  for file in os.listdir(path):
    if file.endswith('.csv'):
      list_aux.append(file)
  return list_aux

def makeUserTarget(df, user):
  aux = []
  for _, row in df.iterrows():
    if user in str(row.SessionID):
        aux.append(1)
    else:
        aux.append(0)
  df['target'] = aux