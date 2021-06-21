"""
Config file for tests with all of the fixtures shared by the tests. Since some
of the tasks would take too long, the fixtures are session-scoped.
"""

import os
import pytest
import src.schools_pkg.parsing as sc_parsing
from src.population_pkg import calculate
from src.population_pkg import save
import src.schools_for_ages as sfa


@pytest.fixture(scope="session")
def schools_path():
    # pytest changes wd to testing directory, so we move back
    real_wd = os.path.dirname(os.getcwd())
    return os.path.join(real_wd, 'data\\Wykaz_szkół_i_placówek_wg_stanu_na_30.IX._2018_w.5.xlsx')


@pytest.fixture(scope="session")
def population_path():
    real_wd = os.path.dirname(os.getcwd())
    return os.path.join(real_wd, 'data\\Ludność. Stan i struktura_30.06.2020')


@pytest.fixture(scope="session")
def schools_loaded(schools_path):
    return sc_parsing.load_schools_df(schools_path)


@pytest.fixture(scope="session")
def schools_regonized(schools_loaded):
    return sc_parsing.set_regon_as_index(schools_loaded)


@pytest.fixture(scope="session")
def schools_no_delegatures(schools_regonized):
    return sc_parsing.drop_delegatures(schools_regonized)


@pytest.fixture(scope="session")
def schools_sum_teachers(schools_no_delegatures):
    return sc_parsing.sum_teachers(schools_no_delegatures)


@pytest.fixture(scope="session")
def schools_reallocated(schools_sum_teachers):
    sc_parsing.reallocate_teachers_per_regon(schools_sum_teachers)
    return schools_sum_teachers


@pytest.fixture(scope="session")
def schools_per_teacher(schools_reallocated):
    schools = schools_reallocated.loc[schools_reallocated['Uczniowie, wychow., słuchacze'] > 0]
    sc_parsing.students_per_teachers_in_school(schools)
    return schools


@pytest.fixture(scope="session")
def schools_simplified(schools_per_teacher):
    dropped_now = sfa.simplify_school_types(schools_per_teacher)
    return schools_per_teacher, dropped_now


@pytest.fixture(scope="session")
def schools_gmina_coded(schools_simplified):
    schools, dropped_now = schools_simplified
    sfa.update_with_gmina_codes(schools)
    return schools


@pytest.fixture(scope="session")
def schools_voivodeships(schools_gmina_coded):
    sfa.update_voivodeship_names(schools_gmina_coded)
    return schools_gmina_coded


@pytest.fixture(scope="session")
def schools_trimmed(schools_voivodeships):
    return sfa.trim_schools_for_population(schools_voivodeships)


@pytest.fixture(scope="session")
def schools_preschooled(schools_trimmed):
    return sfa.reallocate_preschool(schools_trimmed)


@pytest.fixture(scope="session")
def per_age_df(schools_preschooled, population_path):
    return calculate.students_per_age(schools_preschooled, population_path)


@pytest.fixture(scope="session")
def per_year(per_age_df):
    per_age, dropped_now = per_age_df
    per_age.columns = per_age.columns.map(lambda x: 2018 - x)
    return per_age


@pytest.fixture(scope="session")
def per_year_gminatyped(per_year):
    save.add_gmina_types(per_year)
    return per_year
