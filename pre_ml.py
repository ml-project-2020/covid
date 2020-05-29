'''
Final Pre-process data before applying an ML Model
'''
from covid_data import daily_covid, convert_to_state_date
import health_data
import mlpipeline as pipeline
import pandas as pd

def data(rar=True):
    '''
    Returns the final data to use in ML phase

    Input:
    - rar: boolean (set to false to avoid using rarefile)
    '''
    covid = daily_covid()
    covid_positive = covid[covid.resultado==1]

    # Separate features to use in the model
    features_covid = ['entidad_res', 'municipio_res', 'embarazo', 'edad', 'diabetes', 'epoc', 
                  'asma', 'inmusupr', 'hipertension', 'cardiovascular', 'obesidad', 'tabaquismo', 'hospitalizado','muertos']

    data_model = covid_positive.loc[:, features_covid]

    #Generate municipality id
    data_model['CVE_MUN'] = data_model['municipio_res'] + data_model['entidad_res'] * 1000
    mun = data_model.pop('CVE_MUN')
    data_model.insert(2, 'CVE_MUN', mun)

    #Merge with poverty data
    poverty_data = health_data.get_poverty_data()
    data_model = pd.merge(data_model, poverty_data[['CVE_MUN', 'pobreza']], on='CVE_MUN', how='left')

    #Add population density 
    mun_territory = health_data.get_mun_territory()
    conapo_mun = health_data.get_conapo_mun(rar) 
    pop_den = pd.merge(mun_territory, conapo_mun, on='CVE_MUN', how='left')
    pop_den['Densidad_pob'] = pop_den['POB'] / pop_den['superficie']
    data_model = pd.merge(data_model, pop_den[['CVE_MUN', 'POB', 'Densidad_pob']], 
                      on='CVE_MUN', how='left')

    #Add hospital data
    hospitals = health_data.get_hospital_data()
    hospitals['num_medicos'] = (hospitals['Número de Médicos Generales'] +
                           hospitals['Número deMédicos Neumólogos'] + 
                           hospitals['Número de Médicos Infectólogos'] +
                           hospitals['Número de Médicos Urgenciólogos']+
                           hospitals['Número de Médicos Epidemiólogos'])
    hospitals['CVE_MUN'] = hospitals['Clave Municipio'] + hospitals['Clave Estado']*1000
    hosp_cols = ['TOTAL CAMAS AREA HOSPITALIZACIÓN', 'num_medicos', 
             'Total enfermeras en contacto con el paciente']
    hospitals = hospitals.groupby('CVE_MUN').sum()
    
    data_model = pd.merge(data_model, hospitals[hosp_cols], 
                      on='CVE_MUN', how='left')
    data_model['medicos'] = data_model['num_medicos'] /  data_model['POB'] * 10000
    data_model['camas_hosp'] = data_model['TOTAL CAMAS AREA HOSPITALIZACIÓN'] /  data_model['POB'] * 10000
    data_model['enfermeras'] = data_model['Total enfermeras en contacto con el paciente'] /  data_model['POB'] * 10000

    #Drop cols that we don't need
    data_model.drop(['POB', 'TOTAL CAMAS AREA HOSPITALIZACIÓN', 
                 'num_medicos', 'Total enfermeras en contacto con el paciente'], axis=1, inplace=True)

    #Impute missing values
    data_model['pobreza'] = data_model.groupby('entidad_res')['pobreza'].apply(lambda x:x.fillna(x.mean()))
    data_model['Densidad_pob'] = data_model.groupby('entidad_res')['Densidad_pob'].apply(lambda x:x.fillna(x.mean()))
    data_model['camas_hosp'] = data_model.groupby('entidad_res')['camas_hosp'].apply(lambda x:x.fillna(x.mean()))
    data_model['medicos'] = data_model.groupby('entidad_res')['medicos'].apply(lambda x:x.fillna(x.mean()))
    data_model['enfermeras'] = data_model.groupby('entidad_res')['enfermeras'].apply(lambda x:x.fillna(x.mean()))

    return data_model