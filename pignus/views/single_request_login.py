import os
import json
from django.shortcuts import get_object_or_404
import pandas as pd
import xgboost as xgb
from pignus import data_treatment
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from io import StringIO

from pignus.models import User, XGBoostModel, Session, Probability

@csrf_exempt
def single_request_login(request):
  directory_path = os.path.dirname(os.path.abspath(__file__))
  ai_models_path = directory_path + '/../ai_models/'

  post = json.loads(request.body)

  df_accelerometer = mapStringToMotionDf(post["Accelerometer"])
  df_gyroscope = mapStringToMotionDf(post["Gyroscope"])
  df_magnetometer = mapStringToMotionDf(post["Magnetometer"])
  df_keyPressEvent = mapStringToKeyPressDf(post["KeyPress"])
  df_keyboardTouchEvent = mapStringToKeyboardTouchDf(post["KeyboardTouch"])

  df_features = data_treatment.frameSession(df_accelerometer, df_gyroscope, df_magnetometer, df_keyPressEvent, df_keyboardTouchEvent)
  to_drop = ['Mag_Z_mean','Mag_X_mean','Mag_Y_mean','Mag_Y_std','Mag_Z_std','Mag_X_std','Contact_size_mean','Pressure_mean','Pressure_std','Contact_size_std']
  df_features = df_features.set_index(["SessionID", 'WindowNumber']).drop(to_drop, axis=1)
  df_features = df_features[sorted(list(df_features.columns))]

  login = post['Login']
  print(login)

  user = get_object_or_404(User, login=login)
  clf = xgb.XGBClassifier(n_estimators=90, max_depth=9, random_state=31, colsample_bytree=0.6, colsample_bylevel=0.5, learning_rate=0.11, subsample=0.9)
  print('User model loaded:' + user.xgboostmodel.file_path)
  clf.load_model(ai_models_path + user.xgboostmodel.file_path)

  df_features.to_csv(directory_path +'/weird.csv', index=True)
  print(df_features.head())
  predict = clf.predict_proba(df_features)
  print(predict[:, 1])
  predict = predict[:, 1]
  mean_prob = predict.mean()

  return JsonResponse({'auth': float(mean_prob)})


def mapStringToMotionDf(string):
  return pd.read_csv(StringIO(string), names=['Systime','EventTime','ActivityID','X','Y','Z','Phone_orientation'])

def mapStringToKeyPressDf(string):
  return pd.read_csv(StringIO(string), names=['Systime','PressTime','PressType','ActivityID','KeyID','Phone_orientation'])

def mapStringToKeyboardTouchDf(string):
  return pd.read_csv(StringIO(string), names=['Systime','EventTime','ActivityID','Pointer_count','PointerID','ActionID','X','Y','Pressure','Contact_size','Phone_orientation'])

