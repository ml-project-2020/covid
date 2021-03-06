# ML course Project
# COVID-19 in Mexico: Predicting severe disease outcomes using health and socioeconomic variables.

*"AI applications present opportunities for the future of healthcare and can be harnessed at this time, as clinicians take on the complexities of responding to COVID-19" Xiangao Jiang et al(2020)*

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
* [Final Report and Acknowledgements](#final-report-and-acknowledgements)


## Motivation and Brief Summary
The current pandemic caused by the SARS-CoV-2 virus represents an unprecedented challenge to the global economy. As of June 2020, about 7 million people have tested positive and more than 400,000 have died as a result of the virus. To provide data-driven policy advice to individual countries analysis and modeling should be done on national-level data.  With under-funded healthcare systems, institutional-weakness, and large informal economic sectors, Mexico faces a gigantic challenge to contain the virus. We developed classification algorithms to predict death and hospitalization among individuals who tested positive for the virus in Mexican soil using a mix of health and socioeconomic variables at the individual and municipality levels. Using ten-fold cross-validation and synthetic minority over-sampling support vector machine, logistic regression, complement naive Bayes, decision trees, and random forest models were trained to predict patient outcomes (survival vs death and hospitalization vs home recovery).

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
All the data used in this project is stored in the [**data**](data) folder.
To get daily updated data, we wrote:  
* [**covid_data.py**](covid_data.py)  
This module serves to download the most recent COVID-19 data from Mexico. The data is wrangled, cleaned, and transformed into a usable data frame. It also provides a function to aggregating all information to state level.  
   * ```daily_covid()``` returns a pandas dataframe in which each row represents an individual tested for COVID-19
   * ```convert_to_state_date()```converts COVID individual level data to counts by state and date
  
If you run the following, a csv file with daily COVID-19 individual cases will be downloaded to the data folder.
```
$ python3 covid_data.py
```
* [**health_data.py**](health_data.py)  
This module obtains data from ENSANUT, CONAPO, CONEVAL, and the Health Ministry at municipality and state levels.
Particularly, with the mentioned data sources, we obtain: 
   * The number of hospital beds, doctors, and nurses from the Health Resources Data provided by the Secretary of Health.
   * Percentage of people living in poverty from CONEVAL
   * Demographic data (population density) from CONAPO

Calling the ```merge_data_mun()``` function returns a merged data frame in which each row represents a municipality.

* [**pre_ml.py**](pre_ml.py)  
This model merges individual COVID-19 data with health municipality level data. 
It is the final processing of data before applying several techniques of sampling and machine learning models.


## Notebooks Structure
To predict death and hospitalizations, we used several ML classifications models. Particularly, we applied: logistic regression, naive Bayes, support vector machine, decision trees, and random forest models. In these notebooks, we also used a custom module [**mlpipeline.py**](mlpipeline.py) to split, normalize, impute values of the data, apply SMOTE in the learning process, and get the metrics of predicted values. For each model, we provide a notebook that includes the cross-validation approach we used (with imbalanced sample techniques), testing results of the model, and feature importance visualizations:  
* [**Logistic Regression.ipynb**](Logistic%20Regression.ipynb)
* [**Naive_Bayes.ipynb**](Naive_bayes.ipynb)
* [**SVM DecisionTrees.ipynb**](SVM%20DecisionTrees.ipynb)
* [**Random Forest Model.ipynb**](Random%20Forest%20Model.ipynb)  
   *Includes additional visualizations about the model's performance in each state of Mexico*

Finally, to assess the relative risk of each state, we used the predicted values of the *Balanced Random Forest* and *Support Vector Machine* models to construct a simple risk index on COVID death and hospitalizations to compare the risk between states.  
* See [**Relative Risk.ipynb**](Relative%20Risk.ipynb)

## Final Report and Acknowledgements
The overall analysis and results of this project are documented in [**ML_paper.pdf**](ML_paper.pdf).

The CAPP 30254 - Spring 2020 Machine Learning for Public Policy Course motivated this project.
We want to thank professor **Nick Feamster** and the Teaching Assistants: Felipe Alamos, Erika Tyagi, Jonathan Tan, Tammy Glazer, and Alec Macmillen for their great support and comments.  :blush:

**All errors are ours.**
