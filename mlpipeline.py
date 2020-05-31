import pandas as pd
import numpy as np
import seaborn as sns 
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.naive_bayes import GaussianNB
from imblearn.over_sampling import SMOTE
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score


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
    takes 2 datasets (testing data and trainning data) and a list of features to normalize 
    and changes columns to normalized new columns.
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


def upsampling(train, features, target, model, params):
    '''
    Performs a manual manual upsampling within folds.
    Inputs:
        train: training dataframe
        test: testing dataframe
        model: model
        params: dictionary specifying the parameters for each model
    Output:
        Returns model object and avg scores.
    '''

    cv = KFold(n_splits=10, random_state=0, shuffle=True)
    smoter = SMOTE(random_state=42)
    X = train[features]
    y = train[target]
    precision = []
    recall = []
    accuracy = []

    for train_fold_index, val_fold_index in cv.split(X, y):
        # Get the training data
        X_train_fold, y_train_fold = X.iloc[train_fold_index], y.iloc[train_fold_index]
        # Get the validation data
        X_val_fold, y_val_fold = X.iloc[val_fold_index], y.iloc[val_fold_index]
        # Upsample only the data in the training section
        X_train_fold_upsample, y_train_fold_upsample = smoter.fit_resample(X_train_fold,
                                                                           y_train_fold)
        # Fit the model on the upsampled training data
        model_obj = model 
        model_obj.set_params(**params)
        model_obj.fit(X_train_fold_upsample.values, y_train_fold_upsample.values.ravel())
        # Score the model on the (non-upsampled) validation data
        pred = model_obj.predict(X_val_fold)
        r = recall_score(y_val_fold, pred)
        a = accuracy_score(y_val_fold, pred)
        p = precision_score(y_val_fold, pred)
        # Store results in your results data frame 
        precision.append(p)
        recall.append(r)
        accuracy.append(a)
    r_mean = np.array(precision).mean()
    p_mean = np.array(recall).mean()
    a_mean = np.array(accuracy).mean()
        
    return (model_obj, p_mean, a_mean, r_mean)

def grid_search(train, features, target, models, grid):
    '''
    Loops through the parameters in the grid and finds the best model
    Inputs:
        train: training dataframe
        test: testing dataframe
        models: dictionary specifying the models
        gris: dictionary specifying the parameters for each model
    Output:
        Returns a table summarizing each of the model specifications and its F1 
        and accuracy score and the best model defined as the model with higher 
        accuracy score.
    '''

    cols = ['params', 'precision', 'accuracy', 'recall']
    best_score = 0
    best_model = None
    results = pd.DataFrame(columns=cols)

    for model_key in models.keys(): 

        for params in grid[model_key]:
            print("Training model:", model_key, "|", params)
            model_obj, p, a, r = upsampling(train, features, target, models[model_key], params)
            new_row = {'params': params, 'precision': p, 'accuracy': a, 'recall': r}
            results = results.append(new_row, ignore_index=True)
            
            if r > best_score:
                best_score = r
                best_model = model_obj
        
    return results, best_model
