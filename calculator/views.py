from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
import os
import json
import time
from tensorflow import keras
import numpy as np
import pandas as pd

model=keras.models.load_model('./assets/keras_model')

def manual_data(request):
    try:
        params=json.loads(request.body.decode())
        #create list of temperature
        temperature=np.arange(params['temp_min'],params['temp_max']+0.0001,params['step']).tolist()
        #create dataframe
        data=pd.DataFrame(temperature,columns=['Temperature (°C)'])
        data=data.assign(**{'Type':params['type'],'Size (nm)':params['size'],'Concentration (%)':params['concentration']})
        #Organize datafarme to much keras model inputs
        data=data.reindex(columns=['Type','Size (nm)','Concentration (%)','Temperature (°C)'])
        model_output = model.predict(data).tolist()
        viscosity=[]
        for d in model_output:
            viscosity.append(d[0])
        data['Type']=data['Type'].replace([0,1,2,3,4],['Al2O3','CeO2','CuO','Fe','Ag'])
        data.insert(4,'Viscosity (mPa.s)',viscosity)
        file_path='./static/xlsx/file-'+str(round(time.time()*100))+'.xlsx'
        data.to_excel(file_path,index=False)
        return JsonResponse({"temperature":temperature,"viscosity":viscosity,"file_path":file_path})
    except Exception as e:
        res=JsonResponse({"message":"Unknown error !","error":e.args})
        res.status_code=400
        return res


def excel_data(request):
    try:
        file=request.FILES['file']
        data=pd.read_excel(file)
        #Organize datafarme to much keras model inputs In case user didn't prepare them correctly and dropping any additional column
        data=data.reindex(columns=['Type','Size (nm)','Concentration (%)','Temperature (°C)'])
        data=data.loc[:,:'Temperature (°C)']
        #Remove any rows with missing values from the DataFrame
        data.dropna(inplace=True)
        data['Type']=data['Type'].apply(str.lower)
        data['Type']=data['Type'].replace(['al2o3','ceo2','cuo','fe','ag'],[0,1,2,3,4])
        model_output = model.predict(data).tolist()
        viscosity=[]
        for d in model_output:
            viscosity.append(d[0])
        data['Type']=data['Type'].replace([0,1,2,3,4],['Al2O3','CeO2','CuO','Fe','Ag'])
        data.insert(4,'Viscosity (mPa.s)',viscosity)
        file_path='./static/xlsx/file-'+str(round(time.time()*100))+'.xlsx'
        data.to_excel(file_path,index=False)
        return JsonResponse({"file_path":file_path})
    except Exception as e:
        res=JsonResponse({"message":"Make sure that the Excel file follows the required format !","error":e.args})
        res.status_code=400
        return res