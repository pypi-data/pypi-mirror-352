'''
Middleware for a server deployment.  This is designed
to sit between the SDTP objects (in sdtp)
and a server.  These objects provide two principal
functions:
1. Keep the set of tables by name
2. Handle authentication on a table-specific basis
3. Convert results into the wire format for transmission

There are two major classes: 
1. Table, which provides a wrapper around the SDTP Table with the table's
   name, authentication requirememts, and result-conversion utilities
2. TableServer, which provides a registry and lookup service to Tables
'''

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


from json import load

import pandas as pd

from .sdtp_utils import InvalidDataException
from .sdtp_table import RowTableFactory, RemoteSDMLTableFactory, SDMLTable, SDMLTableFactory, FileTableFactory, GCSTableFactory, HTTPTableFactory

class TableNotFoundException(Exception):
    '''
    An exception that is thrown when a table is not found in the TableServer
    '''

    def __init__(self, message):
        super().__init__(message)


class ColumnNotFoundException(Exception):
    '''
    An exception that is thrown when a column is not found for a specific table
    '''

    def __init__(self, message):
        super().__init__(message)

def _check_type(value, python_type, message_prefix):
    # A utility that checks that value is of the correct type, which should be a Python type.
    # Doesn't return: instead, throws an Assertion Failure with a message when the type doesn't check
    assert isinstance(value, python_type), f'{message_prefix} {type(value)}'

def _check_dict_and_keys(dictionary, keys, dict_message, dict_name):
    # A utility that checks that dictionary is a dict, and that the keys keys are all present.  
    # Doesn't return: instead, throws an Assertion Failure with a message when the type doesn't check
    _check_type(dictionary, dict, dict_message)
    missing_keys = keys - dictionary.keys() if keys is not None else {}
    assert len(missing_keys) == 0, f'{dict_name} is missing keys {missing_keys}'


class TableServer:
    '''
    The server for tables.  Its task is to maintain a correspondence
    between table names and the actual tables.  It also maintains the security information for a table (the variables and values required to access the table), and gives column information across tables
    '''

    # Conceptually, there is only a single TableServer  (why would there #  be more?), and so this could be in a global variable and its # methods global.
    def __init__(self):
        self.servers = {}
        self.factories = {}
        # factories which are part of the standard  distribution
        self.add_table_factory(RowTableFactory())
        self.add_table_factory(RemoteSDMLTableFactory())
        self.add_table_factory(FileTableFactory())
        self.add_table_factory(GCSTableFactory())
        self.add_table_factory(HTTPTableFactory())


    def add_table_factory(self, table_factory):
        '''
        Add a TableFactory for table type table_type.  When 
        self.add_table_from_dictionary(table_spec) is called, the appropriate 
        factory is called to build it
        Arguments:
           table_factory: an instance of a subclass of TableFactory which actually builds the table
        '''
        # Check the table factory extends SDMLTableFactory
        _check_type(table_factory, SDMLTableFactory, 'table_factory must be an instance of SDMLTableFactory, not')
        table_type = table_factory.table_type
       
        _check_type(table_type, str, 'table_type must be a string, not')
        self.factories[table_type] = table_factory

    def add_sdtp_table(self, table_name, sdtp_table):
        '''
        Register a SDMLTable to serve data for a specific table name.
        Raises an InvalidDataException if table_name is None or sdtp_table is None or is not an instance of SDMLTable.

        Arguments:
            table_spec: dictionary of the form {"name", "table"}, where table is a Table (see above)

        '''
        _check_type(sdtp_table, SDMLTable, 'The sdtp_table argument to add_sdtp_table must be a Table, not')
        self.servers[table_name] = sdtp_table

    def add_sdtp_table_from_dictionary(self, name, table_dictionary):
        '''
        Add an  SDMLTable from a dictionary (intermediate on-disk form).   The table dictionary has fields schema and type, and then type-
        specific fields.  Calls self.factories[table_dictionary["type"]] to build the table,
        then calls self.add_sdtp_table to add the table.
        Raises an InvalidDataException if self.add_sdtp_table raises it or if the factory 
        is not present, or if the factory raises an exception

        Arguments:
            name: the name of the table
            table_dictionary: dictionary of the form {"name", "table"}, where table is a table specification: a dictionary
                             with the fields type and schema

        '''

        _check_dict_and_keys(table_dictionary, {'type', 'schema'}, 'table_dictionary must be a dictionary not', 'table_dictionary')
        table_type = table_dictionary['type']
        if table_type in self.factories.keys():
            table = self.factories[table_type].build_table(table_dictionary)
            self.add_sdtp_table(name,  table)
        else:
            raise InvalidDataException(f'No factory registered for {table_type}')


    def get_all_tables(self):
        '''
        Get all the tables.  This
        is to support a request for a numeric_spec or all_values for a column name when the
        table_name is not specified. In this case, all tables will be searched for this column name.
        

        Returns:
            a list of all tables
        '''
        tables = self.servers.values()
        return tables

    
    def get_table(self, table_name):
        '''
        Get the table with name table_name, first checking to see
        if  table access is authorized by the passed headers.
        Arguments:
            table_name: name of the table to search for
            
        Returns:
            The SDML table corresponding to the request
        Raises:
            TableNotFoundException if the table is not found
            
        '''
        try:
            return self.servers[table_name]
           
        except KeyError:
            raise TableNotFoundException(f'Table {table_name} not found')

   
    def get_all_values(self, table_name, column_name, jsonify = False):
        '''
        Get all of the distinct values for column column_name for table
        table_name.  Returns the list of distinct values for the columns
        Arguments:
            table_name: table to be searched
            column_name: name of the column
            jsonify: jsonify, or not, the result
           
        Returns:
            Returns the list of distinct values for the columns
        Raises:
            TableNotFoundException if the table is not found
            ColumnNotFoundException if the column can't be found
        '''

        _check_type(column_name, str, 'Column name must be a string, not')
        table = self.get_table(table_name)  # Note this will throw the TableNotFoundException

        try:
            return table.all_values(column_name, jsonify)
        except InvalidDataException:
            raise ColumnNotFoundException(f'Column {column_name} not found in table {table_name}')

    def get_range_spec(self, table_name, column_name, jsonify = False):
        '''
        Get the range specification for column column_name for table
        table_name.  Returns  a two-length list [min_val, max_val]
        Arguments:
            table_name: table to be searched
            column_name: name of the column
            jsonify: jsonify, or not, the result
        Returns:
            Returns  a dictionary with keys{max_val, min_val}
        Raises:
            TableNotFoundException if the table is not found
            ColumnNotFoundException if the column can't be found
        '''
        _check_type(column_name, str, 'Column name must be a string, not')
        table = self.get_table(table_name)  # Note this will throw the TableNotFoundException
        try:
            return table.range_spec(column_name, jsonify)
        except InvalidDataException:
            raise ColumnNotFoundException(f'Column {column_name} not found in table {table_name}')
        
    def get_column(self, table_name, column_name, jsonify = False):
        '''
        Get the column for column column_name for table
        table_name.  Returns the column as a list
        Arguments:
            table_name: table to be searched
            column_name: name of the column
            jsonify: jsonify, or not, the result
        Returns:
            Returns  a dictionary with keys{max_val, min_val}
        Raises:
            TableNotFoundException if the table is not found
            ColumnNotFoundException if the column can't be found
        '''
        _check_type(column_name, str, 'Column name must be a string, not')
        table = self.get_table(table_name)  # Note this will throw the TableNotFoundException
        try:
            return table.get_column(column_name, jsonify)
        except InvalidDataException:
            raise ColumnNotFoundException(f'Column {column_name} not found in table {table_name}')


