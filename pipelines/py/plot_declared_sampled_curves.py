import argparse
from datetime import datetime

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('--metadata', required=True, type=str)
    parser.add_argument('--cases', required=True, type=str)
    parser.add_argument('--png', required=True, type=str)
    parser.add_argument('--date', required=True, type=str)
    params = parser.parse_args()

    countries = ['USA', 'ITA', 'CHN', 'BRA']

    sampled_case_df = pd.read_csv(params.metadata, sep='\t', index_col=0)

    total_cases = len(sampled_case_df)
    sampled_case_count_df = sampled_case_df.loc[:, ['iso3', 'region']].groupby(['iso3']).count()
    sampled_case_count_df.columns = ['cases']
    sampled_case_count_df.sort_values(by=['cases'], inplace=True)
    sampled_df = sampled_case_df[['iso3', 'sampling date d/m/Y', 'region']] \
        .groupby(['iso3', 'sampling date d/m/Y']).count()
    sampled_df.columns = ['cases']
    sampled_df['date'] = sampled_df.index.map(lambda _: _[1])
    sampled_df['date'] = sampled_df['date'].apply(lambda _: datetime.strptime(_, '%d/%m/%Y'))
    sampled_df['iso3'] = sampled_df.index.map(lambda _: _[0])

    date = datetime.strptime(params.date, '%Y%m%d')
    date_parse = lambda _: datetime.strptime(_, '%d/%m/%Y')
    declared_df = pd.read_csv(params.cases, sep=',', parse_dates=['dateRep'], date_parser=date_parse)[
        ['dateRep', 'countryterritoryCode', 'cases']]
    declared_df = declared_df.loc[declared_df['dateRep'] <= date, ['dateRep', 'countryterritoryCode', 'cases']]
    declared_df.columns = ['date', 'iso3', 'cases']
    declared_df = pd.concat([declared_df, sampled_df]).groupby(by=['iso3', 'date']).max()
    declared_df['iso3'] = declared_df.index.map(lambda _: _[0])
    declared_df['date'] = declared_df.index.map(lambda _: _[1])
    declared_df.index = range(len(declared_df))
    total_decrared_cases = declared_df['cases'].sum()

    dates = set(sampled_df['date'].unique()) | set(declared_df['date'].unique())
    sorted_dates = sorted(dates)

    def fix_dates(df):
        for c in df['iso3'].unique():
            c_dates = set(df.loc[df['iso3'] == c, 'date'].unique())
            missing_dates = [[c, d, 0] for d, dd in zip(sorted(dates - c_dates), sorted_dates) if d != dd]
            if missing_dates:
                extra_dates = pd.DataFrame(missing_dates, columns=['iso3', 'date', 'cases'])
                df = df.append(extra_dates, ignore_index=True)
        total = [['total', d, sum(df.loc[df['date'] == d, 'cases'])] for d in sorted_dates]
        extra_dates = pd.DataFrame(total, columns=['iso3', 'date', 'cases'])
        df = df.append(extra_dates, ignore_index=True)
        return df


    sampled_df = fix_dates(sampled_df)
    declared_df = fix_dates(declared_df)

    def accumulate_cases(df):
        df.sort_values(by=['iso3', 'date'], inplace=True)
        df.index = range(len(df))
        for iso3 in df['iso3'].unique():
            iso_df = df[df['iso3'] == iso3]
            prev = 0
            for i in iso_df.index:
                df.loc[i, 'cases'] += prev
                prev = df.loc[i, 'cases']

    accumulate_cases(sampled_df)
    accumulate_cases(declared_df)

    declared_df['percentage'] = declared_df.apply(
        lambda row: 100 * row['cases'] / declared_df.loc[declared_df['date'] == row['date'], 'cases'].sum(), axis=1)
    sampled_df['percentage'] = sampled_df.apply(
        lambda row: 100 * row['cases'] / sampled_df.loc[sampled_df['date'] == row['date'], 'cases'].sum(), axis=1)

    declared_df = declared_df.loc[declared_df['iso3'].isin(countries + ['total']), :]
    sampled_df = sampled_df.loc[sampled_df['iso3'].isin(countries + ['total']), :]

    plt.clf()
    sns.set(font_scale=1.5)
    fig, (ax2, ax1) = plt.subplots(2, 1)
    sns.lineplot(x='date', y='cases', hue='iso3', data=sampled_df, palette='colorblind',
                ax=ax1, style='iso3', markers=True)
    ax1.set(ylabel='number of sampled cases')
    sns.lineplot(x='date', y='cases', hue='iso3', data=declared_df, palette='colorblind',
                ax=ax2, style='iso3', markers=True)
    ax2.set(ylabel='number of declared cases')
    for ax in (ax1, ax2):
        ax.spines['right'].set_visible(False)
        ax.spines['top'].set_visible(False)
        ax.set(yscale="log")
        for tick in ax.xaxis.get_major_ticks():
            tick.label.set_fontsize(12)
    fig.set_size_inches(15, 10)
    plt.tight_layout()
    # plt.show()
    plt.savefig(params.png, dpi=300)
