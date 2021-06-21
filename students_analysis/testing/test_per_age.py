"""
Tests for functions used in per_age_analysis.
"""

import os
import pandas as pd
import src.schools_for_ages as sfa
import src.population_pkg.parsing as pop_parsing
from src.population_pkg import calculate
from src.population_pkg import save


def test_population_df(population_path):
    population = pop_parsing.load_population_df(population_path, 'Śląskie')
    assert population.index.names == ['Code', 'Specification']
    assert population.iloc[0, 0] == 170303


def test_simplify_school_types(schools_simplified):
    schools, dropped_now = schools_simplified
    assert len(schools['Nazwa typu'].unique()) == 9
    assert dropped_now == 313783


def test_gmina_codes(schools_gmina_coded):
    assert schools_gmina_coded['Kod gminy'].iloc[0] == '0201011'
    assert schools_gmina_coded['Kod gminy'].iloc[1000] == '0410033'


def test_voivodeship_names(schools_voivodeships):
    assert schools_voivodeships['Województwo'].iloc[0] == 'Dolnośląskie'
    assert schools_voivodeships['Województwo'].iloc[5000] == 'Mazowieckie'


def test_trim_schools(schools_trimmed):
    assert schools_trimmed.index.names == ['Województwo', 'Kod gminy', 'Nazwa typu']
    assert list(schools_trimmed.columns) == ['Uczniowie, wychow., słuchacze',
                                             'w tym w oddziałach przedszk.', 'Liczba szkół']
    assert schools_trimmed.shape == (8098, 3)


def test_reallocate_preschool(schools_preschooled, schools_voivodeships):
    mask_preschooled = schools_preschooled.index.get_level_values('Nazwa typu') == 'Przedszkole'
    schools_trimmed = sfa.trim_schools_for_population(schools_voivodeships)
    mask_trimmed = schools_trimmed.index.get_level_values('Nazwa typu') == 'Przedszkole'

    assert schools_trimmed.loc[mask_trimmed, 'Uczniowie, wychow., słuchacze'].sum() + \
           schools_trimmed.loc[:, 'w tym w oddziałach przedszk.'].sum() == \
           schools_preschooled.loc[mask_preschooled, 'Uczniowie, wychow., słuchacze'].sum()


def test_per_age_in_gmina(schools_preschooled, population_path):
    school_ages = calculate.agerange_for_school()
    current_ages = [str(age).ljust(2).rjust(9) for age in range(5, 22)]
    population = pop_parsing.load_population_df(population_path, 'Śląskie')
    population_gmina = population.loc['2461011'].loc[current_ages]

    assert calculate.per_age_in_gmina(population_gmina, schools_preschooled,
                                      'Śląskie', '2461011', school_ages) == {3: 9.13311416416632,
                                                                             4: 9.055668011350857,
                                                                             5: 9.448430643486416,
                                                                             6: 9.653109761641568,
                                                                             7: 11.053293529037786,
                                                                             8: 11.43226359289051,
                                                                             9: 11.495425270199298,
                                                                             10: 10.926970174420212,
                                                                             11: 10.320618072255854,
                                                                             12: 9.827956989247312,
                                                                             13: 9.668092987134271,
                                                                             14: 9.330456428819307,
                                                                             15: 13.22276574507958,
                                                                             16: 13.703204219546421,
                                                                             17: 14.123834635562515,
                                                                             18: 11.839363237313972,
                                                                             19: 4.797690602363932}


def test_students_per_age(per_age_df):
    per_age, dropped_now = per_age_df
    assert dropped_now == 15145
    assert per_age.shape == (2457, 17)
    assert list(per_age.iloc[100]) == [18.22077922077922,
                                       18.22077922077922,
                                       17.623376623376625,
                                       14.935064935064934,
                                       17.333333333333332,
                                       22.666666666666668,
                                       22.333333333333332,
                                       18.333333333333332,
                                       20.666666666666668,
                                       19.666666666666668,
                                       15.666666666666666,
                                       15.333333333333334,
                                       0.0,
                                       0.0,
                                       0.0,
                                       0.0,
                                       0.0]


def test_per_year(per_year):
    assert list(per_year.columns) == [2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006,
                                      2005, 2004, 2003, 2002, 2001, 2000, 1999]


def test_add_gmina_types(per_year_gminatyped):
    assert per_year_gminatyped.loc['0201011', 'Typ gminy'] == 'M'
    assert per_year_gminatyped.loc['0201032', 'Typ gminy'] == 'Gm'
    assert per_year_gminatyped.loc['0201043', 'Typ gminy'] == 'M-Gm'


def test_save_per_age_statistics(per_year_gminatyped, tmp_path):
    outfile = os.path.join(tmp_path, 'gminatype_per_teacher.xlsx')
    save.save_per_age_statistics(per_year_gminatyped, outfile)
    results = pd.read_excel(outfile, index_col=[0, 1])

    assert list(results.iloc[0]) == [30.78947368421052, 1.878787878787879, 7.478565934105434,
                                     8.200791298261866]
    assert list(results.iloc[50]) == [10.08078279667767, 0.0, 1.056137012369172, 1.670055509910351]
    assert results.index.names == ['Typ gminy', 'Rok urodzenia']
    assert results.shape == (51, 4)
