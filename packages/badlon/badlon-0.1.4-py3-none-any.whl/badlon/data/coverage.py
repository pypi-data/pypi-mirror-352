import pandas as pd


def calculculate_covered(df_blocks, df_lens, collapse_contigs):
    df_cov = df_blocks.groupby(['genome', 'chr/contig'])['length'].sum().reset_index()
    df_cov.rename(columns={'length': 'covered'}, inplace=True)

    df = pd.merge(df_cov, df_lens, on=['genome', 'chr/contig'])

    if collapse_contigs:
        df = df.groupby(['genome']).sum().reset_index()

    df['coverage'] = df['covered'] / df['size']
    return df
