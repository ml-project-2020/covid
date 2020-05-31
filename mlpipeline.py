import pandas as pd
import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, f1_score
import datetime


def count_nan(data_frame):
    '''
    returns series with number of missing values per column
    '''

    rv = data_frame.isnull().sum()

    return rv


def split_data(data_frame, test_size, seed=1):
    '''
    splits data into trainning set and testing set.
    '''
    train, test = train_test_split(data_frame, test_size=test_size, random_state=seed)

    return (train, test)


def normalize(train_data, test_data, features):
    '''
    takes 2 datasets (testing data and trainning data) and a list of features to normalize and adds 
    normalized new columns.
    '''
    
    scaler = StandardScaler()
    train = train_data.copy()
    test = test_data.copy()
    
    normal_train = scaler.fit_transform(train[features])
    normal_test = scaler.transform(test[features])
    
    for i, col in enumerate(features):
        train.loc[:, col] = normal_train[:, i]
        test.loc[:, col] = normal_test[:, i]

    return train, test

def label_encode(data_frame, cat_var):
    '''
    converts label into a numerical feture
    '''

    df = data_frame.copy()
    df.loc[:, cat_var] = df[cat_var].astype('category')
    df.loc[:, cat_var] = df[cat_var].cat.codes

    return df


def encode_cat(data_frame, vars, prefixes):
    '''
    Performs one hot encoding on categorical variables, leaves last column at the end
    '''

    y = data_frame.columns[-1]
    col = data_frame.pop(y)
    dum_df = pd.get_dummies(data_frame, columns=vars, prefix=prefixes)
    dum_df[y] = col

    return dum_df


def add_drop_cols(train, test):
    '''
     If a column appears in the training set but not in the testing set, creates 
     a column with all 0's in the testing set. If a column appears in the testing set 
     but not in the training set, drops it from  testing data.
    '''

    cols_add = list(set(train.columns) - set(test.columns))
    cols_drop = list(set(test.columns) - set(train.columns))

    if not cols_drop:
        print('No columns to remove from training set')
    
    if not cols_add:
        print('No columns to add to testing set')

    for col in cols_drop:
        print("Removing additional feature {} from testing set".format(col))
        test.drop(col, axis=1, inplace=True)
    
    for col in cols_add:
        print("Adding missing feature {} to training set".format(col))
        train[col] = 0

    return (train, test)