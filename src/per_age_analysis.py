"""
Using schools df from per_teacher_analysis, modify it, then calculate and
save per age statistics.
"""

import pandas as pd
from src.population_pkg.calculate import students_per_age
from src.population_pkg.save import save_per_age_statistics
import src.schools_for_ages as sfa


def run(schools: pd.DataFrame, population_path: str, outpath_per_age: str) -> int:
    """
    Perform per age analysis.

    :param schools: pd.DataFrame from per_teacher_analysis
    :param population_path: directory with data about population
    :param outpath_per_age: where to save the results
    :return: how much data was dropped
    """
    all_dropped = 0

    dropped_now = sfa.simplify_school_types(schools)
    all_dropped += dropped_now

    sfa.update_with_gmina_codes(schools)
    sfa.update_voivodeship_names(schools)
    schools = sfa.trim_schools_for_population(schools)
    schools = sfa.reallocate_preschool(schools)

    per_age, dropped_now = students_per_age(schools, population_path)
    all_dropped += dropped_now

    # Convert ages to year of birth (and the main data is from 2018)
    per_age.columns = per_age.columns.map(lambda x: 2018 - x)
    save_per_age_statistics(per_age, outpath_per_age)

    return all_dropped
