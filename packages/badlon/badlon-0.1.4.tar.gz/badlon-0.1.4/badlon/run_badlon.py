import argparse
import sys

from textwrap import dedent

import badlon.prepare_data_for_sibeliaz as prepare
import badlon.blocks_analysis as analysis
import badlon.block_gene_match as match


def main():
    """
    Start program according to arguments given by user.
    """
    action, args = parse_arguments()
    action(args)


def parse_arguments():
    parser = argparse.ArgumentParser(description='Tool for block based analysis of bacterial populations. '
                                                 'Choose one of available modules.')

    actions = {}  # to add the action to do according to the subparser called

    subparsers = parser.add_subparsers(dest='subparser_called')

    # prepare module
    parser_prepare = subparsers.add_parser('prepare',
                                           help="Prepare draft dataset for SibeliaZ")
    prepare.build_parser(parser_prepare)
    actions['prepare'] = prepare.main

    # analysis module
    parser_analysis = subparsers.add_parser('analysis',
                                            help="Analyze pan-genome and other block-based features "
                                                 "based on synteny blocks.")
    analysis.build_parser(parser_analysis)
    actions['analysis'] = analysis.main

    # match module
    parser_match = subparsers.add_parser('match',
                                         help="Performs matching of block and genes based on coordinates.")
    match.build_parser(parser_match)
    actions['match'] = match.main

    args = parser.parse_args()
    action_called = args.subparser_called

    print('action_called', action_called)

    return actions[action_called], args


if __name__ == "__main__":
    main()
