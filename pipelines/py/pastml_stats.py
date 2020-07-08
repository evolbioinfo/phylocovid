import pandas as pd

if '__main__' == __name__:
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument('--freqs', required=True, type=str)
    parser.add_argument('--pastml_freqs', nargs='+', type=str)
    parser.add_argument('--labels', nargs='+', type=str)
    parser.add_argument('--output_stats', required=True, type=str)
    parser.add_argument('--col', required=False, type=str, default='country')
    params = parser.parse_args()

    df = pd.read_csv(params.freqs, index_col=0, sep='\t')
    df.columns = ['freq']

    for label, tab in zip(params.labels, params.pastml_freqs):
        pdf = pd.read_csv(tab, index_col=0, sep='\t')
        df['freq_{}'.format(label)] = pdf.loc[df.index, 'value']

    df.to_csv(params.output_stats, sep='\t', index_label=params.col)
