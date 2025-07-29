#   -*- coding: utf-8 -*-

##############################################################################
# copyrights and license
#
# Copyright (c) 2025 David Harris Kiesel
#
# Licensed under the MIT License. See LICENSE in the project root for license
# information.
##############################################################################

from copy import copy
import csv
from datetime import (
    date,
    datetime,
)
from decimal import Decimal
from typing import Iterable

# https://pypi.org/project/XlsxWriter/
# https://xlsxwriter.readthedocs.io/
# https://github.com/jmcnamara/XlsxWriter
import xlsxwriter


def parse_bool(
    s: str
) -> bool:
    'Parse a Boolean value.'

    ls = s.lower()

    if ls in (
        'true',
        't',
        'yes',
        'y',
        'on',
        '1',
    ):
        return True
    elif ls in (
        'false',
        'f',
        'no',
        'n',
        'off',
        '0'
    ):
        return False
    else:
        raise \
            ValueError(
                'Invalid value.'
            )


def get_first_and_last_columns(
    column_setting: dict,
    next_col: int
) -> tuple[int, int]:
    'Get first and last columns.'

    columns = column_setting.get('columns')

    if columns is not None:
        if columns.find(':') < 0:
            columns = \
                '{0}:{0}'.format(
                    columns
                )

        columns_components = \
            columns.split(':')

        (row, first_col) = \
            xlsxwriter.utility.xl_cell_to_rowcol(
                columns_components[0] + '1'
            )

        (row, last_col) = \
            xlsxwriter.utility.xl_cell_to_rowcol(
                columns_components[1] + '1'
            )
    else:
        first_col = next_col

        last_col = (
            next_col
            + column_setting.get(
                'span',
                1
            )
            - 1
        )

    return (first_col, last_col)


def get_first_and_last_rows(
    row_setting: dict,
    next_row: int
) -> tuple[int, int]:
    'Get first and last rows.'

    rows = row_setting.get('rows')

    if rows is not None:
        if rows.find(':') < 0:
            first_row = int(rows)

            last_row = int(rows)
        else:
            (first_row, last_row) = \
                [int(x) for x in rows.split(':')]
    else:
        first_row = next_row

        last_row = (
            next_row
            + row_setting.get(
                'span',
                1
            )
            - 1
        )

    return (first_row, last_row)


def get_workbook_format_setters(
    workbook: xlsxwriter.Workbook
) -> dict:
    'Get Workbook format setters.'

    return \
        {
            'font_name': workbook.formats[0].set_font_name,
            'font_size': workbook.formats[0].set_font_size,
            'font_color': workbook.formats[0].set_font_color,
            'bold': workbook.formats[0].set_bold,
            'italic': workbook.formats[0].set_italic,
            'underline': workbook.formats[0].set_underline,
            'font_strikeout': workbook.formats[0].set_font_strikeout,
            'font_script': workbook.formats[0].set_font_script,
            'num_format': workbook.formats[0].set_num_format,
            'locked': workbook.formats[0].set_locked,
            'hidden': workbook.formats[0].set_hidden,
            'align': workbook.formats[0].set_align,
            'valign': workbook.formats[0].set_align,
            'rotation': workbook.formats[0].set_rotation,
            'text_wrap': workbook.formats[0].set_text_wrap,
            'reading_order': workbook.formats[0].set_reading_order,
            'text_justlast': workbook.formats[0].set_text_justlast,
            'center_across': workbook.formats[0].set_center_across,
            'indent': workbook.formats[0].set_indent,
            'shrink': workbook.formats[0].set_shrink,
            'pattern': workbook.formats[0].set_pattern,
            'bg_color': workbook.formats[0].set_bg_color,
            'fg_color': workbook.formats[0].set_fg_color,
            'border': workbook.formats[0].set_border,
            'bottom': workbook.formats[0].set_bottom,
            'top': workbook.formats[0].set_top,
            'left': workbook.formats[0].set_left,
            'right': workbook.formats[0].set_right,
            'border_color': workbook.formats[0].set_border_color,
            'bottom_color': workbook.formats[0].set_bottom_color,
            'top_color': workbook.formats[0].set_top_color,
            'left_color': workbook.formats[0].set_left_color,
            'right_color': workbook.formats[0].set_right_color,
        }


def apply_workbook_format(
    workbook: xlsxwriter.Workbook,
    workbook_format: dict
) -> None:
    'Apply Workbook format.'

    format_setters = \
        get_workbook_format_setters(
            workbook
        )

    for setting in list(workbook_format):
        value = workbook_format.get(setting)

        format_setter = format_setters.get(setting)

        if format_setter is not None:
            format_setter(value)


def transform(
    csv_iterable: Iterable[str],
    workbook_path: str,
    workbook_settings: dict = None
) -> None:
    'Read a CSV iterable and write an XLSX file.'

    if workbook_settings is None:
        workbook_settings = {}

    workbook_options = \
        workbook_settings.get(
            'workbook_options',
            {}
        )

    workbook_options['constant_memory'] = True

    workbook_format = \
        workbook_settings.get(
            'workbook_format',
            {}
        )

    worksheet_settings = \
        workbook_settings.get(
            'worksheet_settings',
            {}
        )

    cell_format_settings_default = \
        workbook_settings.get(
            'cell_format_settings_default',
            {}
        )

    cell_format_settings = \
        workbook_settings.get(
            'cell_format_settings',
            {}
        )

    column_settings = \
        workbook_settings.get(
            'column_settings',
            []
        )

    row_settings = \
        workbook_settings.get(
            'row_settings',
            []
        )

    with xlsxwriter.Workbook(
        filename=workbook_path,
        options=workbook_options
    ) as workbook:
        apply_workbook_format(
            workbook,
            workbook_format
        )

        cell_formats = {}

        if 'default' not in cell_format_settings:
            cell_format_settings['default'] = {}

        for cell_format_name in cell_format_settings:
            cell_formats[cell_format_name] = \
                workbook.add_format(
                    workbook_format
                    | cell_format_settings_default
                    | cell_format_settings[cell_format_name]
                )

        worksheet = \
            workbook.add_worksheet()

        default_width = 10

        column_data_types = {}

        next_col = 0

        for column_setting in column_settings:
            (first_col, last_col) = \
                get_first_and_last_columns(
                    column_setting,
                    next_col
                )

            worksheet.set_column(
                first_col,
                last_col,
                width=column_setting.get(
                    'width',
                    default_width
                ),
                cell_format=cell_formats.get(
                    column_setting.get(
                        'cell_format',
                        'default'
                    )
                ),
                options=column_setting.get('options')
            )

            for col in range(
                first_col,
                last_col + 1
            ):
                column_data_types[col] = \
                    column_setting.get('data_type')

            next_col = last_col + 1

        row_settings_dict = {}

        next_row = 0

        for row_setting in row_settings:
            (first_row, last_row) = \
                get_first_and_last_rows(
                    row_setting,
                    next_row
                )

            for row in range(first_row, last_row + 1):
                worksheet.set_row(
                    row,
                    cell_format=cell_formats.get(
                        row_setting.get(
                            'cell_format',
                            'default'
                        )
                    )
                )

                row_settings_dict[row] = row_setting

            next_row = last_row + 1

        csv_reader = \
            csv.reader(
                csv_iterable
            )

        max_column_offset = -1

        for row_offset, row in enumerate(csv_reader):
            row_setting = row_settings_dict.get(row_offset)

            for column_offset, cell_value in enumerate(row):
                if row_setting is not None:
                    data_type = \
                        row_setting.get('data_type')
                else:
                    data_type = \
                        column_data_types.get(column_offset)

                if data_type == 'decimal':
                    try:
                        converted_cell_value = \
                            Decimal(cell_value)

                        worksheet.write(
                            row_offset,
                            column_offset,
                            converted_cell_value
                        )
                    except Exception:
                        worksheet.write_string(
                            row_offset,
                            column_offset,
                            cell_value
                        )
                elif data_type == 'bool':
                    try:
                        converted_cell_value = \
                            parse_bool(cell_value)

                        worksheet.write(
                            row_offset,
                            column_offset,
                            converted_cell_value
                        )
                    except Exception:
                        worksheet.write_string(
                            row_offset,
                            column_offset,
                            cell_value
                        )
                elif data_type == 'date':
                    try:
                        converted_cell_value = \
                            date.fromisoformat(cell_value)

                        worksheet.write(
                            row_offset,
                            column_offset,
                            converted_cell_value
                        )
                    except Exception:
                        worksheet.write_string(
                            row_offset,
                            column_offset,
                            cell_value
                        )
                elif data_type == 'datetime':
                    try:
                        converted_cell_value = \
                            datetime.fromisoformat(cell_value)

                        worksheet.write(
                            row_offset,
                            column_offset,
                            converted_cell_value
                        )
                    except Exception:
                        worksheet.write_string(
                            row_offset,
                            column_offset,
                            cell_value
                        )
                elif data_type == 'formula':
                    worksheet.write_formula(
                        row_offset,
                        column_offset,
                        cell_value
                    )
                else:
                    worksheet.write_string(
                        row_offset,
                        column_offset,
                        cell_value
                    )

                if column_offset > max_column_offset:
                    max_column_offset = column_offset

        autofilter = \
            copy(
                worksheet_settings.get('autofilter')
            )

        if autofilter is not None:
            if isinstance(autofilter, list):
                if (
                    autofilter[2] > row_offset
                    or autofilter[2] < 0
                ):
                    autofilter[2] = row_offset

                if (
                    autofilter[3] > max_column_offset
                    or autofilter[3] < 0
                ):
                    autofilter[3] = max_column_offset

                worksheet.autofilter(
                    *autofilter
                )
            else:
                worksheet.autofilter(
                    autofilter
                )

        freeze_panes = \
            worksheet_settings.get('freeze_panes')

        if freeze_panes is not None:
            if isinstance(freeze_panes, list):
                worksheet.freeze_panes(
                    *freeze_panes
                )
            else:
                worksheet.freeze_panes(
                    freeze_panes
                )
