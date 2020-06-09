# ML course Project
# COVID-19 in Mexico: Identifying health and socioeconomic variables for covid-19 death and hospitalization prediction

Team Members:  
-Roberto Barroso-Luque (barrosoluquer)  
-Luz Stephanie Ramos Gomez (stephanieramos)  
-Oscar Enrique Noriega Villarreal (onoriega)  
-Jesica Maria Ramirez Toscano (jramireztoscano)  

## Table of contents
* [Motivation and Brief Summary](#general-info)
* [Setup](#setup)
* [Data Collection and Processing](#data-collection)
* [Notebooks Structure](#notebooks-structure)
* [Final Report and Results](#results)


## Motivation and Brief Summary
The current pandemic caused by the SARS-CoV-2 virus represents an unprecedented challenge to the global economy. As of June 2020, about 7 million people have tested positive and more than 400,000 have died as a result of the virus.  In order to provide data-driven policy advice to individual countries analysis and modeling should be done on national-level data.  With under-funded healthcare systems, institutional-weakness, and large informal economic sectors, Mexico faces a gigantic challenge to contain the virus. We developed classification algorithms to predict death and hospitalization among individuals who tested positive for the virus in Mexican soil using a mix of health and socioeconomic variables at the individual and municipality levels. Using ten-fold cross-validation and synthetic minority over-sampling linear support vectors, logistic regression, decision trees, and random forest models were trained to predict patient outcomes (survival vs death and hospitalization vs home recovery).

## Setup
If you want to replicate the presented analysis, some modules must be installed. Particularly, the following:
```
pandas
geopandas
numpy
matplotlib
seaborn
mpl_toolkits
requests
zipfile
rarfile
imblearn
sklearn
```

## Data Collection and Processing
To get daily updated data, we wroted: covid_data.py
If you run the following, a csv file with daily COVID-19 individual cases will be downloaded in the data folder.


## Notebooks Structure

## Final Report and Results