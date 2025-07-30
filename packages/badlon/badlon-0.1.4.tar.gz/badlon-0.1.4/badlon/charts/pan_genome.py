import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

from collections import Counter


def pan_blocks(df, contig_mode_flag, output_folder, permutations=420):
    def append_pan_2d_row_based_on_blocks_df(cur_df, chr=0):
        block_sets = [set(df_sp.block.unique()) for _, df_sp in cur_df.groupby('genome')]
        for _ in range(permutations):
            block_sets = np.random.permutation(block_sets)
            accumulate_set = set()
            accumulate_set_intersect = set(cur_df.block.unique())
            for i, bs in enumerate(block_sets):
                left = bs - accumulate_set
                accumulate_set |= bs
                accumulate_set_intersect &= bs

                pan_2d.append([chr, i + 1, len(left), len(accumulate_set), len(accumulate_set_intersect)])

    pan_2d = []
    if contig_mode_flag:
        append_pan_2d_row_based_on_blocks_df(df)
    else:
        for chr, df_chr in df.groupby('chr/contig'):
            append_pan_2d_row_based_on_blocks_df(df_chr, chr)

    pan_df = pd.DataFrame(pan_2d, columns=['chromosome', 'genomes', 'new blocks', 'pan blocks', 'core blocks'])

    def draw(column):
        sns.set_theme(style="whitegrid", font_scale=1.5)
        plt.figure()
        sns.lineplot(data=pan_df,
                     x='genomes',
                     y=column,
                     hue="chromosome" if not contig_mode_flag else None,
                     ci='sd')
        plt.tight_layout()
        plt.ylabel(column[0].upper() + column[1:])
        plt.xlabel('Number of genomes')
        plt.savefig(output_folder + column.replace(' ', '_') + '.pdf')

    draw(column='new blocks')
    draw(column='pan blocks')
    draw(column='core blocks')


def pan_blocks_length(df, contig_mode_flag, output_folder, permutations=420):
    def get_genome_length(cnt):
        return sum(c * block_to_len[b] for b, c in cnt.items())

    def append_pan_2d_row_based_on_blocks_df(cur_df, chr=0):
        block_cnts = [Counter(df_sp.block.values) for _, df_sp in cur_df.groupby('genome')]

        for _ in range(permutations):
            block_cnts = np.random.permutation(block_cnts)
            accumulate_cnt = Counter()
            max_occ = cur_df.groupby(['block', 'genome']).size().groupby(level='block').max()
            accumulate_cnt_intersect = Counter({i: v for i, v in max_occ.items()})

            for i, bs in enumerate(block_cnts):
                left = bs - accumulate_cnt
                accumulate_cnt |= bs
                accumulate_cnt_intersect &= bs

                pan_2d.append([chr, i + 1,
                               get_genome_length(left),
                               get_genome_length(accumulate_cnt),
                               get_genome_length(accumulate_cnt_intersect)])

    block_to_len = {b: df_b.length.mean() for b, df_b in df.groupby('block')}

    pan_2d = []
    if contig_mode_flag:
        append_pan_2d_row_based_on_blocks_df(df)
    else:
        for chr, df_chr in df.groupby('chr/contig'):
            append_pan_2d_row_based_on_blocks_df(df_chr, chr)

    pan_df = pd.DataFrame(pan_2d, columns=['chromosome', 'genomes',
                                           'new blocks length', 'pan blocks length', 'core blocks length'])

    def draw(column):
        sns.set_theme(style="whitegrid", font_scale=1.3)
        plt.figure()
        sns.lineplot(data=pan_df,
                     x='genomes',
                     y=column,
                     hue="chromosome" if not contig_mode_flag else None,
                     ci='sd')
        plt.ylabel(column[0].upper() + column[1:])
        plt.xlabel('Number of genomes')
        plt.tight_layout()
        plt.savefig(output_folder + column.replace(' ', '_') + '_length.pdf')

    draw(column='new blocks length')
    draw(column='pan blocks length')
    draw(column='core blocks length')