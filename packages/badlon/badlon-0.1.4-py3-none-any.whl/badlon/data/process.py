def block_genome_count(df):
    chrs_f = lambda x: ','.join(list(sorted(set(x))))
    return df.groupby('block').agg(mean_length=('length', 'mean'),
                                   genomes=('genome', 'nunique'),
                                   chroms=('chr/contig', chrs_f))


def filter_dataframe_core(df, groupby='block', count='genome'):
    all_sp = len(df[count].unique())

    allowed_blocks = set(block
                         for block, df_block in df.groupby(groupby)
                         if len(df_block[count].unique()) == all_sp)
    
    print(f'Unique single-copy {groupby}: {len(allowed_blocks)}, unique_genomes={all_sp}')
    return df.loc[df[groupby].isin(allowed_blocks)].copy()


def distance_between_blocks_distribution(df_blocks, groupby='genome', start='start', end='end'):
    ds = []
    for sp, df_sp in df_blocks.groupby(groupby):
        df_sp = df_sp.sort_values(by=[start])
        ds += (start_ - end_ for start_, end_ in zip(df_sp[start][1:], df_sp[end]))
    return ds


