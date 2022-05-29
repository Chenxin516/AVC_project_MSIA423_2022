import logging

import joblib
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


def transform_input(ui_dict):
    """Transform the user input from the app to get predictions using the trained model
    Args:
        ui_dict (dict): a dictionary of user input, collected from the app
    Returns:
        input_new (:obj:`DataFrame <pandas.DataFrame>`): DataFrame that
            stores the transformed user input
    """
    # transform the user input into a pandas DataFrame
    input_df = pd.DataFrame(ui_dict, index=[0])
    logger.debug('Initial Input column names: %s', input_df.columns)

    # change column names to match the one-hot-encoded column names

    df_new = pd.get_dummies(input_df, drop_first=True)
    logger.debug('Column names after all transformation steps: %s', df_new.columns)
    return df_new


def prediction(input_df, model_path):
    """Get loan delinquency prediction for new user input
    Args:
        input_df (:obj:`DataFrame <pandas.DataFrame>`): a DataFrame of the transformed user input
        model_path (str): the path to trained model;
            default is 'models/randomforest.joblib' (config.yaml)

    Returns:
        [pred_label, pred_prob] (:obj:`list`): the first object is a string indicating attrition
        and the second is a number indicating the probability of attrition
    """
    # load pre-trained model
    try:
        loaded_rf = joblib.load(model_path)
        logger.info('Loaded model from %s', model_path)
    except OSError:
        logger.error('Model is not found from %s', model_path)
    # predict probability of attrition

    pred_prob = np.round(loaded_rf.predict_proba(input_df)[0][1], 2)

    # predict the attrition class
    if loaded_rf.predict(input_df)[0] == 0:
        pred_label = "the employee is not likely to leave"
    else:
        pred_label = "the employee is likely to leave"
    return [pred_label, pred_prob]
