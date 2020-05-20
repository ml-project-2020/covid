import requests
import io
from zipfile import ZipFile
import pandas as pd
import numpy as np
import get_data
import os

def  state_features():
    '''
    Gathers and aggregates data on health infrastructure, demographics,
    and population risk conditions on state-level.
    '''
    #FEDERAL HEALTH RESOURCES FROM HEALTH MINISTRY
    # #***Part of get_data code***
    url = 'http://www.dgis.salud.gob.mx/descargas/datosabiertos/recursosSalud/Recursos_Salud_2018.zip'
    r = requests.get(url)
    zipdata = ZipFile(io.BytesIO((r.content)))
    data_name = zipdata.infolist()[0].filename
    print("Getting zip raw data into directory, will delete soon")
    zipdata.extractall()
    #Get the csv file and drop the one in the directory
    df = pd.read_csv(data_name, engine='python')
    print('Raw data deleted. If you specified filename, clean data will be saved in data directory')
    os.remove(data_name)
    #******
    
    #Filter only facilities with Hospitalization features
    df=df[df['Tipo de Establecimiento'] == 'HOSPITALIZACI�N']
    #Keep relevant columns
    relevant_cols = ['Clave Estado', 'N�mero de Consultorios de Epidemiolog�a', \
        'N�mero de Consultorios de Infectolog�a', 'N�mero de Consultorios de Neumolog�a', \
        'N�mero de consultorios en �rea de urgencias', 'TOTAL CAMAS AREA HOSPITALIZACI�N', \
        'N�mero de M�dicos Generales', 'N�mero deM�dicos Neum�logos','N�mero de M�dicos Infect�logos', \
        'N�mero de M�dicos Urgenci�logos','N�mero de M�dicos Epidemi�logos', \
        'Total enfermeras en contacto con el paciente']
    df=df.loc[:, relevant_cols]
        #Generate series for total Hospitalization facilities per state
    total_hosp_units = pd.DataFrame(df['Clave Estado'].value_counts())
        #Generate series for total consulting rooms, hospital beds and relevant medical personnel per state
    agg_data_hs = df.groupby('Clave Estado').sum()
    agg_data_hs.columns = ['Numero de Consultorios de Epidemiologia', \
            'Numero de Consultorios de Infectologia', 'Numero de Consultorios de Neumologia', \
            'Numero de consultorios en area de urgencias', 'TOTAL CAMAS AREA HOSPITALIZACION', \
            'Numero de Medicos Generales', 'Numero de Medicos Neumologos','Numero de Medicos Infectologos', \
            'Numero de Medicos Urgenciologos','Numero de Medicos Epidemiologos', \
            'Total enfermeras en contacto con el paciente']
    agg_data_hs['Total de unidades de Hospitalizacion'] = total_hosp_units
    agg_data_hs=agg_data_hs.reset_index()
    agg_data_hs=agg_data_hs.rename(columns = {'Clave Estado': 'CVE_GEO'})
    
    #DEMOGRAPHIC DATA FROM CONAPO
    url = 'http://www.conapo.gob.mx/work/models/CONAPO/Datos_Abiertos/Proyecciones2018/ind_dem_proyecciones.csv'
    r = requests.get(url).content
    conapo = pd.read_csv(io.StringIO(r.decode('latin-1')))
    #Keep only population projections for 2020
    conapo = conapo[conapo['AÑO'] == 2020]
    #Keep only population columns
    conapo = conapo[['CVE_GEO','EDAD_MED']+ [col for col in conapo if col.startswith('POB')]]
    #Drop the national level data
    conapo = conapo[conapo['CVE_GEO']!=0]

    #DATA ON STATE TERRITORY
    territory = pd.read_csv('../data/state_territory.csv')
    territory = territory[['Clave', 'Km2']]
    territory = territory.rename(columns = {'Clave': 'CVE_GEO'})

    #HEALTH DATA
    ensanut = pd.read_csv('CS_ADULTOS.csv.csv.zip', compression='zip')
    #Keep relevant columns
    relevant_cols = ['ENT', 'P3_1', 'P4_1', 'P5_1', 'P5_2_1', 'P5_2_2', \
        'P5_2_3', 'P13_2', 'F_20MAS']
    ensanut= ensanut[relevant_cols]

    #Change encoding for survey answers
    for c in ['P4_1', 'P5_1', 'P5_2_1', 'P5_2_2', 'P5_2_3']:
        ensanut[c] = ensanut[c].map({1: 1, 2: 0})
    ensanut['P3_1'] = ensanut['P3_1'].map({1: 1, 2: 1, 3:0})
    ensanut['P13_2'] = ensanut['P13_2'].map({1: 1, 2: 1, 3:0, 8: np.nan})
    ensanut.dropna()
    ensanut.loc[(ensanut['P5_1'] == 1) | (ensanut['P5_2_1'] == 1)| (ensanut['P5_2_2'] == 1) | \
                (ensanut['P5_2_3'] == 1), 'Cardiovascular'] = 1  
    ensanut.loc[(ensanut['P5_1'] == 0) | (ensanut['P5_2_1'] == 0)| (ensanut['P5_2_2'] == 0) | \
                (ensanut['P5_2_3'] == 0), 'Cardiovascular'] = 0
    ensanut = ensanut.drop(['P5_1', 'P5_2_1', 'P5_2_2', 'P5_2_3'], axis=1)
    ensanut.columns = ['CVE_GEO', 'Diabetes', 'Hipertension', 'Tabaquismo', 'POB_20_MAS_2018', 'Cardiovascular']
    for c in ['Diabetes', 'Hipertension', 'Tabaquismo', 'Cardiovascular']:
        ensanut[c] = ensanut[c] * ensanut['POB_20_MAS_2018']
    ensanut = ensanut.groupby('CVE_GEO').sum()
    ensanut.reset_index()
    for c in ['Diabetes', 'Hipertension', 'Tabaquismo', 'Cardiovascular']:
        ensanut['Porcentaje_'+c]=ensanut[c]/ensanut['POB_20_MAS_2018']


    #Join data

    df=pd.merge( conapo, territory, on='CVE_GEO')
    df['Densidad_pob'] = df['POB_MIT_AÑO']/ df['Km2']
    df=pd.merge( df,agg_data_hs, on='CVE_GEO')
    df=pd.merge( df,ensanut, on='CVE_GEO')

    return df

