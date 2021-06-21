"""
Tests for functions used in per_teacher_analysis.
"""

import math
import os
import pandas as pd
import src.schools_pkg.parsing as sc_parsing
from src.schools_pkg.save import save_gmina_statistics
from src.schools_pkg.save import save_gminatype_statistics


def test_load_schools(schools_loaded):
    assert schools_loaded.loc[1, 'Oddziały'] == 5
    assert schools_loaded.loc[100, 'Miejscowość'] == 'Jawor'
    assert schools_loaded.loc[1000, 'w tym w oddziałach przedszk.'] == 0
    assert schools_loaded['Uczniowie, wychow., słuchacze'].sum() == 6388792


def test_drop_duplicate(schools_loaded):
    schools = sc_parsing.drop_duplicate_regon(schools_loaded)
    assert len(schools_loaded) - len(schools) == schools_loaded.duplicated(['Regon']).sum()


def test_regon_as_index(schools_regonized, schools_loaded):
    assert len(schools_loaded.columns) - len(schools_regonized.columns) == 1
    assert schools_regonized.index.name == 'Regon'


def test_drop_delegatures(schools_no_delegatures, schools_regonized):
    assert len(schools_regonized) - \
           len(schools_no_delegatures) == len(
        schools_regonized[schools_regonized['Złożoność'] == 4])
    assert len(schools_no_delegatures[schools_no_delegatures['Złożoność'] == 4]) == 0


def test_sum_teachers(schools_sum_teachers, schools_no_delegatures):
    teacher_cols = ['Nauczyciele pełnozatrudnieni', 'Nauczyciele niepełnozatrudnieni (w etatach)']
    assert schools_sum_teachers.columns.any() not in teacher_cols
    assert schools_sum_teachers.loc[:, 'Nauczyciele'].sum(
    ) == schools_no_delegatures.loc[:, teacher_cols].sum().sum()


def test_reallocate_per_regon(schools_reallocated, schools_no_delegatures):
    teacher_cols = ['Nauczyciele pełnozatrudnieni', 'Nauczyciele niepełnozatrudnieni (w etatach)']
    assert schools_reallocated['Nauczyciele'].sum(
    ) == schools_no_delegatures.loc[:, teacher_cols].sum().sum()


def test_per_teacher(schools_per_teacher):
    i = 34160040500000
    assert schools_per_teacher.loc[i, 'Uczniów na etat nauczycielski'] == \
           schools_per_teacher.loc[i, 'Uczniowie, wychow., słuchacze'] / \
           schools_per_teacher.loc[i, 'Nauczyciele']

    i_no_teachers = 36263228300000
    assert math.isnan(schools_per_teacher.loc[i_no_teachers, 'Uczniów na etat nauczycielski'])


def test_gmina_statistics(schools_reallocated, tmp_path):
    # Redo the operation to avoid potential view/copy/in-place operations mess
    schools_per_teacher = schools_reallocated.loc[schools_reallocated[
                                                      'Uczniowie, wychow., słuchacze'] > 0]
    sc_parsing.students_per_teachers_in_school(schools_per_teacher)

    outfile = os.path.join(tmp_path, 'gmina_per_teacher.xlsx')
    save_gmina_statistics(schools_per_teacher, outfile)

    results_gmina = pd.read_excel(outfile, index_col=list(range(8)))
    assert results_gmina.index.names == ['woj', 'pow', 'gm', 'Województwo', 'Powiat', 'Gmina',
                                         'Typ gminy', 'Nazwa typu']
    assert results_gmina.shape == (10144, 4)
    assert (results_gmina.iloc[0] == [15.7002891101831, 7.121862988921546,
                                      11.78861788617886, 11.50520465810591]).all()


def test_gminatype_statistics(schools_reallocated, tmp_path):
    # Redo the operation to avoid potential view/copy/in-place operations mess
    schools_per_teacher = schools_reallocated.loc[schools_reallocated[
                                                      'Uczniowie, wychow., słuchacze'] > 0]
    sc_parsing.students_per_teachers_in_school(schools_per_teacher)

    outfile = os.path.join(tmp_path, 'gminatype_per_teacher.xlsx')
    save_gminatype_statistics(schools_per_teacher, outfile)

    results_gminatype = pd.read_excel(outfile, index_col=list(range(2)))
    assert results_gminatype.index.names == ['Typ gminy', 'Nazwa typu']
    assert results_gminatype.shape == (66, 4)
    assert (results_gminatype.iloc[0] == [39.87975951903807, 0.3630862329803329,
                                          5.936502603729213, 6.265061786032909]).all()
