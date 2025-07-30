import os.path
import argparse

import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from itertools import chain
from glob import glob
from bisect import bisect
from collections import defaultdict, Counter

from badlon.data.converters import block_coords_to_infercars
from badlon.data.parsers import genome_lengths_from_block_coords, parse_infercars_to_df, parse_genes_lst
from badlon.charts.coverage import coverages_match_chart


INFERCARS_FILENAME = 'blocks_coords.infercars'
ANNOTATED_BLOCKS_FILE = 'annotated_blocks_coords.csv'
ANNOTATED_GENES_FILE = 'annotated_genes_coords.csv'

lst_info_columns = ['start', 'end', 'orientation', 'type', 'gene_id', 'gene', 'desc']
genome_lengths_file = 'genomes_lengths.csv'


def build_parser(parser):
    required = parser.add_argument_group('Required arguments')

    required.add_argument('--blocks_file', '-b', required=True,
                          help='Blocks folder resulted as output of original Sibelia or maf2synteny tool. '
                               'Usually it\'s `sibeliaz_out/3000/` folder.')

    required.add_argument('--annotated_folder', '-a', required=True,
                        help='LSTINFO folder path, output of `annotate` step of PanACoTA.')

    required.add_argument('--pangenome_file', '-pg', required=True,
                        help='File .lst with orthologous genes, output of `pangenome` step of PanACoTA.')

    required.add_argument('--type', '-t',
                        required=True,
                        choices=['chr', 'contig'],
                        help='Type of genome assembly, either \'chr\' or \'contig\'')

    parser.add_argument('--output', '-o', default='block_genes_match_output',
                          help='Path to output folder. Default: blockomics_output.')


def annotate_genes_og(genes_df, pangenome_file):
    gene_to_group = {}

    with open(pangenome_file) as f:
        lines = [line.rstrip() for line in f]
        for line in lines:
            splited = line.split()
            og = int(splited[0])
            genes = splited[1:]

            for gene in genes:
                gene_to_group[gene] = og

    genes_df['og'] = [gene_to_group.get(id, '') for id in genes_df['gene_id']]


def annotate_genes_chromo_genome(genes_df):
    def get_chromo(gene_id):
        chromo = gene_id.split('.')[-1].split('_')[0]
        filtered_letters = ''.join([c for c in chromo if not c.isalpha()])

        return int(filtered_letters)

    def get_genome(gene_id):
        return gene_id.rsplit('.', 1)[0]

    genes_df['genome'] = [get_genome(gene_id) for gene_id in genes_df.gene_id]
    genes_df['chr/contig'] = [get_chromo(gene_id) for gene_id in genes_df.gene_id]


def match_blocks_genes(blocks_df, genes_df):
    def get_ogs_ids(genes_df, inverted=False):
        ogs = [0 if og == '' else (og if or_ == 'D' else -og) for og, or_ in zip(genes_df.og, genes_df.orientation)]
        ids = [id for id, or_ in zip(genes_df.gene_id, genes_df.orientation)]
        return ([-og for og in ogs[::-1]], ids[::-1]) if inverted else (ogs, ids)

    block_to_left_border_ogs, block_to_left_border_ids = defaultdict(list), defaultdict(list)
    block_to_right_border_ogs, block_to_right_border_ids = defaultdict(list), defaultdict(list)
    block_to_ogs, block_to_ids = defaultdict(list), defaultdict(list)

    gene_to_block = defaultdict(lambda: ('outside', ''))

    for strain, genes_strain_df in genes_df.groupby('genome'):
        for chr, genes_strain_chr_df in genes_strain_df.groupby('chr/contig'):
            blocks_strain_df = blocks_df[(blocks_df['genome'] == strain) & (blocks_df['chr/contig'] == str(chr))] \
                .sort_values(by=['start'])
            genes_strain_chr_df = genes_strain_chr_df.sort_values('start')

            for b_id, b_start, b_end, b_or in zip(blocks_strain_df.block, blocks_strain_df.start,
                                                  blocks_strain_df.end, blocks_strain_df.orientation):

                genes_start_index = bisect(genes_strain_chr_df.start.values, b_start)
                genes_start_index = genes_start_index - 1 if genes_start_index > 0 else 0
                genes_end_index = bisect(genes_strain_chr_df.start.values, b_end)

                if genes_strain_chr_df.end.values[genes_start_index] < b_start:
                    genes_start_index += 1

                current_genes = genes_strain_chr_df[genes_start_index:genes_end_index]

                genes_start_index, genes_end_index = 0, len(current_genes)

                if len(current_genes) == 0: continue

                start_is_on_border = current_genes.start.values[0] < b_start
                end_is_on_border = current_genes.end.values[-1] > b_end

                if start_is_on_border: genes_start_index += 1
                if end_is_on_border: genes_end_index -= 1

                inverted = b_or == '-'
                left_ogs, left_ids = get_ogs_ids(current_genes[0:genes_start_index], inverted)
                center_ogs, center_ids = get_ogs_ids(current_genes[genes_start_index:genes_end_index], inverted)
                right_ogs, right_ids = get_ogs_ids(current_genes[genes_end_index:], inverted)

                for g_id in current_genes[0:genes_start_index].gene_id:
                    gene_to_block[g_id] = ('left_border', b_id)
                for g_id in current_genes[genes_start_index:genes_end_index].gene_id:
                    gene_to_block[g_id] = ('inside', b_id)
                for g_id in current_genes[genes_end_index:].gene_id:
                    gene_to_block[g_id] = ('right_border', b_id)

                block_to_ogs[(strain, b_id, b_start)] = center_ogs
                block_to_ids[(strain, b_id, b_start)] = center_ids

                block_to_left_border_ogs[(strain, b_id, b_start)], \
                block_to_right_border_ogs[(strain, b_id, b_start)] = \
                    (right_ogs, left_ogs) if inverted else (left_ogs, right_ogs)

                block_to_left_border_ids[(strain, b_id, b_start)], \
                block_to_right_border_ids[(strain, b_id, b_start)] = \
                    (right_ids, left_ids) if inverted else (left_ids, right_ids)

    blocks_df['genes_tail_ids'] = [' '.join(map(str, block_to_left_border_ids[(b_strain, b_id, b_s)]))
                               for b_id, b_strain, b_s in zip(blocks_df.block, blocks_df.genome, blocks_df.start)]
    blocks_df['genes_inside_ids'] = [' '.join(map(str, block_to_ids[(b_strain, b_id, b_s)]))
                                 for b_id, b_strain, b_s in zip(blocks_df.block, blocks_df.genome, blocks_df.start)]
    blocks_df['genes_head_ids'] = [' '.join(map(str, block_to_right_border_ids[(b_strain, b_id, b_s)]))
                               for b_id, b_strain, b_s in zip(blocks_df.block, blocks_df.genome, blocks_df.start)]

    blocks_df['genes_tail_ogs'] = [' '.join(map(str, block_to_left_border_ogs[(b_strain, b_id, b_s)]))
                               for b_id, b_strain, b_s in zip(blocks_df.block, blocks_df.genome, blocks_df.start)]
    blocks_df['genes_inside_ogs'] = [' '.join(map(str, block_to_ogs[(b_strain, b_id, b_s)]))
                                 for b_id, b_strain, b_s in zip(blocks_df.block, blocks_df.genome, blocks_df.start)]
    blocks_df['genes_head_ogs'] = [' '.join(map(str, block_to_right_border_ogs[(b_strain, b_id, b_s)]))
                               for b_id, b_strain, b_s in zip(blocks_df.block, blocks_df.genome, blocks_df.start)]

    genes_df['block_state'] = [gene_to_block[g_id][0] for g_id in genes_df.gene_id]
    genes_df['block_id'] = [gene_to_block[g_id][1] for g_id in genes_df.gene_id]


def main(args):
    output_folder, blocks_file, contig_mode_flag = args.output, args.blocks_file, args.type == 'contig'
    annotated_folder, pangenome_file = args.annotated_folder, args.pangenome_file
    if output_folder[-1] != '/': output_folder += '/'
    if annotated_folder[-1] != '/': annotated_folder += '/'
    if not 'LSTINFO' in annotated_folder: annotated_folder += 'LSTINFO/'

    other_folder = output_folder + 'other_formats/'
    os.makedirs(output_folder, exist_ok=True)
    os.makedirs(other_folder, exist_ok=True)

    chr_lengths_df = genome_lengths_from_block_coords(blocks_file)
    chr_lengths = {(g, c): s for g, c, s in
                   zip(chr_lengths_df['genome'], chr_lengths_df['chr/contig'], chr_lengths_df['size'])}

    genes_df = parse_genes_lst(annotated_folder)
    annotate_genes_og(genes_df, pangenome_file)
    annotate_genes_chromo_genome(genes_df)

    block_coords_to_infercars(blocks_file, other_folder + INFERCARS_FILENAME)
    blocks_df = parse_infercars_to_df(other_folder + INFERCARS_FILENAME)

    match_blocks_genes(blocks_df, genes_df)

    blocks_df.to_csv(output_folder + ANNOTATED_BLOCKS_FILE, index=False)
    genes_df.to_csv(output_folder + ANNOTATED_GENES_FILE, index=False)

    cov_df = coverages_match_chart(blocks_df, genes_df, chr_lengths, output_folder, contig_mode_flag, filter_singletons=True)
    cov_df.to_csv(output_folder + 'coverages_perc.csv', index=False)
