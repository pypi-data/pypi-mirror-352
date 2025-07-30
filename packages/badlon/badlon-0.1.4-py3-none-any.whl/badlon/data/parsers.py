import re
import os

import pandas as pd
import numpy as np

from collections import defaultdict
from itertools import takewhile
from io import StringIO
from glob import glob


PATTERN = re.compile("([A-Za-z0-9_\(\)\/\s\.-]+)\.([A-Za-z0-9_]+):(\d+)-(\d+) ([+|-]).*")
COLUMNS = ["block", "genome", "chr/contig", "start", "end", "orientation"]
BLOCKS_SEPARATOR = '-' * 80

LST_INFO_COLUMNS = ['start', 'end', 'orientation', 'type', 'gene_id', 'gene', 'desc']


def parse_infercars_to_df(file_name):
    def find_indices(lst, condition):
        return [i for i, elem in enumerate(lst) if condition(elem)]

    with open(file_name) as f:
        lines = f.readlines()

    last_line = len(lines) - 1
    while lines[last_line] == '\n': last_line -= 1

    n_at_end = len(lines) - 1 - last_line
    for _ in range(1 - n_at_end): lines.append('\n')

    bs = np.split(lines, find_indices(lines, lambda x: x[0] == ">"))
    temp = []

    for i, b in enumerate(bs):
        if len(b) == 0: continue
        b_i = int(b[0][1:])

        for oc in b[1:-1]:
            m = PATTERN.match(oc)
            temp.append([b_i, m.group(1), m.group(2), int(m.group(3)), int(m.group(4)), m.group(5)])

    return pd.DataFrame(temp, columns=COLUMNS)


def genome_lengths_from_block_coords(in_file):
    with open(in_file) as f:
        head_lines = list(takewhile(lambda line: (line != BLOCKS_SEPARATOR + os.linesep) and
                                                 (line != BLOCKS_SEPARATOR + '\n'), f))

    # names of chromosomes
    df_head = pd.read_csv(StringIO(''.join(head_lines)), sep='\t')
    df_head['genome'] = [d.rsplit('.', 1)[0] for d in df_head.Description]
    df_head['chr/contig'] = [d.rsplit('.', 1)[1] for d in df_head.Description]
    df_head['size'] = df_head['Size']

    df_head.drop(columns=['Seq_id', 'Size', 'Description'], inplace=True)

    return df_head


def parse_genes_lst(folder_genes):
    genes_dfs = []
    for lst_file in glob(folder_genes + '*.lst'):
        genes_df = pd.read_csv(lst_file, sep='\t', header=None, names=LST_INFO_COLUMNS)
        genes_dfs.append(genes_df)

    if len(genes_dfs) == 0:
        raise ValueError(f'Did not found any .lst files in `{folder_genes}` folder.')

    return pd.concat(genes_dfs)