import requests
import io
from zipfile import ZipFile
import pandas as pd
import os
import numpy as np

DAILY_COVID_URL = 'http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip'

def daily_data(filename=None):
    '''
    Get the data from Health Department of Mexico Federal Government
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
    #Clean data
    df.columns = map(str.lower, df.columns)
    df.fecha_def = np.where(df.fecha_def == '9999-99-99', np.nan, df.fecha_def)
    for col in ['fecha_ingreso', 'fecha_actualizacion', 'fecha_def', 'fecha_sintomas']:
        df[col] = pd.to_datetime(df[col])
    cols_99 = ['intubado', 'neumonia', 'epoc', 'asma', 'inmusupr','hipertension', 'otra_com',\
         'cardiovascular', 'obesidad', 'renal_cronica', 'tabaquismo', 'otro_caso', 'migrante', \
             'pais_origen', 'uci']
    for col in cols_99:
        if col == 'pais_origen':
            df[col] = np.where(df[col] == '99', np.nan, df[col])
        else:
            df[col] = np.where(((df[col] == 99) | (df[col] == 98) | \
            (df[col] == 97)), np.nan, df[col])
    #Save csv in directory if requested
    if filename:
        if os.path.exists(filename):
            os.remove(filename)
        df.to_csv(filename)
    return df


if __name__ == "__main__":
    daily_data('daily_covid.csv')


