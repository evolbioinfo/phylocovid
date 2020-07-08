from collections import defaultdict
from datetime import datetime

import numpy as np
import pandas as pd
from pastml import numeric2datetime
from pastml.tree import read_tree


if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--input_tree', required=True, type=str)
    parser.add_argument('--input_locs', required=True, type=str)
    parser.add_argument('--input_stats', required=False, type=str, default=None)
    parser.add_argument('--input_dates', required=True, type=str)
    parser.add_argument('--date', required=True, type=str)
    parser.add_argument('--size', required=True, type=int)
    parser.add_argument('--output_ids', type=str, nargs='+')
    parser.add_argument('--output_stats', required=True, type=str)
    parser.add_argument('--output_stats_per_time', required=True, type=str)
    parser.add_argument('--time_format', required=False, type=str, default='%Y_%m')
    params = parser.parse_args()

    tree = read_tree(params.input_tree)
    ids = {_.name for _ in tree}
    loc_df = pd.read_csv(params.input_locs, index_col=0, sep='\t')
    loc_df.index = loc_df.index.map(str)
    loc_df = loc_df.loc[loc_df.index.isin(ids), :]

    date_df = pd.read_csv(params.input_dates, index_col=0, sep='\t', skiprows=[0], header=None)
    date_df.index = date_df.index.map(str)
    date_df = date_df.loc[date_df.index.isin(ids), :]
    date_df.columns = ['date']
    date_df['date'] = date_df['date'].apply(numeric2datetime)

    loc_df['date'] = date_df.loc[loc_df.index, 'date']
    loc_df['iso3_time'] = loc_df['iso3'] + '_' + loc_df['date'].apply(lambda _: _.strftime(params.time_format))

    to_keep = date_df[date_df['date'] <= datetime(year=2020, month=2, day=1)].index
    kept_count_df = loc_df.loc[to_keep, ['iso3', 'region']].groupby(['iso3']).count()
    kept_count_df.columns = ['count']
    kept_loc_df = loc_df.loc[to_keep, :]

    case_per_time_df = loc_df[['iso3_time', 'region']].groupby(['iso3_time']).count()
    case_per_time_df.columns = ['sampled_cases']

    sampled_case_df = loc_df[['iso3', 'region']].groupby(['iso3']).count()
    sampled_case_df.columns = ['cases']

    if params.input_stats:
        date = datetime.strptime(params.date, '%Y%m%d')
        date_parse = lambda _: datetime.strptime(_, '%d/%m/%Y')
        stat_df = pd.read_csv(params.input_stats, sep=',', parse_dates=['dateRep'], date_parser=date_parse)[['dateRep', 'countryterritoryCode', 'cases']]
        stat_df = stat_df[stat_df['dateRep'] <= date]
        theoretical_case_df = stat_df[['countryterritoryCode', 'cases']].groupby(['countryterritoryCode']).sum()
        theoretical_case_df = theoretical_case_df.loc[theoretical_case_df.index.isin(sampled_case_df.index), :]
        case_df = pd.concat([theoretical_case_df, sampled_case_df]).groupby(level=0).max()
        total_cases = case_df['cases'].sum()
        case_df['frequencies'] = case_df['cases'] / total_cases
        case_df['rescaled_cases'] = np.round(case_df['frequencies'] * params.size, 0).astype(int)
        case_df['sampled_cases'] = sampled_case_df.loc[case_df.index, 'cases']

        case_df['took'] = case_df.index.map(lambda _: len(kept_loc_df[kept_loc_df['iso3'] == _]))
        case_df['extras'] = case_df['sampled_cases'] - case_df['rescaled_cases']
        left = params.size
        # remove the extras that we have to take for other reasons
        left -= np.maximum(0, case_df['took'] - np.minimum(np.maximum(case_df['rescaled_cases'], 5), case_df['sampled_cases'])).sum()

        case_df.sort_values(by=['extras'], inplace=True, ascending=True)
        for i, (iso3, row) in enumerate(case_df.iterrows()):
            avail, took = row['sampled_cases'], row['took']
            like_to_take = max(np.round(left * case_df['cases'].iloc[i] / case_df['cases'].iloc[i:].sum()), 5)
            can_take = min(like_to_take, avail)
            case_df.loc[iso3, 'subsampled_cases'] = max(can_take, took)
            left -= can_take
        case_df.drop(labels=['took', 'extras'], axis=1, inplace=True)
    else:
        case_df = pd.DataFrame(index=sampled_case_df.index)
        left = params.size
        n = len(case_df)
        avg_to_take = left / n
        print('Aiming to take {} samples per country.'.format(avg_to_take))
        case_df['frequencies'] = 1 / n
        case_df['rescaled_cases'] = np.round(avg_to_take, 0).astype(int)
        case_df['sampled_cases'] = sampled_case_df.loc[case_df.index, 'cases']

        case_df['took'] = case_df.index.map(lambda _: len(kept_loc_df[kept_loc_df['iso3'] == _]))
        # remove the extras that we have to take for other reasons
        left -= np.maximum(0, case_df['took'] - avg_to_take).sum()

        case_df.sort_values(by=['sampled_cases'], inplace=True, ascending=True)

        for i, (iso3, row) in enumerate(case_df.iterrows()):
            avail, took = row['sampled_cases'], row['took']
            like_to_take = np.round(left / (n - i), 0)
            can_take = min(like_to_take, avail)
            case_df.loc[iso3, 'subsampled_cases'] = max(can_take, took)
            left -= can_take
        case_df.drop(labels=['took'], axis=1, inplace=True)

    case_df.sort_values(by=['subsampled_cases'], inplace=True, ascending=True)
    case_df.to_csv(params.output_stats, sep='\t', index_label='iso3')

    for iso3 in case_df.index:
        left = int(case_df.loc[iso3, 'subsampled_cases'])
        iso3_loc_df = loc_df[loc_df['iso3'] == iso3]
        sc_df = iso3_loc_df[['iso3_time', 'region']].groupby(['iso3_time']).count()
        sc_df.columns = ['cases']
        sc_df.sort_values(by=['cases'], inplace=True, ascending=True)
        n = len(sc_df)
        avg_to_take = left / n
        sc_df['took'] = sc_df.index.map(lambda _: len(kept_loc_df[kept_loc_df['iso3_time'] == _]))

        # remove the extras that we have to take for other reasons
        left -= np.maximum(0, sc_df['took'] - avg_to_take).sum()

        for i, (iso3_time, row) in enumerate(sc_df.iterrows()):
            avail, took = row['cases'], row['took']
            like_to_take = int(left / (n - i))
            can_take = min(like_to_take, avail)
            case_per_time_df.loc[iso3_time, 'subsampled_cases'] = max(can_take, took)
            case_per_time_df.loc[iso3_time, 'iso3'] = iso3
            left -= can_take

        print(iso3, case_df.loc[iso3, 'subsampled_cases'], case_per_time_df[case_per_time_df['iso3'] == iso3])
    case_per_time_df.to_csv(params.output_stats_per_time, sep='\t', index_label='iso3_{}'.format(params.time_format))

    for output_ids in params.output_ids:
        tree = read_tree(params.input_tree)
        case_per_time_df['remove_cases'] = case_per_time_df['sampled_cases'] - case_per_time_df['subsampled_cases']
        bin2tips = defaultdict(list)
        for _ in tree:
            if _.name not in to_keep and case_per_time_df.loc[loc_df.loc[_.name, 'iso3_time'], 'remove_cases']:
                bin2tips[_.dist].append(_)
        while case_per_time_df['remove_cases'].sum():
            min_bin = min(bin2tips.keys())
            min_tips = bin2tips[min_bin]
            tip = np.random.choice(min_tips, 1)[0]
            min_tips.remove(tip)
            if not min_tips:
                del bin2tips[min_bin]
            if case_per_time_df.loc[loc_df.loc[tip.name, 'iso3_time'], 'remove_cases'] > 0:
                case_per_time_df.loc[loc_df.loc[tip.name, 'iso3_time'], 'remove_cases'] -= 1
                parent = tip.up
                parent.remove_child(tip)
                if len(parent.children) == 1 and not parent.is_root():
                    grandparent = parent.up
                    child = parent.remove_child(parent.children[0])
                    if child.is_leaf() and child.dist in bin2tips and child in bin2tips[child.dist]:
                        bin2tips[child.dist].remove(child)
                        if not bin2tips[child.dist]:
                            del bin2tips[child.dist]
                        bin2tips[parent.dist + child.dist].append(child)
                    grandparent.add_child(child, dist=parent.dist + child.dist)
                    grandparent.remove_child(parent)

        while len(tree.children) == 1:
            tree = tree.children[0]
            tree.dist = 0
            tree.up = None

        with open(output_ids, 'w+') as f:
            f.write('\n'.join(_.name for _ in tree))

