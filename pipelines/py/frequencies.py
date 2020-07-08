from datetime import datetime

import pandas as pd
from pastml.tree import read_tree

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--input_locs', required=True, type=str)
    parser.add_argument('--input_stats', required=True, type=str, default=None)
    parser.add_argument('--date', required=True, type=str)
    parser.add_argument('--output_frequencies_country', required=True, type=str)
    parser.add_argument('--output_frequencies_intregion', required=True, type=str)
    parser.add_argument('--output_frequencies_region', required=True, type=str)
    params = parser.parse_args()

    tree = read_tree(params.input_tree)
    ids = {_.name for _ in tree}
    loc_df = pd.read_csv(params.input_locs, index_col=0, sep='\t')
    loc_df.index = loc_df.index.map(str)
    loc_df = loc_df.loc[loc_df.index.isin(ids), :]

    sampled_case_df = loc_df[['iso3', 'region']].groupby(['iso3']).count()
    sampled_case_df.columns = ['cases']

    date = datetime.strptime(params.date, '%Y%m%d')
    date_parse = lambda _: datetime.strptime(_, '%d/%m/%Y')
    stat_df = pd.read_csv(params.input_stats, sep=',', parse_dates=['dateRep'], date_parser=date_parse)[['dateRep', 'countryterritoryCode', 'cases']]
    stat_df = stat_df[stat_df['dateRep'] <= date]
    theoretical_case_df = stat_df[['countryterritoryCode', 'cases']].groupby(['countryterritoryCode']).sum()
    theoretical_case_df = theoretical_case_df.loc[theoretical_case_df.index.isin(sampled_case_df.index), :]
    case_df = pd.concat([theoretical_case_df, sampled_case_df]).groupby(level=0).max()
    total_cases = case_df['cases'].sum()
    case_df['frequencies'] = case_df['cases'] / total_cases

    # Save frequencies for PastML
    has_country = ~pd.isna(loc_df['iso3']) & ~pd.isna(loc_df['country']) & ~pd.isna(loc_df['region']) & ~pd.isna(loc_df['intregion'])
    iso32country = dict(zip(loc_df.loc[has_country, 'iso3'], loc_df.loc[has_country, 'country']))
    iso32region = dict(zip(loc_df.loc[has_country, 'iso3'], loc_df.loc[has_country, 'region']))
    iso32intregion = dict(zip(loc_df.loc[has_country, 'iso3'], loc_df.loc[has_country, 'intregion']))

    case_df = case_df[['frequencies']]
    case_df.columns = ['value']
    case_df['parameter'] = case_df.index.map(lambda _: iso32country[str(_)])
    case_df[['parameter', 'value']].to_csv(params.output_frequencies_country, sep='\t', index=False)
    case_df['parameter'] = case_df.index.map(lambda _: iso32intregion[str(_)])
    case_df[['parameter', 'value']].groupby(['parameter']).sum().to_csv(params.output_frequencies_intregion, sep='\t', index_label='parameter')
    case_df['parameter'] = case_df.index.map(lambda _: iso32region[str(_)])
    case_df[['parameter', 'value']].groupby(['parameter']).sum().to_csv(params.output_frequencies_region, sep='\t', index_label='parameter')
