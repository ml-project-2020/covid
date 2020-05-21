#Module to pre process individual level data into state level data
import pandas as pd
import get_data
import numpy as np

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
        covid_df = get_data.daily_data()    
        xls = '../data/description_catalogue_covid_mx.xlsx'
        state_codes = pd.read_excel(xls, sheet_name='Catálogo de ENTIDADES')
    state_codes = dict(zip(state_codes.CLAVE_ENTIDAD , 
                       list(zip(state_codes.ENTIDAD_FEDERATIVA, 
                       state_codes.ABREVIATURA))))

    binary_cols = ['intubado', 'neumonia','embarazo', 'habla_lengua_indig', 
                   'diabetes','epoc', 'asma', 'inmusupr', 'hipertension',
                   'otra_com', 'cardiovascular', 'obesidad', 'renal_cronica', 
                   'tabaquismo', 'otro_caso', 'uci']
    positive_cases = covid_df.loc[covid_df['resultado']==1, :]
    rep_pos = positive_cases[binary_cols].replace({2:0, 2.0:0, 99: np.nan})
    positive_cases.loc[:, binary_cols] = rep_pos
    positive_cases.rename(columns = {'resultado':'casos_positivos'}, 
                          inplace=True)

    #Add death dummy if patient dies 1 == death
    positive_cases.loc[:,'muertos']=np.where(positive_cases['fecha_def'].isnull()
                                            ,0,1)

    #Change hospitalized, 1 if hospitalized 0 if sent home
    positive_cases.loc[positive_cases['tipo_paciente'] == 1,'tipo_paciente'] = 0
    positive_cases.loc[positive_cases['tipo_paciente'] == 2,'tipo_paciente'] = 1
    positive_cases.rename(columns = {'tipo_paciente':'hospitalizado'},
                          inplace=True)
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
               'muerte', 'intubado','neumonia', 'edad',
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

