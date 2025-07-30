import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

from collections import defaultdict
from itertools import chain

from badlon.data.process import filter_dataframe_core


def coverage(cov_df, output_file, log=False):
    sns.set_theme(style="whitegrid", font_scale=1.3)
    plt.figure()

    cov_df.rename(columns={'chr/contig': 'chromosome'}, inplace=True)
    sns.histplot(cov_df,
                 x='coverage',
                 hue='chromosome' if 'chromosome' in cov_df.columns else None,
                 bins=50,
                 log_scale=(False, log),
                 element="step")

    plt.ylabel('Number of genomes')
    plt.xlabel('Coverage')
    plt.tight_layout()
    plt.savefig(output_file)


def coverages_match_chart(blocks_df, genes_df, genome_lengths, folder, contig_mode_flag, filter_singletons=False):
    def construct_locus_labels(df, c_start, c_end, label):
        return [(p, 's', label) for p in df[c_start]], [(p, 'e', label) for p in df[c_end]]

    type_coverages_2d = []
    type_coverages_flat = []

    if filter_singletons:
        genes_df = genes_df[genes_df.og != ''].copy()

    for core in [False, True]:
        if core:
            genes_df = filter_dataframe_core(genes_df, count='genome', groupby='og')
            blocks_df = filter_dataframe_core(blocks_df, count='genome', groupby='block')

        for strain, genes_strain_df in genes_df.groupby('genome'):
            for chr, genes_strain_chr_df in genes_strain_df.groupby('chr/contig'):
                blocks_strain_df = blocks_df[(blocks_df['genome'] == strain) & (blocks_df['chr/contig'] == str(chr))] \
                    .sort_values(by=['start'])
                genes_strain_chr_df = genes_strain_chr_df.sort_values('start')

                ls1, le1 = construct_locus_labels(blocks_strain_df, 'start', 'end', 'block')
                ls2, le2 = construct_locus_labels(genes_strain_chr_df, 'start', 'end', 'gene')

                covered = defaultdict(int)
                events = list(sorted(chain(ls1, le1, ls2, le2)))

                prev = 0
                state = {'block': 0, 'gene': 0}

                for cur_pos, event, type in events:
                    cov_str = ', '.join(t for t, c in state.items() if c > 0)
                    covered[cov_str] += cur_pos - prev

                    if event == 's':
                        state[type] += 1
                    elif event == 'e':
                        state[type] -= 1
                    prev = cur_pos

                try:
                    chr_len = genome_lengths[(strain, str(chr))]
                except KeyError:
                    # print(f"WARNING Length of {strain}.{chr} is missed in block_coords file, skipping it.")
                    continue

                type_coverages_flat.append([covered[t] / chr_len * 100 for t in sorted(covered.keys()) if t != ''])
                for t, c in covered.items():
                    if t == '': continue
                    type_coverages_2d.append([strain, 'core' if core else 'all', chr, t, c / chr_len * 100])

    cov_df = pd.DataFrame(type_coverages_2d, columns=['genome', 'core', 'chr/contig', 'type', 'covered'])
    sns.set_theme(style="whitegrid", font_scale=1.3)
    plt.figure()

    cov_df['chr,core'] = cov_df['chr/contig'].astype('str') + ',' + cov_df['core']

    sns.barplot(x="chr,core", y="covered", hue="type", data=cov_df, hue_order=['gene', 'block', 'block, gene'], palette="Set1")

    plt.xlabel('Chromosome, core/all')
    plt.ylabel('Fraction of genome covered')
    plt.legend(loc='best')

    plt.tight_layout()
    plt.savefig(folder + f'coverages_perc_barplot.pdf')

    return cov_df