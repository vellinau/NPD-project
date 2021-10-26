"""
Main program. Run to get the results.
"""

import argparse
from src import per_teacher_analysis, per_age_analysis


parser = argparse.ArgumentParser(description='')
parser.add_argument('schools_path', nargs='?', type=str, help='path to .xlsx file with schools data',
                    default='data\\Wykaz_szkół_i_placówek_wg_stanu_na_30.IX._2018_w.5.xlsx')
parser.add_argument('population_path', nargs='?', type=str, help='path to directory with population data',
                    default='data\\Ludność. Stan i struktura_30.06.2020')
parser.add_argument('outpath_gmina', nargs='?', type=str, help='where to save results of per teacher '
                                                    'analysis, for each gmina',
                    default='results\\gmina_per_teacher.xlsx')
parser.add_argument('outpath_gminatype', nargs='?', type=str, help='where to save results of per teacher '
                                                        'analysis, in total',
                    default='results\\gminatype_per_teacher.xlsx')
parser.add_argument('outpath_per_age', nargs='?', type=str, help='where to save results of per age '
                                                      'analysis, in total',
                    default='results\\gminatype_per_age.xlsx')
args = parser.parse_args()


schools, dropped_1 = per_teacher_analysis.run(args.schools_path, args.outpath_gmina,
                                              args.outpath_gminatype)
dropped_2 = per_age_analysis.run(schools, args.population_path, args.outpath_per_age)
dropped_percentage = (dropped_1 + dropped_2) / (schools["Uczniowie, wychow., słuchacze"].sum()
                                                + dropped_1) * 100

print(f'{round(dropped_percentage, 2)}% of information about students dropped during all '
      f'calculations.')
