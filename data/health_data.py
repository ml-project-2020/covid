import requests
import io
from zipfile import ZipFile
import pandas as pd
import numpy as np
import os

def get_ensanut():
    '''
    Obtain health data
    '''

    ensanut = pd.read_csv('data/CS_ADULTOS.csv.csv.zip', compression='zip')
    relevant_cols = ['ENT', 'P3_1', 'P4_1', 'P5_1', 'P5_2_1', 'P5_2_2', \
                    'P5_2_3', 'P13_2', 'F_20MAS']
    ensanut= ensanut[relevant_cols]

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

    return ensanut


def get_hospital_data():
    '''
    Obtain federal health resources from  health ministry by h
    '''

    hospitals = pd.read_csv('data/Recursos_Salud_2018.csv', encoding='latin1')
    hospitals=hospitals[hospitals['Tipo de Establecimiento'] == 'HOSPITALIZACIÓN']

    relevant_cols = ['Clave Estado', 'Nombre Estado', 'Clave Municipio', 'Nombre Municipio', 'Número de Consultorios de Epidemiología', \
            'Número de Consultorios de Infectología', 'Número de Consultorios de Neumología', \
            'Número de consultorios en área de urgencias', 'TOTAL CAMAS AREA HOSPITALIZACIÓN', \
            'Número de Médicos Generales', 'Número deMédicos Neumólogos','Número de Médicos Infectólogos', \
            'Número de Médicos Urgenciólogos','Número de Médicos Epidemiólogos', \
            'Total enfermeras en contacto con el paciente']
    hospitals=hospitals[relevant_cols]
    
    return hospitals


def get_conapo():
    '''
    Demographic data from conapo
    '''

    url = 'http://www.conapo.gob.mx/work/models/CONAPO/Datos_Abiertos/Proyecciones2018/ind_dem_proyecciones.csv'
    r = requests.get(url).content
    conapo = pd.read_csv(io.StringIO(r.decode('latin-1')))
    
    #Keep only population projections for 2020
    conapo = conapo[conapo['AÑO'] == 2020]
    
    #Keep only population columns
    conapo = conapo[['CVE_GEO','EDAD_MED']+ [col for col in conapo if col.startswith('POB')]]

    #Drop the national level data
    conapo = conapo[conapo['CVE_GEO']!=0]

    return conapo


def get_territory():
    '''
    Data on state territory
    '''

    territory = pd.read_csv('data/state_territory.csv')
    territory = territory[['Clave', 'Km2']]
    territory = territory.rename(columns = {'Clave': 'CVE_GEO'})

    return territory


def merge_data():
    '''
    Merge all health and territory data
    '''

    ensanut = get_ensanut()
    hospitals = get_hospital_data()
    conapo = get_conapo()
    territory = get_territory()

    # group hospital data by state
    hospitals = hospitals[hospitals.columns.difference(['Nombre Estado', 'Clave Municipio', 'Nombre Municipio'])]
    total_hosp_units = pd.DataFrame(hospitals['Clave Estado'].value_counts())
    agg_data_hs = hospitals.groupby('Clave Estado').sum()
    agg_data_hs['Total de unidades de Hospitalizacion'] = total_hosp_units
    agg_data_hs=agg_data_hs.reset_index()
    agg_data_hs=agg_data_hs.rename(columns = {'Clave Estado': 'CVE_GEO'})

    # merge
    data_all = pd.merge(conapo, territory, on='CVE_GEO')
    data_all['Densidad_pob'] = data_all['POB_MIT_AÑO']/ data_all['Km2']
    data_all = pd.merge(data_all , agg_data_hs, on='CVE_GEO')
    data_all = pd.merge(data_all, ensanut, on='CVE_GEO')
    
    return data_all





