import logging
import numpy as np
import joblib
from sklearn.ensemble import RandomForestClassifier
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import metrics

logger = logging.getLogger(__name__)


def get_data(file='data/raw/employee_attrition_train.csv'):
    """
    input: location of the dataset
    output: dataframe
    """
    try:
        df = pd.read_csv(file)
        logger.info("read df from data file")
    except FileNotFoundError:
        logger.error("file not found from the local directory, please download data from S3 first")
    return df


def clean_data(data: pd.DataFrame):
    """Clean_date.
    Args:
        data (pd.DataFrame):raw dataframe downloaded
    Returns:
        df_model (dataframe): cleaned dataframe ready for modeling
    """
    # impute missing numeric col with mean
    missing_col = ['Age', 'DailyRate', 'DistanceFromHome']
    for col in missing_col:
        for i in data[data[col].isna()].index.tolist():
            data[col][i] = data.mean()[col]

    # drop missing categorical col
    data.dropna(axis=0, inplace=True)
    df = data[['EnvironmentSatisfaction', 'Attrition', 'Gender', 'JobInvolvement', 'JobLevel', 'JobSatisfaction',
               'MaritalStatus',
               'OverTime', 'PerformanceRating', 'RelationshipSatisfaction', 'WorkLifeBalance',
               'YearsSinceLastPromotion']]
    # convert target variables to 1 and 0
    df['Attrition'] = df['Attrition'].map({'Yes': 1, 'No': 0})
    # label encode categorical variables
    df_model = pd.get_dummies(df.loc[:, df.columns != "Attrition"], drop_first=True)

    df_model['Attrition'] = df['Attrition']

    return df_model


def split_data(df_model):
    """Split train and test data
       Args:
           df_model (pd.DataFrame): preprocessed dataframes for model training
       Returns:
           X_train(pd.Dataframe): x variables of train data
           X_test(pd.Dataframe): x variables of test data
           y_train(pd.Series): y variables of test data
           y_test(pd.Series): y variables of test data
    """
    y = df_model['Attrition']
    X = df_model.drop(columns=['Attrition'])
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=101)
    logger.debug('Split data to training and testing sets')
    return X_train, X_test, y_train, y_test


def train_model(X_train, y_train, output_model_path="./models/random_forest.sav"):
    """
    train and save classifier model
    Args:
        X_train(pd.Dataframe): x variables of train data
        y_train(pd.Series): y variables of test data
        output_model_path(str): path to saved trained model
    Returns:
        final_rf(sklearn.RandomForestClassifier): trained random forest model
    """

    final_rf = RandomForestClassifier(bootstrap=False,
                                      max_depth=50,
                                      min_samples_leaf=8,
                                      min_samples_split=8,
                                      n_estimators=200)
    final_rf.fit(X_train, y_train)

    logger.info("Classifier model trained")

    joblib.dump(final_rf, output_model_path)

    logger.info("Classifier model saved to %s" % output_model_path)

    return final_rf


def predict(final_rf, X_test):
    """Make predictions on test data
       Args:
           final_rf(sklearn.RandomForestClassifier): trained random forest model
           X_test(pd.Dataframe): x variables of test data
       Returns:
           y_pred(np.ndarray): predicted values
    """
    y_pred = final_rf.predict(X_test)
    logger.debug('Made predictions')
    return y_pred


def evaluation(y_test, y_pred):
    """Evaluate model performance
       Args:
           y_test(pd.Series): y variables of test data
           y_pred(np.ndarray): predicted values
       Returns:
           result(pd.Dataframe): result of evaluation
    """
    accuracy = metrics.accuracy_score(y_test, y_pred)
    confusion = metrics.confusion_matrix(y_test, y_pred)
    result = pd.DataFrame(confusion,
                          index=['Actual negative', 'Actual positive'],
                          columns=['Predicted negative', 'Predicted positive'])

    print('Accuracy on test: %0.3f' % accuracy)
    print(result)
    return result

