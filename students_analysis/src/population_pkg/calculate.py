"""
Provide methods used to calculate max, min, median, mean of the number of
students per school for each year of birth in different types of gminas.
"""

import pandas as pd
from src.population_pkg import parsing


def agerange_for_school() -> dict:
    """
    Create a dictionary with age range for each type of school.

    :return: a dictionary with age range for each type of school
    """
    school_ages = {}
    school_ages['Przedszkole'] = list(range(3, 7))
    school_ages['Szkoła podstawowa'] = list(range(7, 15))
    school_ages['Gimnazjum'] = list(range(13, 16))
    school_ages['Zawodówka'] = list(range(15, 18))
    school_ages['Dziewięcioletnia ogólnokształcąca szkoła baletowa'] = list(range(10, 19))
    school_ages['Sześcioletnia ogólnokształcąca szkoła sztuk pięknych'] = list(range(13, 19))
    school_ages['Liceum ogólnokształcące'] = list(range(15, 19))
    school_ages['Technikum'] = list(range(15, 20))
    return school_ages


def students_per_age(schools: pd.DataFrame, population_path: str) -> (pd.DataFrame, int):
    """
    Calculate how much students are there in each gmina for each age. Drop
    gmina if unable to locate data about population for this code.

    :param schools: dataframe with data about schools
    :param population_path: where data about population is located
    :return:
        - dataframe with how many students are there for each age
        - how much data was dropped
    """
    school_ages = agerange_for_school()
    per_age = pd.DataFrame(columns = list(range(3, 20)))
    # Ages in population df are in form of '       2 ' or '       22'
    current_ages = [str(age).ljust(2).rjust(9) for age in range(5, 22)]
    students_dropped = 0

    for sheetname in schools.index.get_level_values('Województwo').unique():
        population = parsing.load_population_df(population_path, sheetname)

        for gmina in schools.loc[sheetname].index.get_level_values('Kod gminy').unique():
            try:
                population_gmina = population.loc[gmina].loc[current_ages]
                per_age.loc[gmina] = per_age_in_gmina(
                    population_gmina, schools, sheetname, gmina, school_ages)
            except KeyError:
                dropping = schools.loc[sheetname, gmina, :].sum()['Uczniowie, wychow., słuchacze']
                students_dropped += dropping
                print(f'No gmina with code {gmina} in population data. Dropping {dropping} '
                      f'students...')

    return per_age, students_dropped


def per_age_in_gmina(population_gmina: pd.DataFrame, schools: pd.DataFrame, sheetname: str,
                     gmina: str, school_ages: dict) -> dict:
    """
    In selected gmina, calculate how much students are there for each age.

    :param population_gmina: part of population dataframe corresponding to gmina
    :param schools: dataframe with data about schools
    :param sheetname: name of gmina's voivodeship, corresponding to sheetname
    :param gmina: gmina code
    :param school_ages: a dictionary with age range for each type of school
    :return: dict of how much students are there for each age
    """
    # Now we convert ages to ints and subtract 2, since data from schools are
    # from 2 years earlier
    population_gmina.index = population_gmina.index.map(int) - 2

    all_schools = schools.loc[sheetname, gmina, :].sum()['Liczba szkół']
    students_per_age_school = {age: 0 for age in range(3, 20)}

    for school in schools.loc[sheetname, gmina, :].index.get_level_values('Nazwa typu'):
        all_eligible = population_gmina.loc[school_ages[school]].sum()['Total']
        for age in school_ages[school]:
            age_proportion = population_gmina.loc[age, 'Total'] / all_eligible
            students_per_age_school[age] += age_proportion * schools.loc[(
                sheetname, gmina, school), 'Uczniowie, wychow., słuchacze'] / all_schools

    return students_per_age_school


def statistics_for_type(per_age: pd.DataFrame, gmina_type: str) -> pd.DataFrame:
    """
    Calculate max, min, median, mean of the number of students per school for
    each year of birth in selected type of gmina.

    :param per_age: how many students are there for each year of birth in each gmina
    :param gmina_type: which type of gmina do we select
    :return: dataframe with results
    """
    mask = per_age['Typ gminy'] == gmina_type
    per_age = per_age.drop(['Typ gminy'], axis=1)

    stat_cols = {'Maks. uczniów na szkołę': per_age.loc[mask].max(),
                 'Min. uczniów na szkołę': per_age.loc[mask].min(),
                 'Mediana uczniów na szkołę': per_age.loc[mask].median(),
                 'Średnia uczniów na szkołę': per_age.loc[mask].mean()}
    stats = pd.DataFrame(stat_cols)

    stats.loc[:, 'Rok urodzenia'] = stats.index
    stats.loc[:, 'Typ gminy'] = gmina_type
    return stats.set_index(['Typ gminy', 'Rok urodzenia'])
