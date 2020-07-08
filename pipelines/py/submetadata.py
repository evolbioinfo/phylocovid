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
    parser.add_argument('--output_tab', required=False, type=str, default=None)
    parser.add_argument('--input_dates', required=True, type=str)
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

    loc_df['sampling date numeric'] = date_df.loc[loc_df.index, 'date']
    loc_df['sampling date d/m/Y'] = loc_df['sampling date numeric'].apply(lambda _ : numeric2datetime(_).strftime('%d/%m/%Y'))

    loc_df[['sampling date numeric', 'sampling date d/m/Y', 'iso2', 'iso3', 'country', 'intregion', 'region']].to_csv(params.output_tab, sep='\t', index_label='id')

