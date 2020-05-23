import requests
import io
from zipfile import ZipFile
import pandas as pd
import os
import numpy as np
import datetime as dt

DAILY_COVID_URL = 'http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip'

def daily_data(filename=None):
    '''
    Get the data from Health Department of the Mexico Federal Government
    '''
    print('Requesting data to datos abiertos Mexico')
    r = requests.get(DAILY_COVID_URL)
    #Check if the request went through :0
    assert r.ok
    #Convert it to a zip object
    zipdata = ZipFile(io.BytesIO((r.content)))
    data_name = zipdata.infolist()[0].filename
    print("Getting zip raw data into directory, will delete soon")
    zipdata.extractall()
    #Get the csv file and drop the one in the directory
    df = pd.read_csv(data_name, engine='python')
    print('Raw data deleted. If you specified filename, clean data will be saved in data directory')
    os.remove(data_name)
    
    #Clean data Part
    df.columns = map(str.lower, df.columns)
    df['pais_origen'] = np.where(df['pais_origen'] == '99', np.nan, df['pais_origen'])

    #Change date columns to date type
    df.fecha_def = np.where(df.fecha_def == '9999-99-99', np.nan, df.fecha_def)
    data_cols = ['fecha_actualizacion', 'fecha_ingreso', 'fecha_def', 'fecha_sintomas']
    for col in data_cols:
        df[col] = pd.to_datetime(df[col])

    #Modify dummies for health conditions variables
    binary_cols = ['intubado', 'neumonia','embarazo', 'habla_lengua_indig', 
                   'diabetes','epoc', 'asma', 'inmusupr', 'hipertension',
                   'otra_com', 'cardiovascular', 'obesidad', 'renal_cronica', 
                   'tabaquismo', 'otro_caso', 'uci']
    rep_pos = df[binary_cols].replace({2:0, 2.0:0, 99: np.nan, 97:0, 98:0})
    df.loc[:, binary_cols] = rep_pos

    #Create dummy death variable
    df['muertos'] = np.where(df['fecha_def'].isnull(), 0,1)

    #Create dummy for hospitalized patients
    df.loc[df['tipo_paciente'] == 1,'tipo_paciente'] = 0
    df.loc[df['tipo_paciente'] == 2,'tipo_paciente'] = 1
    df.rename(columns = {'tipo_paciente':'hospitalizado'},
                          inplace=True)

    #Create estimated recovery dummy and recovery date
    df['recovered'] = np.where((df.fecha_ingreso + pd.DateOffset(days=30) < str(dt.date.today())) & \
                               (df.muertos == 0),\
          1,0)
    df['fecha_rec'] = df.fecha_ingreso + pd.DateOffset(30)
    df.loc[df.recovered == 0, 'fecha_rec'] = np.nan

    #Save csv in directory if requested
    if filename:
         if os.path.exists(filename):
             os.remove(filename)
         df.to_csv(filename)
    return df

if __name__ == "__main__":
    daily_data('daily_covid.csv')
