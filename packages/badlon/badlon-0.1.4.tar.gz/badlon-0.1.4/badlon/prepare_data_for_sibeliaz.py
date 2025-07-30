import os

import pandas as pd
import numpy as np

from Bio import SeqIO
from glob import glob
from collections import defaultdict, Counter


def build_parser(parser):
    required = parser.add_argument_group('Required arguments')

    required.add_argument('--folder', '-f', required=True,
                        help='Folder with PanACoTA output. '
                             'Will be used to search genome files based on LSTINFO file from annotate module.')
    parser.add_argument('--contigs', '-c',
                        help='Number of maximum contigs to take from every genome. '
                             'By default, keeps all.',
                        type=int,
                        default=1_000_000)
    parser.add_argument('--output', '-o', help='Output file path.', default='for_sibeliaz.fna')
    parser.add_argument('--annotate_subfolder', '-a',
                        help='Subfolder of PanACoTA contains results of annotate module. '
                             'Used for finding LSTINFO file. '
                             'Default is \'2-annotate\'.',
                        default='2-annotate')
    parser.add_argument('--min_len', '-l',
                        help='Minimum contig length, less then that value will be filtered. Default is 1000.',
                        default=1000,
                        type=int)
    return parser


def main(args):
    folder = args.folder if args.folder[-1] == '/' else args.folder + '/'

    gembase_file = glob(folder + args.annotate_subfolder + '/LSTINFO-LSTINFO*')[0]
    output_file = args.output
    os.makedirs(folder + 'blocks-sibeliaz/', exist_ok=True)

    gembase_df = pd.read_csv(gembase_file, sep='\t')
    all_contigs = []

    cnt = Counter()
    contig_lengths = defaultdict(list)

    for _, row in gembase_df.iterrows():
        contigs = [contig for contig in SeqIO.parse(open(folder + row['orig_name']), 'fasta')][0:args.contigs]
        contigs = [contig for contig in contigs if len(contig) > args.min_len]

        for i, contig in enumerate(contigs):
            # print(contig.id, contig.name, contig.description)
            contigs[i].id = row['gembase_name'] + '.' + str(i + 1) + ' ' + contig.description
            contig_lengths[i + 1].append(len(contig))

        # assert len(contigs) == args.contigs
        print(f'Found genome:')
        print('    Label:', row['gembase_name'])
        print('    Filepath:', row['orig_name'])
        print('    Contig/chrs:', len(contigs))

        cnt[len(contigs)] += 1

        all_contigs += contigs

    # print(cnt)
    for chr, lengths in contig_lengths.items():
        print('Chr/contig:', chr, '   mean length:', np.mean(lengths))

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    SeqIO.write(all_contigs, open(output_file, 'w'), 'fasta')

    print('\nCreated file:', output_file)

    print()
    print('___________________________________________')
    print('Recommended SibeliaZ command:')
    print(f'sibeliaz -k 15 -a {len(gembase_df) * 20} '
          f'-n -t 32 -o sibeliaz_out {output_file}')

    print()
    print('___________________________________________')
    print('For building blocks (blocks minimal size 3000):')
    print('cd sibeliaz_out')
    print(f'echo $\'30 150\\n100 500\\n500 1500\' > fine.txt')
    print('maf2synteny -s fine.txt -b 3000 blocks_coords.gff')