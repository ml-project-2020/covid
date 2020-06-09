# ML course Project
# COVID-19 in Mexico: Identifying health and socioeconomic variables for COVID-19 death and hospitalization prediction

Team Members:  
* Roberto Barroso-Luque (barrosoluquer)  
* Luz Stephanie Ramos Gomez (stephanieramos)  
* Oscar Enrique Noriega Villarreal (onoriega)  
* Jesica Maria Ramirez Toscano (jramireztoscano)  

## Table of contents
* [Motivation and Brief Summary](#motivation-and-brief-summary)
* [Setup](#setup)
* [Data Collection and Processing](#data-collection-and-processing)
* [Notebooks Structure](#notebooks-structure)
* [Final Report and Results](#final-report-and-results)


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
All the data used in this project is stored in the **data** folder.
To get daily updated data, we wrote:  
* **covid_data.py**  
This module serves to download the most recent COVID-19 data from Mexico. The data is wrangled, cleaned, and transformed into a usable data frame. It also provides a function to aggregating all information to state level.  
   * ```daily_covid()``` returns a pandas dataframe in which each row represents an individual tested for COVID-19
   * ```convert_to_state_date()```converts COVID individual level data to counts by state and date  
If you run the following, a csv file with daily COVID-19 individual cases will be downloaded to the data folder.
```
$ python3 covid_data.py
```
* **health_data.py**  
This module obtains data from ENSANUT, CONAPO, CONEVAL, and the Health Ministry at municipality and state levels.
Particularly, with the mentioned data sources, we obtain: 
   * The number of hospital beds, doctors, and nurses from the Health Resources Data provided by the Secretary of Health.
   * Percentage of people living in poverty from CONEVAL
   * Demographic data (population density) from CONAPO

Calling the ```merge_data_mun()`` function returns a merged data frame in which each row represents a municipality.

* **pre_ml.py**  
This model merges individual COVID-19 data with health municipality level data. 
It is the final processing of data before applying several techniques of sampling and machine learning models.


## Notebooks Structure
To predict death and hospitalizations, we used several ML classifications models. Particularly, we applied: logistic regression, naive Bayes, linear support vector machines, decision trees, and random forest models. 
For each model, we provide a notebook that includes the cross-validation approach we used (with imbalanced sample techniques), testing results of the model, and feature importance visualizations.  
* **Logistic Regression.ipynb**
* **Naive_Bayes.ipynb**
* **SVM DecisionTrees.ipynb**
* **Random Forest Model.ipynb**  
   *Includes additional visualizations about the model's performance in each state of Mexico*

Finally, to assess the relative risk of each state, we used the predicted values of the *Balanced Random Forest* and *Linear Support Vector Machines* models to construct a simple risk index on COVID death and hospitalizations to compare the risk between states.  
* See **Relative Risk.ipynb**

## Final Report and Results
The overall analysis of this project is documented in *Final_report.pdf*.
