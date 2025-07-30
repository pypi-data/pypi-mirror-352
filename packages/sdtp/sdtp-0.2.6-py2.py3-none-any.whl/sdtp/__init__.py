"""Top-level package for The Simple Data Transfer Protocol."""

__author__ = """Rick McGeer"""
__email__ = 'rick@mcgeer.com'
__version__ = '0.1.0'

# BSD 3-Clause License
# Copyright (c) 2024, The Regents of the University of California (Regents)
# All rights reserved.
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from .sdtp_utils import InvalidDataException
from .sdtp_utils import SDML_BOOLEAN, SDML_DATE, SDML_DATETIME, SDML_NUMBER, SDML_PYTHON_TYPES, SDML_SCHEMA_TYPES, SDML_STRING, SDML_TIME_OF_DAY
from .sdtp_utils import type_check, check_sdml_type_of_list, jsonifiable_value,  jsonifiable_row, jsonifiable_rows, jsonifiable_column, convert_to_type, convert_list_to_type, convert_row_to_type_list, convert_rows_to_type_list, convert_dict_to_type
from .sdtp_filter import SDQL_FILTER_OPERATORS, SDQL_FILTER_FIELDS, check_valid_spec, check_valid_spec_return_boolean, SDQLFilter
from .sdtp_table import SDMLTable, SDMLFixedTable, SDMLDataFrameTable, RowTable, RemoteSDMLTable, SDMLTableFactory, RowTableFactory, RemoteSDMLTableFactory, FileTable, FileTableFactory, GCSTable, GCSTableFactory, HTTPTable, HTTPTableFactory
from .table_server import  TableServer, TableNotFoundException, ColumnNotFoundException
from .sdtp_server import sdtp_server_blueprint, SDTPServer

__all__ = [
  'InvalidDataException',
  'SDML_BOOLEAN', 'SDML_DATE', 'SDML_DATETIME', 'SDML_NUMBER', 'SDML_PYTHON_TYPES', 'SDML_SCHEMA_TYPES', 'SDML_STRING', 'SDML_TIME_OF_DAY',
  'type_check', 'check_sdml_type_of_list', 'jsonifiable_value', ' jsonifiable_row', 'jsonifiable_rows', 'jsonifiable_column', 'convert_to_type', 'convert_list_to_type', 'convert_row_to_type_list', 'convert_rows_to_type_list', 'convert_dict_to_type',
  'SDQL_FILTER_OPERATORS', 'SDQL_FILTER_FIELDS', 'check_valid_spec', 'check_valid_spec_return_boolean', 'SDQLFilter',
  'SDMLTable', 'SDMLFixedTable', 'SDMLDataFrameTable', 'RowTable', 'RemoteSDMLTable', 'SDMLTableFactory', 'RowTableFactory', 'RemoteSDMLTableFactory', 'FileTable', 'FileTableFactory', 'GCSTable', 'GCSTableFactory', 'HTTPTable', 'HTTPTableFactory',
  'TableServer', 'TableNotFoundException', 'ColumnNotFoundException',
  'sdtp_server_blueprint', 'SDTPServer'
]