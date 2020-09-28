import argparse

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--tab', required=True, type=str)
    parser.add_argument('--png', required=True, type=str)
    params = parser.parse_args()

    stat_df = pd.read_csv(params.tab, sep='\t', index_col=0)
    stat_df.columns = ['declared_cases', 'frequencies', 'rescaled', 'sampled_cases', 'phylogenetic_diversity_cases']
    stat_df['declared_percentage'] = (stat_df['declared_cases'] / stat_df['declared_cases'].sum()) * 100
    stat_df = stat_df[stat_df['declared_percentage'] >= 1]
    df = pd.DataFrame(columns=['ISO3', 'cases', 'percentage', 'type'])
    for label in ('declared', 'sampled', 'phylogenetic diversity'):
        label = '{}_cases'.format(label.replace(' ', '_'))
        df = df.append(pd.DataFrame.from_dict({'ISO3': stat_df.index,
                                               'cases': stat_df[label],
                                               'percentage': (stat_df[label] / stat_df[label].sum() * 100),
                                               'type': [label] * len(stat_df)}), ignore_index=True)

    plt.clf()
    sns.set(font_scale=2)
    fig, ax = plt.subplots(1, 1)
    ax = sns.barplot(x='ISO3', y='percentage', hue='type', data=df, palette='colorblind')
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    fig.set_size_inches(15, 10)
    plt.tight_layout()
    # plt.show()
    plt.savefig(params.png, dpi=300)