"""
Provide methods used to load and properly parse official data about schools.
"""

import pandas as pd


def load_schools_df(schools_path: str) -> pd.DataFrame:
    """
    Load data about schools to a dataframe.

    :param schools_path: where data about schools is located
    :return: loaded dataframe
    """
    cols_to_use = ['Lp.', 'woj', 'pow', 'gm', 'Województwo', 'Powiat', 'Gmina', 'Typ gminy',
                   'Miejscowość', 'Nazwa typu', 'Złożoność', 'Nazwa szkoły, placówki', 'Regon',
                   'Uczniowie, wychow., słuchacze', 'w tym dziewczęta',
                   'w tym w oddziałach przedszk.', 'w tym w oddziałach innego typu', 'Oddziały',
                   'Nauczyciele pełnozatrudnieni', 'Nauczyciele niepełnozatrudnieni (w etatach)',
                   'Regon jednostki sprawozdawczej']
    # Row no. 1 is empty
    schools = pd.read_excel(schools_path, index_col=0, na_filter=False,
                            usecols=cols_to_use, skiprows=[1])
    assert (schools.columns == cols_to_use[1:]).all()
    return schools


def drop_duplicate_regon(schools: pd.DataFrame) -> pd.DataFrame:
    """
    Drop schools with duplicate REGONs from the dataframe.

    :param schools: dataframe with data about schools
    :return: dataframe, edited
    """
    duplicates = schools.duplicated(['Regon'])
    print(f'{schools.loc[duplicates, "Uczniowie, wychow., słuchacze"].sum()} students from '
          f'{duplicates.sum()} schools with duplicated REGON found. Dropping...')
    return schools[~duplicates]


def set_regon_as_index(schools: pd.DataFrame) -> pd.DataFrame:
    """
    Set REGON as index to a dataframe once duplicates are dropped.

    :param schools: dataframe with data about schools
    :return: dataframe, edited
    """
    schools = drop_duplicate_regon(schools)
    return schools.set_index('Regon')


def drop_delegatures(schools: pd.DataFrame) -> pd.DataFrame:
    """
    Drop facilities that are in fact delegatures, not schools.

    :param schools: dataframe with data about schools
    :return: dataframe, edited
    """
    delegatures = schools['Złożoność'] == 4
    print(f'{schools.loc[delegatures, "Uczniowie, wychow., słuchacze"].sum()} students from '
          f'{delegatures.sum()} delegatures found. Dropping...')
    return schools[~delegatures]


def sum_teachers(schools: pd.DataFrame) -> pd.DataFrame:
    """
    Sum two of the teacher columns to get one number of full-time jobs.

    :param schools: dataframe with data about schools
    :return: dataframe, edited
    """
    teacher_cols = ['Nauczyciele pełnozatrudnieni', 'Nauczyciele niepełnozatrudnieni (w etatach)']
    schools['Nauczyciele'] = schools.loc[:, teacher_cols].sum(axis=1)
    return schools.drop(teacher_cols, axis=1)


def reallocate_teachers_per_regon(schools: pd.DataFrame):
    """
    Reallocate teachers between interconnected facilities, so that their number
    correspond to the number of classes (or students) in each school.

    :param schools: dataframe with data about schools
    """
    regons = schools.loc[schools.duplicated(
        ['Regon jednostki sprawozdawczej']), 'Regon jednostki sprawozdawczej'].unique()
    bad_regon_count = 0

    for regon in regons:
        mask_regon = schools['Regon jednostki sprawozdawczej'] == regon
        if (schools.loc[mask_regon, 'Złożoność'] == 1).sum() > 1:
            print(
                f'There are several schools of level 1 with REGON equal {regon}. '
                f'Data might be innacurate.')
        # Assume the ratio of teachers to classes is constant in one facility
        all_teachers = schools.loc[mask_regon, 'Nauczyciele'].sum()
        all_classes = schools.loc[mask_regon, 'Oddziały'].sum()
        if all_classes > 0:
            for i in schools.loc[mask_regon].index:
                school_classes = schools.loc[i, 'Oddziały']
                schools.loc[i, 'Nauczyciele'] = all_teachers * school_classes/all_classes
        else:
            # If there are no classes, we can assume contant ratio of teachers to students
            all_students = schools.loc[mask_regon, 'Uczniowie, wychow., słuchacze'].sum()
            if all_students > 0:
                for i in schools.loc[mask_regon].index:
                    school_students = schools.loc[i, 'Uczniowie, wychow., słuchacze']
                    schools.loc[i, 'Nauczyciele'] = all_teachers * school_students/all_students
            else:
                bad_regon_count += 1

    if bad_regon_count > 0:
        print(f'{bad_regon_count} facilities are not connected to any classes or students; '
              f'teachers not reallocated.')


def students_per_teachers_in_school(schools: pd.DataFrame):
    """
    Add new column with number of students per teacher in school.

    :param schools: dataframe with data about schools
    """
    mask = schools['Nauczyciele'] > 0
    students = schools.loc[mask, 'Uczniowie, wychow., słuchacze']
    teachers = schools.loc[mask, 'Nauczyciele']
    schools.loc[mask, 'Uczniów na etat nauczycielski'] = students / teachers
