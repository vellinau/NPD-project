"""
Modify schools df from per teacher analysis for use in per age analysis.
"""

import pandas as pd


def simplify_school_types(schools: pd.DataFrame) -> int:
    """
    Simplify school types that typically have the exactly same range. If some
    type of school has unclear age range, drop it.

    :param schools: pd.DataFrame from per_teacher_analysis
    :return: how much data was dropped
    """
    types_simplified = {}

    for przedszkole in ['Przedszkole', 'Punkt przedszkolny', 'Zespół wychowania przedszkolnego']:
        types_simplified[przedszkole] = 'Przedszkole'
    for podstawowka in ['Szkoła podstawowa', 'Ogólnokształcąca szkoła muzyczna I stopnia']:
        types_simplified[podstawowka] = 'Szkoła podstawowa'
    for zawodowka in ['Branżowa szkoła I stopnia', 'Szkoła specjalna przysposabiająca do pracy']:
        types_simplified[zawodowka] = 'Zawodówka'
    for liceum in ['Czteroletnie liceum plastyczne', 'Ogólnokształcąca szkoła muzyczna II stopnia',
                   'Liceum ogólnokształcące']:
        types_simplified[liceum] = 'Liceum ogólnokształcące'
    for school in ['Gimnazjum', 'Technikum', 'Sześcioletnia ogólnokształcąca szkoła sztuk pięknych',
                   'Dziewięcioletnia ogólnokształcąca szkoła baletowa']:
        types_simplified[school] = school

    mask = schools['Nazwa typu'].isin(types_simplified.keys())

    dropped_now = schools.loc[~mask, "Uczniowie, wychow., słuchacze"].sum()
    print(f'{dropped_now} students are enrolled in {(~mask).sum()} schools with unclear age range. '
          f'Dropping...')

    schools.loc[:, 'Nazwa typu'] = schools['Nazwa typu'].map(types_simplified)
    schools = schools.loc[mask]

    return dropped_now


def update_with_gmina_codes(schools: pd.DataFrame):
    """
    For each gmina, generate its 7-digit code.

    Each pair of the first 6 digits is taken directly from data, with leading
    zero added if necessary. The last digit is converted to number from
    gminatype.

    :param schools: pd.DataFrame from per_teacher_analysis
    """
    gminatypes_converter = {'M': '1', 'Gm': '2', 'M-Gm': '3'}

    # Convert 1,2,13 -> 01,02,13.
    for column in ['woj', 'pow', 'gm']:
        schools.loc[:, column] = schools[column].apply(str)
        schools.loc[:, column] = schools[column].str.zfill(2)

    schools.loc[:, 'Kod gminy'] = schools['woj'] + schools['pow'] + \
        schools['gm'] + schools['Typ gminy'].map(gminatypes_converter)


def update_voivodeship_names(schools: pd.DataFrame):
    """
    Discard 'WOJ. ' and capitalize voivodeship names, for connection to
    population df.

    :param schools: pd.DataFrame from per_teacher_analysis
    """
    schools.loc[:, 'Województwo'] = schools['Województwo'].str[5:]
    schools.loc[:, 'Województwo'] = schools['Województwo'].str.capitalize()


def trim_schools_for_population(schools: pd.DataFrame) -> pd.DataFrame:
    """
    Drop all the info not needed to calculate per age statistics for each gmina.
    Count the schools.

    :param schools: pd.DataFrame from per_teacher_analysis
    :return: dataframe, edited
    """
    schools.loc[:, 'Liczba szkół'] = 1
    schools = schools.groupby(['Województwo', 'Kod gminy', 'Nazwa typu']).sum()

    irrelevant_cols = ['Złożoność', 'w tym dziewczęta', 'w tym w oddziałach innego typu',
                       'Oddziały', 'Regon jednostki sprawozdawczej', 'Nauczyciele',
                       'Uczniów na etat nauczycielski']

    return schools.drop(irrelevant_cols, axis=1)


def reallocate_preschool(schools: pd.DataFrame) -> pd.DataFrame:
    """
    Reallocate preschoolers from primary school to preschool if necessary, so
    they are counted in their own age range.

    :param schools: pd.DataFrame from per_teacher_analysis
    :return: dataframe, edited
    """
    mask = schools['w tym w oddziałach przedszk.'] > 0
    assert schools.loc[mask].index.get_level_values('Nazwa typu').unique(
    ) == 'Szkoła podstawowa', 'Evidently not all extra preschoolers are enrolled in primary ' \
                              'school -- let the analyst know!'

    for gmina in schools.loc[mask].index.get_level_values('Kod gminy'):
        voivodeship = schools.loc[:, gmina, :].index.get_level_values('Województwo')[0]
        extra_preschool = schools.loc[(voivodeship, gmina, 'Szkoła podstawowa'),
                                      'w tym w oddziałach przedszk.'].sum()
        schools.loc[(voivodeship, gmina, 'Szkoła podstawowa'),
                    'Uczniowie, wychow., słuchacze'] -= extra_preschool
        if (voivodeship, gmina, 'Przedszkole') in schools.index:
            schools.loc[(voivodeship, gmina, 'Przedszkole'),
                        'Uczniowie, wychow., słuchacze'] += extra_preschool
        else:
            schools.loc[(voivodeship, gmina, 'Przedszkole')] = [extra_preschool, 0, 0]
            # Resort index after inserting new row
            schools = schools.sort_index()

    return schools.drop(['w tym w oddziałach przedszk.'], axis=1)
