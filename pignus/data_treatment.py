import pandas as pd
import numpy as np
import time

def createSkeleton(keyPressEvent_df):
  keyPressEvent_df['SessionID'] = keyPressEvent_df.ActivityID
  aux = keyPressEvent_df[['Systime','SessionID']].groupby('SessionID').agg([np.min,np.max]).Systime
  aux = aux.reset_index()
  bla = []
  step = 10000
  for _,row in aux.iterrows():
      i = 0
      t0 = row.amin
      while (t0+step < row.amax):
          aux_dict = {}
          aux_dict['SessionID'] = row.SessionID
          aux_dict['WindowNumber'] = i
          aux_dict['WindowStart'] = t0
          aux_dict['WindowEnd'] = t0+step
          t0 += step
          i += 1
          bla.append(aux_dict)
  return (pd.DataFrame(bla))

def windowDf(df,skeleton):
  aux_list = []
  last_session = -1
  last_windowNumber = -1
  last_windowEnd = -1
  count = 0
  j = 0
  for _,row in df.iterrows():
      if row.SessionID != last_session:
          skeletonWithSessionId = skeleton[skeleton.SessionID == row.SessionID]
          last_session = row.SessionID
      currentSystime = int(row.Systime)
      if currentSystime > last_windowEnd:
          final_df = skeletonWithSessionId[(skeletonWithSessionId.WindowStart <= currentSystime) & (skeletonWithSessionId.WindowEnd > currentSystime)]
          if final_df.empty:
              last_windowEnd = -1
              last_windowNumber = -1
          else:
              last_windowEnd = final_df.WindowEnd.values[0]
              last_windowNumber = final_df.WindowNumber.values[0]
      aux_list.append(last_windowNumber)
      count = count + 1
      j = j + 1
      if (j == 100000):
          j = 0
  df['WindowNumber'] = aux_list
  return df

def preProcessingMotion(df):
  df = df[df.WindowNumber != -1]
  grouped_df = df.groupby(['SessionID', 'WindowNumber']).agg({
    'X': {
      'X_mean':'mean',
      'X_std': 'std'
    },
    'Y': {
      'Y_mean':'mean',
      'Y_std':'std'
    },
    'Z': {
      'Z_mean':'mean',
      'Z_std':'std'
    }
  })
  grouped_df.columns = grouped_df.columns.droplevel()
  grouped_df = grouped_df.reset_index()
  return grouped_df

def get_deltas(df):
  deltas = []
  ultimo0 = 0
  ultimo1 = 0
  found0 = False
  found1 = False
  for _,row in df.iterrows():
    currentSystime = row.Systime
    if row.PressType == 0:
      if found1:
        deltas.append(currentSystime-ultimo1)
      else:
        deltas.append(None)
      ultimo0 = currentSystime
      found0 = True
    elif row.PressType == 1:
      if found0:
        deltas.append(currentSystime-ultimo0)
      else:
        deltas.append(None)
      ultimo1 = currentSystime
      found1 = True
  return deltas

def getPressTypeDelta(x):
  print(x == 1)

def preProcessingKeyPressEvent(df):
  df = df[df.WindowNumber != -1]
  aux = []
  for session in df.SessionID.unique():
    aux += get_deltas(df[df.SessionID == session])
  df['Deltas'] = aux
  grouped_df = df.groupby(['SessionID', 'WindowNumber']).agg({
    'PressType': {
      'Press_count': lambda x: x.count(),
    }
  })
  filteredByPressType1 = df[df.PressType == 1].copy()
  filteredByPressType0 = df[df.PressType == 0].copy()
  grouped0_df = filteredByPressType0.groupby(['SessionID', 'WindowNumber']).agg({
    'Deltas': {
        'Deltas_0_mean': 'mean',
        'Deltas_0_median': 'median',
        'Deltas_0_std': 'std'
    }
  })
  grouped1_df = filteredByPressType1.groupby(['SessionID', 'WindowNumber']).agg({
    'Deltas': {
        'Deltas_1_mean': 'mean',
        'Deltas_1_median': 'median',
        'Deltas_1_std': 'std'
    }
  })
  features = grouped_df.merge(grouped0_df, left_index=True, right_index=True).merge(grouped1_df, left_index=True, right_index=True)
  features.columns = features.columns.droplevel()
  features = features.reset_index()
  return features


def preProcessingKeyBoardTouchEvent(df):
  df = df[df.WindowNumber != -1]
  grouped_df = df.groupby(['SessionID', 'WindowNumber']).agg({
    'Contact_size': {
      'Contact_size_mean':'mean',
      'Contact_size_std': 'std'
    },
    'Pressure': {
        'Pressure_mean':'mean',
        'Pressure_std': 'std'
    },
})
  grouped_df.columns = grouped_df.columns.droplevel()
  grouped_df = grouped_df.reset_index()
  return grouped_df


def frameSession(accelerometer_df, gyroscope_df, magnetometer_df, keyPressEvent_df, keyBoardTouchEvent_df):
  # print('keyPressEvent_df\n', keyPressEvent_df.head())
  # print('accelerometer_df\n', accelerometer_df.head())
  # print('gyroscope_df\n', gyroscope_df.head())
  # print('magnetometer_df\n', magnetometer_df.head())
  # print('keyBoardTouchEvent_df\n', keyBoardTouchEvent_df.head())
  # import code; code.interact(local=dict(globals(), **locals()))
  printStartSeparator()
  printDfInfo(accelerometer_df, 'accelerometer')
  printDfInfo(gyroscope_df, 'gyroscope')
  printDfInfo(magnetometer_df, 'magnetometer')
  printDfInfo(keyPressEvent_df, 'keyPressEvent')
  printDfInfo(keyBoardTouchEvent_df, 'keyBoardTouchEvent')
  printEndSeparator()
  skeleton = createSkeleton(keyPressEvent_df)
  print(skeleton.head())

  accelerometer_df['SessionID'] = accelerometer_df.ActivityID
  gyroscope_df['SessionID'] = gyroscope_df.ActivityID
  magnetometer_df['SessionID'] = magnetometer_df.ActivityID
  keyPressEvent_df['SessionID'] = keyPressEvent_df.ActivityID
  keyBoardTouchEvent_df['SessionID'] = keyBoardTouchEvent_df.ActivityID

  accelerometer_df = windowDf(accelerometer_df,skeleton)
  gyroscope_df = windowDf(gyroscope_df,skeleton)
  magnetometer_df = windowDf(magnetometer_df,skeleton)
  keyPressEvent_df = windowDf(keyPressEvent_df,skeleton)
  keyBoardTouchEvent_df = windowDf(keyBoardTouchEvent_df,skeleton)

  accelerometer_df = preProcessingMotion(accelerometer_df)
  gyroscope_df = preProcessingMotion(gyroscope_df)
  magnetometer_df = preProcessingMotion(magnetometer_df)
  keyPressEvent_df = preProcessingKeyPressEvent(keyPressEvent_df)
  keyBoardTouchEvent_df = preProcessingKeyBoardTouchEvent(keyBoardTouchEvent_df)

  accelerometer_df = accelerometer_df.rename(columns = {
    'X_mean': 'Acc_X_mean',
    'X_std': 'Acc_X_std',
    'Y_mean': 'Acc_Y_mean',
    'Y_std': 'Acc_Y_std',
    'Z_mean': 'Acc_Z_mean',
    'Z_std': 'Acc_Z_std'
  })

  gyroscope_df = gyroscope_df.rename(columns = {
    'X_mean': 'Gyr_X_mean',
    'X_std': 'Gyr_X_std',
    'Y_mean': 'Gyr_Y_mean',
    'Y_std': 'Gyr_Y_std',
    'Z_mean': 'Gyr_Z_mean',
    'Z_std': 'Gyr_Z_std'
  })

  magnetometer_df = magnetometer_df.rename(columns = {
    'X_mean': 'Mag_X_mean',
    'X_std': 'Mag_X_std',
    'Y_mean': 'Mag_Y_mean',
    'Y_std': 'Mag_Y_std',
    'Z_mean': 'Mag_Z_mean',
    'Z_std': 'Mag_Z_std'
  })

  df_features = (keyPressEvent_df
  .merge(keyBoardTouchEvent_df, how='left', on=['SessionID', 'WindowNumber'])
  .merge(accelerometer_df, how='left', on=['SessionID', 'WindowNumber'])
  .merge(gyroscope_df, how='left', on=['SessionID', 'WindowNumber'])
  .merge(magnetometer_df, how='left', on=['SessionID', 'WindowNumber']))
  return df_features

def printStartSeparator():
  print("******************************************************\n\n\n\n\n\n\n")

def printEndSeparator():
  print("\n\n\n\n\n\n\n******************************************************")


def printDfInfo(df, variableName):
  print(variableName + ': ')
  print('Df size: ' + str(len(df)))
  print('Time interval: ' + str((df.Systime[len(df) - 1] - df.Systime[0])/1000) + 'segs')
