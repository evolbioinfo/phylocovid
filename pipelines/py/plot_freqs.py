import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from hdx.location.country import Country


def get_iso3(_):
    iso3 = Country.get_iso3_country_code_fuzzy(_)[0]
    return iso3 if iso3 else _


N = 5


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--tab', required=True, type=str)
    parser.add_argument('--png', required=True, type=str)
    params = parser.parse_args()

    stat_df = pd.read_csv(params.tab, sep='\t', index_col=0)
    stat_df = stat_df[stat_df['freq'] >= 0.01]
    stat_df.index = stat_df.index.map(get_iso3)
    df = pd.DataFrame(columns=['ISO3', 'frequency (%)', 'type'])
    for label in stat_df.columns:
        df = df.append(pd.DataFrame.from_dict(
            {'ISO3': stat_df.index, 'frequency (%)': stat_df[label] * 100,
             'type': [label.replace('freq_', '').replace('PD_', 'PD').replace('G_', 'GD') if label != 'freq' else 'declared'] * len(stat_df)}),
            ignore_index=True)

    plt.clf()
    sns.set(font_scale=2)
    fig, ax = plt.subplots(1, 1)
    ax = sns.barplot(x='ISO3', y='frequency (%)', hue='type', data=df, palette='colorblind')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.set_size_inches(15, 10)
    plt.tight_layout()
    # plt.show()
    plt.savefig(params.png, dpi=300)