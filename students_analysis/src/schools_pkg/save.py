"""
Provide methods used to save per teacher results.
"""

import pandas as pd
from src.schools_pkg import calculate


def save_gmina_statistics(schools: pd.DataFrame, outfile: str):
    """
    Run calculations (min, max, mean, median of students per teacher in each
    gmina) and save the results to the file.

    :param schools: dataframe with data about schools
    :param outfile: where to save results
    """
    groupby_cols = ['woj', 'pow', 'gm', 'Województwo', 'Powiat', 'Gmina', 'Typ gminy', 'Nazwa typu']

    irrelevant_cols = ['Miejscowość', 'Złożoność', 'Nazwa szkoły, placówki', 'w tym dziewczęta',
                       'w tym w oddziałach przedszk.', 'w tym w oddziałach innego typu', 'Oddziały',
                       'Uczniowie, wychow., słuchacze', 'Nauczyciele',
                       'Regon jednostki sprawozdawczej', 'Uczniów na etat nauczycielski']

    gmina_stats = calculate.group_schools_with_statistics(schools, groupby_cols, irrelevant_cols)

    print(f'Printing out to {outfile}...')
    gmina_stats.to_excel(outfile)


def save_gminatype_statistics(schools: pd.DataFrame, outfile: str):
    """
    Run calculations (min, max, mean, median of students per teacher in each
    type of gmina) and save the results to the file.

    :param schools: dataframe with data about schools
    :param outfile: where to save results
    """
    groupby_cols = ['Typ gminy', 'Nazwa typu']

    irrelevant_cols = ['woj', 'pow', 'gm', 'Województwo', 'Powiat', 'Gmina',
                       'Miejscowość', 'Złożoność', 'Nazwa szkoły, placówki', 'w tym dziewczęta',
                       'w tym w oddziałach przedszk.', 'w tym w oddziałach innego typu', 'Oddziały',
                       'Uczniowie, wychow., słuchacze', 'Nauczyciele',
                       'Regon jednostki sprawozdawczej', 'Uczniów na etat nauczycielski']

    gminatype_stats = calculate.group_schools_with_statistics(
        schools, groupby_cols, irrelevant_cols)

    print(f'Printing out to {outfile}...\n')
    gminatype_stats.to_excel(outfile)
