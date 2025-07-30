import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from badlon.data.process import filter_dataframe_core, distance_between_blocks_distribution


def inter_block_distribution(df, contig_mode_flag, output_file, state='core', log=False):
    sns.set_theme(style="whitegrid", font_scale=1.3)
    plt.figure()

    distance_between_2d = []
    for chr, df_chr in df.groupby('chr/contig'):
        if state == 'core':
            df_filtered = filter_dataframe_core(df_chr)
            ds = distance_between_blocks_distribution(df_filtered)
        else:
            ds = distance_between_blocks_distribution(df_chr)
        for d in ds:
            distance_between_2d.append([chr, d])

    distance_between_df = pd.DataFrame(data=distance_between_2d, columns=['chromosome', 'distance'])
    sns.histplot(distance_between_df,
                 bins=50,
                 log_scale=(False, log),
                 x='distance',
                 hue='chromosome' if not contig_mode_flag else None,
                 element="step")

    plt.ylabel('Number of blocks')
    plt.xlabel('Length in nucleotides')
    plt.title(f'Length of fragments not covered by {"common" if state == "after" else "any"} blocks')

    plt.tight_layout()
    plt.xlim(xmin=0)

    plt.savefig(output_file)
    # plt.show()