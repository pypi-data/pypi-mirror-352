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
'''
Run tests on the dashboard table
'''

import csv
from json import dumps


import pandas as pd
import pytest
import sys
sys.path.append('./src')
sys.path.append('.')
from sdtp import SDML_BOOLEAN, SDML_NUMBER, SDML_STRING, SDML_DATE, SDML_DATETIME, SDML_TIME_OF_DAY, InvalidDataException
from sdtp import check_sdml_type_of_list
from sdtp import jsonifiable_value, jsonifiable_column
from sdtp import SDMLFixedTable, RowTable, FileTable, HTTPTable, RemoteSDMLTable, RowTableFactory, FileTableFactory, HTTPTableFactory
from pytest_httpserver import HTTPServer
import json

table_test_1 = {
    "rows": [["Ted", 21], ["Alice", 24], ['Mary', 24]],
    "schema": [
        {"name": "name", "type": SDML_STRING},
        {"name": "age", "type": SDML_NUMBER}
    ]
}

def _makeTable():
    return  SDMLFixedTable(table_test_1["schema"], lambda: table_test_1["rows"])

def test_create():
    '''
    Test table creation and ensure that the names and types match
    '''
    table = _makeTable()
    assert table.column_names() == ['name', 'age']
    assert table.column_types() == [SDML_STRING, SDML_NUMBER]
    assert table.get_rows() == table_test_1["rows"]
    for column in table_test_1["schema"]:
        assert(table.get_column_type(column["name"]) == column["type"])
    assert table.get_column_type(None) == None
    assert table.get_column_type("Foo") == None


def test_all_values_and_range_spec():
    '''
    Test getting all the values and the numeric specification from columns
    '''
    table = _makeTable()
    assert table.all_values('name') == ['Alice', 'Mary', 'Ted']
    assert table.all_values('age') == [21, 24]
    
    with pytest.raises(InvalidDataException) as e:
        table.all_values(None)
        # assert e.message == 'None is not a column of this table'
    with pytest.raises(InvalidDataException) as e:
        table.all_values('Foo')
        # assert e.message == 'Foo is not a column of this table'
    with pytest.raises(InvalidDataException) as e:
        table.range_spec(None)
        # assert e.message == 'None is not a column of this table'
    with pytest.raises(InvalidDataException) as e:
        table.range_spec('Foo')
        # assert e.message == 'Foo is not a column of this table'
    assert table.range_spec('name') == ["Alice", "Ted"] # {'max_val': "Ted", "min_val": "Alice"}
    assert table.range_spec('age') == [21, 24] # {'max_val': 24, "min_val": 21}
    assert table.get_column('name') == ['Ted', 'Alice', 'Mary']
    assert table.get_column('age') == [21, 24, 24]

    table.get_rows = lambda: [['Ted', 21], ['Alice', 24], ['Jane', 20]]
    assert table.range_spec('age') == [20, 24] # {'max_val': 24, "min_val": 20}
    assert table.all_values('name') == [ 'Alice', 'Jane', 'Ted']
    assert table.get_column('name') == ['Ted', 'Alice', 'Jane']
    assert table.range_spec('name') == [ 'Alice', 'Ted']


# Test to build a RowTable

from tests.table_data_good import names, ages, dates, times, datetimes, booleans
rows = [[names[i], ages[i], dates[i], times[i], datetimes[i], booleans[i]] for i in range(len(names))]

schema = [
    {"name": "name", "type": SDML_STRING},
    {"name": "age", "type": SDML_NUMBER},
    {"name": "date", "type": SDML_DATE},
    {"name": "time", "type": SDML_TIME_OF_DAY},
    {"name": "datetime", "type": SDML_DATETIME},
    {"name": "boolean", "type": SDML_BOOLEAN}
]


def test_row_table():
    row_table = RowTable(schema, rows)
    assert (row_table.schema == schema)
    assert (row_table.get_rows() == rows)


#
# test convert to dataframe
#

def test_construct_dataframe():
    row_table = RowTable(schema, rows)
    df = row_table.to_dataframe()
    assert(df.columns.tolist() == row_table.column_names())
    for column in schema:
        column_values = df[column["name"]].tolist()
        assert(check_sdml_type_of_list(column["type"], column_values))


import requests
from pytest_httpserver import HTTPServer
# @pytest.fixture(scope="session")
# def httpserver_listen_address():
#    return ("127.0.0.1", 8888)

def test_connect():
    httpserver = HTTPServer(port=8888)
    remote_table = RemoteSDMLTable('test', schema, httpserver.url_for("/"))
    assert(not remote_table.ok)
    httpserver.expect_request("/get_tables").respond_with_json({"test": schema})
    httpserver.start()
    remote_table.connect_with_server()
    assert(remote_table.ok)
    httpserver.stop()

def test_no_connect():
    httpserver = HTTPServer(port=8888)
    remote_table = RemoteSDMLTable('test', schema, httpserver.url_for("/"))
    with pytest.raises(InvalidDataException) as exception:
        remote_table.connect_with_server()
    assert(f'Error connecting with {remote_table.url}/get_tables' in repr(exception))
    assert(not remote_table.ok )

def test_bad_connect():
    httpserver = HTTPServer(port=8888)
    remote_table = RemoteSDMLTable('test', schema, httpserver.url_for("/"))
    assert(not remote_table.ok)
    httpserver.expect_request("/foobar").respond_with_json({"foo": "bar"})
    httpserver.start()
    with pytest.raises(InvalidDataException) as exception:
        remote_table.connect_with_server()
    assert(f'Bad connection with {remote_table.url}' in repr(exception))
    assert(not remote_table.ok)   
    httpserver.stop()


def test_bad_table():
    httpserver = HTTPServer(port=8888)
    remote_table = RemoteSDMLTable('test1', schema, httpserver.url_for("/"))
    assert(not remote_table.ok)
    httpserver.expect_request("/get_tables").respond_with_json({"test": schema})
    httpserver.start()
    with pytest.raises(InvalidDataException) as exception:
        remote_table.connect_with_server()
    assert(f'Server at {remote_table.url} does not have table {remote_table.table_name}' in repr(exception))
    assert(not remote_table.ok)   
    httpserver.stop()

def test_bad_schema():
    httpserver = HTTPServer(port=8888)
    bad_schema = schema[1:]
    remote_table = RemoteSDMLTable('test', bad_schema, httpserver.url_for("/"))
    httpserver.expect_request("/get_tables").respond_with_json({"test": schema})
    httpserver.start()
    with pytest.raises(InvalidDataException) as exception:
        remote_table.connect_with_server()
    assert(f' has {len(schema)} columns' in repr(exception))
    assert(not remote_table.ok)
    bad_schema = [dict(entry) for entry in schema]
    bad_schema[0]["name"] = "foo"
    remote_table.schema = bad_schema
    with pytest.raises(InvalidDataException) as exception:
        remote_table.connect_with_server()
    assert('Schema mismatch' in repr(exception))
    bad_schema = [dict(entry) for entry in schema]
    bad_schema[0]["type"] = SDML_DATETIME
    remote_table.schema = bad_schema
    with pytest.raises(InvalidDataException) as exception:
        remote_table.connect_with_server()
    assert('Schema mismatch' in repr(exception))
    httpserver.stop()

# Test the remote column operations.  The RemoteSDML table will issue requests to the httpserver, who will repond with the JSONIfied version.  The 
# Remote table will then translate that into a data structure.  So:
# 1. Pull the json  responses from the server table and get the server to respond with that
# 2. Translate each json response into a data structure
# 3. Pull the response from the RemoteTable and compare.
def test_remote_column_operations():
    httpserver = HTTPServer(port=3000)
    server_table = RowTable(schema, rows)
    httpserver.expect_request("/get_tables").respond_with_json({"test": schema})
    all_values_responses = {}
    range_spec_responses = {}
    get_column_responses = {}

    for column in schema:
        response = server_table.all_values(column["name"], False)
        json_response = jsonifiable_column(response, column["type"])
        httpserver.expect_request("/get_all_values", query_string={"table_name": "test", "column_name": column["name"]}).respond_with_json(json_response)
        all_values_responses[column["name"]] = response
    range_spec_responses = {}
    for column in schema:
        response = server_table.range_spec(column["name"], False)
        json_response = jsonifiable_column(response, column["type"])
        httpserver.expect_request("/get_range_spec", query_string={"table_name": "test", "column_name": column["name"]}).respond_with_json(json_response)
        range_spec_responses[column["name"]] = response
    for column in schema:
        response = server_table.get_column(column["name"], False)
        json_response = jsonifiable_column(response, column["type"])
        httpserver.expect_request("/get_column", query_string={"table_name": "test", "column_name": column["name"]}).respond_with_json(json_response)
        get_column_responses[column["name"]] = response
    httpserver.start()
    remote_table = RemoteSDMLTable('test', schema, httpserver.url_for("/"))
    column_names = [column["name"] for column in schema]
    remote_all_values_results = {}
    remote_range_spec_responses = {}
    remote_get_column_responses = {}

    for name in column_names:
        try:
            remote_all_values_results[name] = remote_table.all_values(name)
        except Exception:
            httpserver.stop()
            assert False
        try:
            remote_range_spec_responses[name] = remote_table.range_spec(name)
        except Exception:
            httpserver.stop()
            assert False
        try:
            remote_get_column_responses[name] = remote_table.get_column(name)
        except Exception:
            httpserver.stop()
            assert False
    httpserver.stop()
    assert remote_all_values_results == all_values_responses
    assert remote_range_spec_responses == range_spec_responses
    assert remote_get_column_responses == get_column_responses

# Test that the data in two tables are equivalent


def _data_equivalent(table1, table2):
    rows1 = table1.get_filtered_rows()
    rows2 = table2.get_filtered_rows()
    assert len(rows1) == len(rows2)
    for i in range(len(rows1)):
        assert rows1[i] == rows2[i]

# test that two tables are equivalent: the types and schemas 
# have to be the same, and the data has to be the same

def _tables_equivalent(table1, table2):
    assert type(table1) == type(table2)
    assert table1.schema == table2.schema
    _data_equivalent(table1, table2)

# Test a reloadable table.  The reloadable table should be a reloadable form
# of equivalent_table (the non-reloadable form of the same table)
# tests:
#   1. Make sure the reloadable_table starts off with no inner table and
#      the schema is the same as the equivalent table
#   2. Test load.  The inner_table should have the same schema as the 
#      the reloadable table.
#   3. Test that after load, the inner table and the equivalent table are equivalent
#   4. Test flush, ensuring that the inner_table is None after flush
#   5. Test that a get_filtered_rows request forces a load and the results of the
#      get_filtered_rows query are the same on the reloadable_table and the
#      equivalent table.  This is done by testing that the data is equivalent on
#      a flushed reloadable table and the equivalent table -- the get_filtered_rows()
#      call loads thg table and then calls get_filtered_rows() on the inner table
#   6. Retest flushing the table

def _test_reloadable_table(reloadable_table, equivalent_table):
    assert reloadable_table.inner_table is None
    assert reloadable_table.schema == equivalent_table.schema
    reloadable_table.load()
    assert reloadable_table.inner_table is not  None
    assert reloadable_table.schema == reloadable_table.inner_table.schema
    _tables_equivalent(reloadable_table.inner_table, equivalent_table)
    reloadable_table.flush()
    assert reloadable_table.inner_table is None
    _data_equivalent(reloadable_table, equivalent_table)
    reloadable_table.flush()
    assert reloadable_table.inner_table is None
    reloadable_table.flush()
    assert reloadable_table.inner_table is None
    for column in reloadable_table.schema:
        assert reloadable_table.all_values(column["name"]) == equivalent_table.all_values(column["name"])
        assert reloadable_table.get_column(column["name"]) == equivalent_table.get_column(column["name"])
        assert reloadable_table.range_spec(column["name"]) == equivalent_table.range_spec(column["name"])
    reloadable_table.flush()
    assert reloadable_table.inner_table is None


#
# test the file table using _test_reloadable_tables
# 

def test_file_table():
    r1 = RowTableFactory()
    f1 = FileTableFactory()
    # build and 
    with open('tests/tables/test1.sdml', 'r') as f:
        row_table_spec = json.load(f)
        row_table = r1.build_table(row_table_spec)
        assert isinstance(row_table, RowTable)
    with open('tests/tables/file_table.sdml', 'r') as f:
        file_table_spec = json.load(f)
        file_table = f1.build_table(file_table_spec)
        assert isinstance(file_table, FileTable)
        # check to make sure that file_table.inner_table is initially None
        assert file_table.inner_table is None
    _test_reloadable_table(file_table, row_table)

#
# test the http  table using _test_reloadable_tables
# 
def test_http_table():
    r1 = RowTableFactory()
    h1 = HTTPTableFactory()
    response = requests.get('https://raw.githubusercontent.com/rickmcgeer/sdtp-examples/refs/heads/main/simple-table-example/tables/nightingale.sdml')
    assert response.status_code < 400
    row_table_spec = response.json()
    row_table = r1.build_table(row_table_spec)
    assert isinstance(row_table, RowTable)
    with open('tests/tables/nightingale-http.sdml', 'r') as f:
        http_table_spec = json.load(f)
        http_table = h1.build_table(http_table_spec)
        assert isinstance(http_table, HTTPTable)
    _test_reloadable_table(http_table, row_table)