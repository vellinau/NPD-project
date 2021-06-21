"""
Provide methods used to save per age results.
"""

import pandas as pd
from src.population_pkg import calculate


def add_gmina_types(per_age: pd.DataFrame):
    """
    Convert gmina types from numbers back to strings.

    :param per_age: how many students are there for each age in each gmina
    """
    gminatypes_converter = {'1': 'M', '2': 'Gm', '3': 'M-Gm'}

    per_age.loc[:, 'Typ gminy'] = per_age.index.str[-1].map(gminatypes_converter)


def save_per_age_statistics(per_age: pd.DataFrame, outfile: str):
    """
    Run calculations (min, max, mean, median of students per school for each year of birth
    in each type of gmina) and save the results to the file.

    :param per_age: how many students are there for each year of birth in each gmina
    :param outfile: where to save results
    """
    add_gmina_types(per_age)

    df1 = calculate.statistics_for_type(per_age, 'Gm')
    df2 = calculate.statistics_for_type(per_age, 'M')
    df3 = calculate.statistics_for_type(per_age, 'M-Gm')

    print(f'Printing out to {outfile}...\n')
    df1.append([df2, df3]).to_excel(outfile)
