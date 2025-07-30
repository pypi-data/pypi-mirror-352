import matplotlib.pyplot as plt
import seaborn as sns


def length_distribution(df, output_file, contig_mode_flag, log=False):
    plt.figure()
    sns.set_theme(style="whitegrid", font_scale=1.3)

    df.rename(columns={'chroms': 'chromosome'}, inplace=True)
    sns.histplot(df,
                 x='mean_length',
                 hue='chromosome' if not contig_mode_flag else None,
                 bins=50,
                 log_scale=(False, log),
                 element="step",
                 hue_order=['1', '2', '1,2'])

    plt.ylabel('Number of blocks')
    plt.xlabel('Mean length in nucleotides')
    plt.xlim(xmin=0)
    plt.title(f'Distribution of LCB length')

    plt.tight_layout()
    plt.savefig(output_file)