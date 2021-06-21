"""
Provide methods used to load and properly parse official data about population.
"""

import pandas as pd
import os.path


def fix_index_and_cols(population: pd.DataFrame) -> pd.DataFrame:
    """
    Name columns, fix values in those columns so that they can be used as index,
    then set them as MultiIndex.

    :param population: dataframe with data about population
    :return: dataframe, updated
    """
    population.columns = ['Specification', 'Code', 'Total']
    for i in population.index:
        if population.loc[i, 'Code'] != '       ':
            last_code = population.loc[i, 'Code']
        else:
            population.loc[i, 'Code'] = last_code
    # Unify codes, since '023' can only be str, but 123 is naturally int
    population.loc[:, 'Code'] = population.loc[:, 'Code'].map(str)
    return population.set_index(['Code', 'Specification'])


def load_population_df(population_path: str, sheetname: str) -> pd.DataFrame:
    """
    Read selected sheet from the file and parse it.

    :param population_path: where population data is located
    :param sheetname: name of the sheet (voivodeship)
    :return: loaded dataframe
    """
    # Fix incorrect sheetname in tabela12.xls
    if sheetname == 'Śląskie':
        sheetname = 'Śląske'
    population = pd.read_excel(os.path.join(population_path, 'tabela12.xls'),
                               sheet_name=sheetname, skiprows=8, header=None, usecols='A:C')
    return fix_index_and_cols(population)
