import logging
import sys
import argparse
import os
import shutil

import seaborn as sns
import matplotlib.pyplot as plt

from badlon.data.converters import block_coords_to_infercars
from badlon.data.parsers import genome_lengths_from_block_coords, parse_infercars_to_df
from badlon.data.coverage import calculculate_covered
from badlon.data.process import block_genome_count
from badlon.charts.u_curve import u_curve
from badlon.charts.length_distribution import *
from badlon.charts.inter_block_distribution import *
from badlon.charts.pan_genome import *
from badlon.charts.coverage import *

INFERCARS_FILENAME = 'blocks_coords.infercars'
BLOCKS_TABLE_FILENAME = 'blocks_coords.csv'
BLOCK_FREQ_TABLE_FILENAME = 'blocks_frequency.csv'
COVERAGE_TABLE_FILENAME = 'lengths_coverages.csv'


def build_parser(parser):
    required = parser.add_argument_group('Required arguments')

    required.add_argument('--blocks_file', '-b', required=True,
                          help='Blocks resulted as output of original Sibelia or maf2synteny tool. '
                               'Usually it\'s sibeliaz_out/3000/block_coords.txt file.')

    required.add_argument('--type', '-t',
                        required=True,
                        choices=['chr', 'contig'],
                        help='Type of genome assembly, either \'chr\' or \'contig\'')

    parser.add_argument('--output', '-o', default='blockomics_output',
                          help='Path to output folder. Default: blockomics_output.')


def preprocess_data():
    global block_count_df, blocks_df, coverage_df

    block_coords_to_infercars(blocks_file, other_folder + INFERCARS_FILENAME)

    chr_lengths = genome_lengths_from_block_coords(blocks_file)

    blocks_df = parse_infercars_to_df(other_folder + INFERCARS_FILENAME)
    blocks_df['length'] = blocks_df['end'] - blocks_df['start']

    coverage_df = calculculate_covered(blocks_df, chr_lengths, contig_mode_flag)
    block_count_df = block_genome_count(blocks_df)

    coverage_df.to_csv(tables_folder + COVERAGE_TABLE_FILENAME, index=False)
    blocks_df.to_csv(tables_folder + BLOCKS_TABLE_FILENAME, index=False)
    block_count_df.to_csv(tables_folder + BLOCK_FREQ_TABLE_FILENAME, index=False)


def charts():
    u_curve(block_count_df, weighted=True, output_file=figures_folder + 'u_curve_weighted.pdf',
            contig_mode_flag=contig_mode_flag)
    u_curve(block_count_df, weighted=False, output_file=figures_folder + 'u_curve.pdf',
            contig_mode_flag=contig_mode_flag)

    length_distribution(block_count_df, output_file=figures_folder + 'block_length_distribution.pdf',
                        contig_mode_flag=contig_mode_flag)

    inter_block_distribution(blocks_df, output_file=figures_folder + 'inter_block_length_core.pdf', state='core',
                             contig_mode_flag=contig_mode_flag)
    inter_block_distribution(blocks_df, output_file=figures_folder + 'inter_block_length_all.pdf', state='all',
                             contig_mode_flag=contig_mode_flag)

    coverage(coverage_df, output_file=figures_folder + 'coverage_distribution.pdf')

    pan_blocks(blocks_df, output_folder=figures_folder, contig_mode_flag=contig_mode_flag)
    pan_blocks_length(blocks_df, output_folder=figures_folder, contig_mode_flag=contig_mode_flag)


def main(args):
    global blocks_file, other_folder, tables_folder, figures_folder, contig_mode_flag

    d = vars(args)
    output_folder, blocks_file, contig_mode_flag = d['output'], d['blocks_file'], d['type'] == 'contig'
    if output_folder[-1] != '/': output_folder += '/'
    shutil.rmtree(output_folder, ignore_errors=True)

    tables_folder = output_folder + 'tables/'
    figures_folder = output_folder + 'figures/'
    other_folder = output_folder + 'other_formats/'

    os.makedirs(tables_folder, exist_ok=True)
    os.makedirs(figures_folder, exist_ok=True)
    os.makedirs(other_folder, exist_ok=True)

    preprocess_data()
    charts()