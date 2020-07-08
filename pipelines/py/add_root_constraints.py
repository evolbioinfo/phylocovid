import pandas as pd
import numpy as np
from ete3 import Tree

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--tree', required=True, type=str)
    parser.add_argument('--in_dates', required=True, type=str, default=None)
    parser.add_argument('--out_dates', required=True, type=str, default=None)
    parser.add_argument('--constraint', required=True, type=str, default=None)
    params = parser.parse_args()

    tree = Tree(params.tree, format=3)
    df = pd.read_csv(params.in_dates, skiprows=[0], header=None, sep='\t', index_col=0)
    df.columns = ['date']
    df.index = df.index.map(str)
    n = max(tree.children, key=lambda _: len(list(_.iter_leaves())))
    if n.dist == 0:
        df.loc[n.name, 'date'] = params.constraint
    with open(params.out_dates, 'w+') as f:
        f.write('{}\n'.format(len(df)))
    df.to_csv(params.out_dates, header=False, mode='a', sep='\t')
