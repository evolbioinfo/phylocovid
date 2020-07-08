from datetime import datetime

import pandas as pd
import numpy as np
from pastml.tree import read_tree

ISO3 = 'iso3'


def calc_percentage(df, column):
    df[column.replace('cases', 'percentage')] = np.round(100 * df[column] / df[column].sum(), 2)


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--input_locs', required=True, type=str)
    parser.add_argument('--input_stats', required=True, type=str, default=None)
    parser.add_argument('--date', required=True, type=str)
    parser.add_argument('--ids_phylogenetic', required=True, type=str)
    parser.add_argument('--ids_genomic', required=True, type=str)
    parser.add_argument('--output_stats', required=True, type=str)
    params = parser.parse_args()

    tree = read_tree(params.input_tree)
    ids = {_.name for _ in tree}
    loc_df = pd.read_csv(params.input_locs, index_col=0, sep='\t')
    loc_df.index = loc_df.index.map(str)
    loc_df = loc_df.loc[loc_df.index.isin(ids), :]

    sampled_case_df = loc_df[[ISO3, 'region']].groupby([ISO3]).count()
    sampled_case_df.columns = ['cases']

    date = datetime.strptime(params.date, '%Y%m%d')
    date_parse = lambda _: datetime.strptime(_, '%d/%m/%Y')
    stat_df = pd.read_csv(params.input_stats, sep=',', parse_dates=['dateRep'], date_parser=date_parse)\
        [['dateRep', 'countryterritoryCode', 'cases']]
    stat_df = stat_df[stat_df['dateRep'] <= date]
    theoretical_case_df = stat_df[['countryterritoryCode', 'cases']].groupby(['countryterritoryCode']).sum()
    theoretical_case_df = theoretical_case_df.loc[theoretical_case_df.index.isin(sampled_case_df.index), :]
    case_df = pd.concat([theoretical_case_df, sampled_case_df]).groupby(level=0).max()
    case_df.columns = [(c if c != 'cases' else 'declared_cases') for c in case_df.columns]
    calc_percentage(case_df, 'declared_cases')
    case_df['sampled_cases'] = sampled_case_df.loc[case_df.index, 'cases']
    calc_percentage(case_df, 'sampled_cases')

    with open(params.ids_phylogenetic, 'r') as f:
        ids = f.read().strip().strip('\n').split('\n')
    phy_case_df = loc_df.loc[ids, [ISO3, 'region']].groupby([ISO3]).count()
    phy_case_df.columns = ['phylogenetic_diversity_cases']
    calc_percentage(phy_case_df, 'phylogenetic_diversity_cases')
    case_df = case_df.join(phy_case_df, how='outer')

    with open(params.ids_genomic, 'r') as f:
        ids = f.read().strip().strip('\n').split('\n')
    gen_case_df = loc_df.loc[ids, [ISO3, 'region']].groupby([ISO3]).count()
    gen_case_df.columns = ['genetic_diversity_cases']
    calc_percentage(gen_case_df, 'genetic_diversity_cases')
    case_df = case_df.join(gen_case_df, how='outer')
    case_df.to_csv(params.output_stats, sep='\t', index_label='ISO3')
