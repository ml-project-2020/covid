import requests
import io
from zipfile import ZipFile
import pandas as pd
import os
import numpy as np
import datetime as dt

DAILY_COVID_URL = 'http://187.191.75.115/gobmx/salud/datos_abiertos/datos_abiertos_covid19.zip'

def daily_covid(filename=None):
    '''
    Get the daily covid cases from Health Department of the Mexico Federal Government
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

def convert_to_state_date(frames=False, covid_df=None, state_codes=None):
    '''
    Function to convert covid individual level data
    to counts by state and date. Counts include number of new cases
    each day by state, number of positive cases that had pre existing conditions
    such as diabetes, asma, cardiovscular disease, etc.
    Inputs:
    - frames: boolean set to True if both covid_df and state_codes are provided
              as inputs else leave as default (False)
    - covid_df (optional) pandas dataframe
                if data has already been loaded do not re load.
    - state_codes: (optional) pandas data frame.
    In jupyter notebook 'Descriptive Visualizations' both dataframes are loaded
    and should be given as inputs. 
    Returns:
    - final_df : pandas dataframe with count columns. 
      See print statement for all columns included.
    '''
    #Get state codes from description catalogue
    if not frames:
        covid_df = daily_covid()    
        xls = '../data/description_catalogue_covid_mx.xlsx'
        state_codes = pd.read_excel(xls, sheet_name='Catálogo de ENTIDADES')
    state_codes = dict(zip(state_codes.CLAVE_ENTIDAD , 
                       list(zip(state_codes.ENTIDAD_FEDERATIVA, 
                       state_codes.ABREVIATURA))))

    #Subset positive cases
    num_tests = covid_df.groupby(['entidad_um']).count().reset_index()\
                [['entidad_um','id_registro']]
    num_tests.columns = ['entidad_um', 'num_tests']

    positive_cases = covid_df.loc[covid_df['resultado']==1, :]
    positive_cases.rename(columns = {'resultado':'casos_positivos'}, 
                          inplace=True)
    positive_cases = positive_cases.merge(num_tests, right_on='entidad_um',
                                          left_on='entidad_um')

    #Bins age column
    binss = [i for i in range(0, 121, 10)]
    positive_cases.loc[:, 'edad'] = pd.cut(positive_cases.edad, binss)
    by_age = positive_cases.groupby(['entidad_um', 'fecha_ingreso', 'edad'])\
             ['casos_positivos'].sum().reset_index()
    by_age.loc[:,'casos_positivos'] = by_age['casos_positivos'].fillna(0)
    by_age = pd.pivot_table(by_age, values='casos_positivos',
                            index=['entidad_um','fecha_ingreso'],
                            columns='edad')
    by_age.columns = ['Edad: ' + str(col) for col in by_age.columns]
    by_age.reset_index(inplace=True)

    to_keep = ['fecha_ingreso','entidad_um', 'casos_positivos','hospitalizado', 
               'muertos', 'intubado','neumonia', 'edad', 'num_tests',
               'habla_lengua_indig', 'diabetes', 'epoc', 'asma', 'inmusupr', 
               'hipertension', 'otra_com','cardiovascular', 'obesidad', 
               'renal_cronica', 'tabaquismo','otro_caso', 'uci']

    positive_cases = positive_cases.loc[:, to_keep]

    by_state_date = positive_cases.groupby(['entidad_um', 'fecha_ingreso'])\
    [to_keep[2:]].sum().reset_index()

    final_df = by_state_date.merge(by_age, right_on=['entidad_um',
                                   'fecha_ingreso'], left_on=['entidad_um',
                                   'fecha_ingreso'])
    final_df.loc[:, 'entidad'] = final_df['entidad_um'].apply(lambda row:
                                                       state_codes[row][0])
    print('Finished cleaning, wrangling and grouping count columns are:', 
          list(final_df.columns[2:]))
    return final_df

if __name__ == "__main__":
    daily_covid('../data/daily_covid.csv')
