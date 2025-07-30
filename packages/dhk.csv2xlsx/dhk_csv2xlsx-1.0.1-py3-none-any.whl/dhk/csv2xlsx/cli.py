#   -*- coding: utf-8 -*-

##############################################################################
# copyrights and license
#
# Copyright (c) 2025 David Harris Kiesel
#
# Licensed under the MIT License. See LICENSE in the project root for license
# information.
##############################################################################

import argparse
import json
import logging
import os.path
import sys

from dhk.csv2xlsx import csv2xlsx


def get_parser() -> argparse.ArgumentParser:
    'Get parser.'

    parser = \
        argparse.ArgumentParser(
            prog='csv2xlsx',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            description='Read a CSV file and write an XLSX file.',
            add_help=True,
            epilog="""
Examples:

    %(prog)s \\
        CSV_FILE

    %(prog)s \\
        --settings-file SETTINGS_FILE \\
        CSV_FILE

    %(prog)s \\
        --settings-file SETTINGS_FILE \\
        --output OUTPUT \\
        CSV_FILE
"""
        )

    parser.add_argument(
        '--settings-file',
        '-s',
        dest='settings_fd',
        metavar='SETTINGS_FILE',
        type=argparse.FileType('r'),
        default=None,
        help='settings file; default: None'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='count',
        default=0,
        help='verbose'
    )

    parser.add_argument(
        '--force',
        '-f',
        action='store_true',
        help='force; suppress prompts'
    )

    parser.add_argument(
        '--output',
        '-o',
        dest='output_file',
        default=None,
        help='output file; default: CSV_FILE - .csv + .xlsx'
    )

    parser.add_argument(
        'csv_fd',
        metavar='CSV_FILE',
        type=argparse.FileType('r'),
        help='CSV file'
    )

    return parser


def configure_logging(
    level: int
) -> None:
    'Configure logging.'

    logging.basicConfig(
        level=level
    )


def main(
    args: argparse.Namespace
) -> None:
    '``main`` entry point.'

    logging_levels = \
        (
            logging.WARNING,
            logging.INFO,
            logging.DEBUG,
        )

    configure_logging(
        logging_levels[
            min(
                len(logging_levels) - 1,
                args.verbose
            )
        ]
    )

    if args.settings_fd is not None:
        workbook_settings = \
            json.load(args.settings_fd)

        args.settings_fd.close()
    else:
        workbook_settings = {}

    workbook_path = args.output_file

    if workbook_path is None:
        root, ext = \
            os.path.splitext(
                args.csv_fd.name
            )

        workbook_path = \
            root + '.xlsx'

    if not args.force:
        if os.path.exists(workbook_path):
            while True:
                response = \
                    input(
                        "Output file '{0}' exists.  Continue? (y/n) ".format(
                            workbook_path
                        )
                    )

                if response == 'y':
                    break
                elif response == 'n':
                    sys.exit()

    csv2xlsx.transform(
        args.csv_fd,
        workbook_path,
        workbook_settings=workbook_settings
    )

    args.csv_fd.close()
