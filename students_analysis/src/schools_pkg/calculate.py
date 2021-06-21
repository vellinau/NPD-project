"""
Provide methods used to calculate max, min, median, mean of the number of
students per teacher in gmina for different types of grouping.
"""

import pandas as pd


def basic_statistics(group: pd.DataFrame) -> pd.DataFrame:
    """
    For provided group, calculate max, min, median, mean of the number of
    students per teacher in gmina.

    :param group: group of rows in pd.DataFrame
    :return: group, with new columns appended
    """
    sum_teachers = group['Nauczyciele'].sum()
    sum_students = group['Uczniowie, wychow., słuchacze'].sum()

    maximum = group['Uczniów na etat nauczycielski'].max()
    minimum = group['Uczniów na etat nauczycielski'].min()
    median = group['Uczniów na etat nauczycielski'].median()

    group['Maks. uczniów na etat'], group['Min. uczniów na etat'] = maximum, minimum
    group['Mediana uczniów na etat'] = median
    group['Średnia uczniów na etat'] = sum_students / sum_teachers

    return group


def group_schools_with_statistics(schools: pd.DataFrame, groupby_cols: list, irrelevant_cols:
                                  list) -> pd.DataFrame:
    """
    Calculate basic statistics for provided type of grouping.

    :param schools: pd.DataFrame with data about schools
    :param groupby_cols: which columns identify a group
    :param irrelevant_cols: which columns are irrelevant and should be dropped
    :return: dataframe, edited
    """
    mask = schools['Nauczyciele'] > 0
    schools_grouped = schools.loc[mask].groupby(groupby_cols).apply(basic_statistics)
    # All the values are the same in each row in group, so we just take the last one
    schools_grouped = schools_grouped.groupby(groupby_cols).last()

    return schools_grouped.drop(irrelevant_cols, axis=1)
