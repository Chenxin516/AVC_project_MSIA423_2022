
import pytest
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.realpath(__file__)) + '/../src')
from predict import transform_input



def test_transform_input():
    """test1 (transform_input()): happy path for transform input"""
    # Define input Dictionary
    input = {'EmployeeNumber': 1, 'EnvironmentSatisfaction': 1, 'JobInvolvement': 1, 'JobLevel': 1,
             'JobSatisfaction': 1, 'PerformanceRating': 1, 'RelationshipSatisfaction': 1,
             'YearsSinceLastPromotion': 1, 'WorkLifeBalance': 1, 'MaritalStatus': 'Divorced', 'Gender': 'Male',
             'OverTime': 'Yes'}

    # Define expected output, df_true
    df_true = pd.DataFrame(
        [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1]],
        index=[0],
        columns=['EmployeeNumber', 'EnvironmentSatisfaction', 'JobInvolvement', 'JobLevel',
                 'JobSatisfaction', 'PerformanceRating', 'RelationshipSatisfaction',
                 'YearsSinceLastPromotion', 'WorkLifeBalance', 'Gender_Male',
                 'MaritalStatus_Married', 'MaritalStatus_Single', 'OverTime_Yes'])

    df_test = transform_input(input)
    # Test that the true and test are the same
    assert df_test.equals(df_true)


def test_transform_input_bad():
    """test2 (transform_input()): unhappy path """
    sample_input = 'this is not  a dictionary'

    with pytest.raises(ValueError):
        transform_input(sample_input)
