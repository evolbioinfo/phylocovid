import logging

import pandas as pd
import numpy as np
from ete3 import Tree

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--tree', required=True, type=str)
    parser.add_argument('--dates', required=True, type=str, default=None)
    parser.add_argument('--ids', required=True, type=str, default=None)
    parser.add_argument('--log', required=True, type=str, default=None)
    parser.add_argument('--threshold', required=False, type=int, default=3)
    params = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(asctime)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S",
                        filename=params.log)

    tree = Tree(params.tree)
    df = pd.read_csv(params.dates, skiprows=[0], header=None, sep='\t', index_col=0)
    df.columns = ['time']
    df.index = df.index.map(str)
    df = df.loc[[_.name for _ in tree], :]
    df['time'] = df['time'].astype(float)
    outliers = []
    for n in tree.traverse('preorder'):
        n.add_feature('dtr', n.dist + (getattr(n.up, 'dtr') if not n.is_root() else 0))
        if n.is_root():
            for c, side in zip(n.children, ('left', 'right')):
                c.add_feature('side', side)
        else:
            side = getattr(n, 'side')
            for c in n.children:
                c.add_feature('side', side)
        if n.is_leaf():
            df.loc[n.name, 'dtr'] = getattr(n, 'dtr')
            df.loc[n.name, 'side'] = getattr(n, 'side')

    def get_slope(df, name, two_sides=False):
        dtr = df.loc[name, 'dtr']
        time = df.loc[name, 'time']
        others = (df.index != name) & (df['time'] != time)
        if two_sides:
            side = df.loc[name, 'side']
            others &= df['side'] != side
        return np.median((dtr - df.loc[others, 'dtr']) / (time - df.loc[others, 'time']))

    slope = df.index.map(lambda _: get_slope(df, _))
    logging.info('Slope before outlier removal: median={:g}, std={:g}.'.format(np.median(slope), np.std(slope)))
    slope = df.index.map(lambda _: get_slope(df, _, True))
    logging.info('Two side slope before outlier removal: median={:g}, std={:g}.'.format(np.median(slope), np.std(slope)))
    side = 'left' if len(df[df['side'] == 'left']) > len(df) / 2 else 'right'
    side_df = df[df['side'] == side]
    side_slope = side_df.index.map(lambda _: get_slope(side_df, _))
    logging.info('Side slope before outlier removal: median={:g}, std={:g}.'.format(np.median(side_slope), np.std(side_slope)))

    root_dtr = min(df['dtr'])
    root_time = min(df.loc[df['dtr'] == root_dtr, 'time'])
    df = df.loc[df['time'] > 0, :]
    has_rate = df['time'] > root_time
    df['rate'] = np.where(has_rate, (df['dtr'] - root_dtr) / (df['time'] - root_time), np.nan)
    median_rate = np.median(df.loc[has_rate, 'rate'])
    rate_std = df.loc[has_rate, 'rate'].std()
    logging.info('Rate before outlier removal: median={:g}, std={:g}.'.format(median_rate, rate_std))
    df['z'] = (df['rate'] - median_rate) / rate_std
    is_outlier = df['z'] > params.threshold
    print(df.loc[is_outlier, 'z'].head(n=sum(is_outlier)))
    logging.info(df.loc[is_outlier, 'z'].head(n=sum(is_outlier)))
    with open(params.ids, 'w+') as f:
        f.write('\n'.join(df.loc[is_outlier, :].index))
    df = df[~is_outlier]
    has_rate = df['time'] > root_time
    logging.info('Rate after outlier removal: median={:g}, std={:g}.'.format(np.median(df.loc[has_rate, 'rate']), df.loc[has_rate, 'rate'].std()))
    slope = df.index.map(lambda _: get_slope(df, _))
    logging.info('Slope after outlier removal: median={:g}, std={:g}.'.format(np.median(slope), np.std(slope)))
    slope = df.index.map(lambda _: get_slope(df, _, True))
    logging.info(
        'Two side slope after outlier removal: median={:g}, std={:g}.'.format(np.median(slope), np.std(slope)))
    side = 'left' if len(df[df['side'] == 'left']) > len(df) / 2 else 'right'
    side_df = df[df['side'] == side]
    side_slope = side_df.index.map(lambda _: get_slope(side_df, _))
    logging.info(
        'Side slope after outlier removal: median={:g}, std={:g}.'.format(np.median(side_slope), np.std(side_slope)))
