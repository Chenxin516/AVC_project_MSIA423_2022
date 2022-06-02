import logging
from typing import List

import numpy as np
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import metrics

logger = logging.getLogger(__name__)


def get_data(file: str) -> pd.DataFrame:
    """
    input (str): location of the dataset
    output (pd.dataframe): loaded dataframe
    """
    try:
        df = pd.read_csv(file)
        logger.info("read df from data file")
    except FileNotFoundError:
        logger.error("file not found from the local directory, please download data from S3 first")
    return df


def clean_data(data: pd.DataFrame, missing_col: List[str], columns: List[str], output_path='./data/raw'
                                                                                           '/employee_results.csv') \
        -> pd.DataFrame:
    """Clean_date.
    Args:
        data (pd.DataFrame):raw dataframe downloaded
        missing_col (list(str)): missing columns
        columns (list(str)): columns to be selected
        output_path (str): output path to save processed data
    Returns:
        df_model (dataframe): cleaned dataframe ready for modeling
    """
    # impute missing numeric col with mean
    for col in missing_col:
        for i in data[data[col].isna()].index.tolist():
            data[col][i] = data.mean()[col]

    # dave processed data
    data.dropna(axis=0, inplace=True)
    df = data[columns]
    df['EmployeeNumber'] = data['EmployeeNumber']
    if output_path == '':
        pass
    else:
        df.to_csv(output_path, index=False)

    df = df.drop(columns=['EmployeeNumber'])
    # convert target variables to 1 and 0
    df['Attrition'] = df['Attrition'].map({'Yes': 1, 'No': 0})
    # label encode categorical variables
    df_model = pd.get_dummies(df.loc[:, df.columns != "Attrition"], drop_first=True)

    df_model['Attrition'] = df['Attrition']

    return df_model


def split_data(df_model: pd.DataFrame, test_size: float, random_state: int) \
        -> [pd.DataFrame, pd.Series, pd.DataFrame, pd.Series]:
    """Split train and test data
       Args:
           df_model (pd.DataFrame): preprocessed dataframes for model training
           test_size (float): ratio of test data to the entire data
           random_state (int): random state
       Returns:
           X_train(pd.Dataframe): x variables of train data
           X_test(pd.Dataframe): x variables of test data
           y_train(pd.Series): y variables of test data
           y_test(pd.Series): y variables of test data
    """
    y = df_model['Attrition']
    X = df_model.drop(columns=['Attrition'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=random_state)
    logger.debug('Split data to training and testing sets')
    return [X_train, X_test, y_train, y_test]


def train_model(X_train: pd.DataFrame, y_train: pd.Series, max_depth: int,
                n_estimators: int) -> RandomForestClassifier:
    """
    train and save classifier model
    Args:
        X_train(pd.Dataframe): x variables of train data
        y_train(pd.Series): y variables of test data
        n_estimators (int): number of trees in the forest
        max_depth (int): maximum depth of trees
    Returns:
        final_rf(sklearn.RandomForestClassifier): trained random forest model
    """

    final_rf = RandomForestClassifier(bootstrap=False,
                                      max_depth=max_depth,
                                      n_estimators=n_estimators)
    final_rf.fit(X_train, y_train)

    logger.info("Classifier model trained")

    return final_rf


def predict(final_rf: RandomForestClassifier, X_test: pd.Series) -> [np.array, np.array]:
    """Make predictions on test data
       Args:
           final_rf(sklearn.RandomForestClassifier): trained random forest model
           X_test(pd.Dataframe): x variables of test data
       Returns:
           y_pred(np.ndarray): predicted values
    """
    logger.info("Score model")
    ypred_bin_test = final_rf.predict(X_test)
    logger.debug('Made predictions')
    ypred_proba_test = final_rf.predict_proba(X_test)[:, 1]
    return [ypred_proba_test, ypred_bin_test]


def evaluation(y_test: pd.Series, ypred_proba_test: np.array, ypred_bin_test: np.array) -> pd.DataFrame:
    """Evaluate model performance
       Args:
           y_test(pd.Series): y variables of test data
           ypred_proba_test (np array): predicted probability for test dataset
           ypred_bin_test (np array): predicted label for test dataset
       Returns:
           result(pd.Dataframe): result of evaluation
    """
    auc = metrics.roc_auc_score(y_test, ypred_proba_test)
    accuracy = metrics.accuracy_score(y_test, ypred_bin_test)
    confusion = metrics.confusion_matrix(y_test, ypred_bin_test)
    result = pd.DataFrame(confusion,
                          index=['Actual negative', 'Actual positive'],
                          columns=['Predicted negative', 'Predicted positive'])

    print('AUC on test: %0.3f' % auc)
    print('Accuracy on test: %0.3f' % accuracy)
    print(result)
    return result
