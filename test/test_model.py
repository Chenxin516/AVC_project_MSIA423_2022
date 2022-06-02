import pytest
import sys
import os
import pandas as pd
import numpy as np

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from model import clean_data


def test_clean_data():
    """test (clean_data()): happy path for clean_data function"""
    # Define input Dictionary
    input = pd.DataFrame(
        [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 'Yes'], [1, 2, np.nan, 3, 4, 55, 3, 4, 4, 2, 3, 1, 'No'],
         [1, 2, 5, 4, np.nan, 3, 4, 4, 2, 3, 1, 'Yes']],
        columns=['EmployeeNumber', 'EnvironmentSatisfaction', 'JobInvolvement', 'JobLevel',
                 'JobSatisfaction', 'PerformanceRating', 'RelationshipSatisfaction',
                 'YearsSinceLastPromotion', 'WorkLifeBalance', 'Gender_Male',
                 'MaritalStatus_Married', 'MaritalStatus_Single', 'OverTime_Yes', 'Attrition'])

    missing_col = ['JobSatisfaction', 'JobInvolvement']

    columns = ['EmployeeNumber', 'EnvironmentSatisfaction', 'JobInvolvement', 'JobLevel',
               'JobSatisfaction', 'PerformanceRating', 'RelationshipSatisfaction',
               'YearsSinceLastPromotion', 'WorkLifeBalance', 'Gender_Male',
               'MaritalStatus_Married', 'MaritalStatus_Single', 'Attrition']

    # Define expected output, df_true
    df_true = pd.DataFrame(
        [[1, 1.0, 1, 1.0, 1, 1, 1, 1, 1, 0, 1]],
        index=[0],
        columns=['EnvironmentSatisfaction', 'JobInvolvement', 'JobLevel',
                 'JobSatisfaction', 'PerformanceRating', 'RelationshipSatisfaction',
                 'YearsSinceLastPromotion', 'WorkLifeBalance', 'Gender_Male',
                 'MaritalStatus_Married', 'Attrition'])

    df_test = clean_data(input, missing_col, columns, output_path='')
    # Test that the true and test are the same
    assert df_test.equals(df_true)


def test_clean_data_bad():
    """test2 (transform_input()): unhappy path """
    input = 'this is not  a dictionary'

    missing_col = ['JobSatisfaction', 'JobInvolvement']

    columns = ['EmployeeNumber', 'EnvironmentSatisfaction', 'JobInvolvement', 'JobLevel',
               'JobSatisfaction', 'PerformanceRating', 'RelationshipSatisfaction',
               'YearsSinceLastPromotion', 'WorkLifeBalance', 'Gender_Male',
               'MaritalStatus_Married', 'MaritalStatus_Single', 'Attrition']

    with pytest.raises(TypeError):
        clean_data(input, missing_col, columns, output_path='')
