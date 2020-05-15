import requests
import io
from zipfile import ZipFile
import pandas as pd
import os
import numpy as np

DAYLY_COVID_URL = 'http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip'

def daily_data(filename):
    '''
    Get the data from Health Department of Mexico Federal Government
    '''
    r = requests.get(DAYLY_COVID_URL)
    #Check if the request went through :0
    assert r.ok
    #Convert it to a zip object
    zipdata = ZipFile(io.BytesIO((r.content)))
    data_name = zipdata.infolist()[0].filename
    zipdata.extractall()
    #Get the csv file and drop the one in the directory
    df = pd.read_csv(data_name, engine='python')
    os.remove(data_name)
    #Clean data
    df.columns = map(str.lower, df.columns)
    df.fecha_def = np.where(df.fecha_def == '9999-99-99', np.nan, df.fecha_def)
    for col in ['fecha_ingreso', 'fecha_actualizacion', 'fecha_def', 'fecha_sintomas']:
        df[col] = pd.to_datetime(df[col])
    df.intubado = np.where(((df.intubado == 99) | (df.intubado == 98) | \
        (df.intubado == 97)), np.nan, df.intubado) 
    
    df.to_csv(filename)
    return


if __name__ == "__main__":
    daily_data('daily_covid.csv')

    
    np.where(((df.intubado == 99) | (df.intubado == 98) | (df.intubado == 97)), np.nan, df.intubado)




