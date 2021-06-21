"""
Loading data about schools from the path, modify it, then calculate and save
per teacher statistics.
"""

import pandas as pd
import src.schools_pkg.parsing as parsing
from src.schools_pkg.save import save_gmina_statistics
from src.schools_pkg.save import save_gminatype_statistics


def run(schools_path: str, outpath_gmina: str, outpath_gminatype: str) -> (pd.DataFrame, int):
    """
    Perform per teacher analysis.

    :param schools_path: path to file with data about schools
    :param outpath_gmina: where to save results for all gminas
    :param outpath_gminatype: where to save results for gminas grouped by their type
    :return:
        - pd.DataFrame with data for further calculations
        - how much data was dropped
    """
    schools = parsing.load_schools_df(schools_path)
    students_at_start = schools['Uczniowie, wychow., słuchacze'].sum()

    schools = parsing.set_regon_as_index(schools)
    schools = parsing.drop_delegatures(schools)
    schools = parsing.sum_teachers(schools)
    parsing.reallocate_teachers_per_regon(schools)
    # After reallocating teachers, we can freely discard data from schools with no students
    schools = schools.loc[schools['Uczniowie, wychow., słuchacze'] > 0]
    parsing.students_per_teachers_in_school(schools)

    save_gmina_statistics(schools, outpath_gmina)
    save_gminatype_statistics(schools, outpath_gminatype)

    students_dropped = students_at_start - schools['Uczniowie, wychow., słuchacze'].sum()

    return schools, students_dropped
