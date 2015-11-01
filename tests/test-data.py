# -*- coding: utf8 -*-

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from nose.tools import assert_true, assert_equals
from .utils import setup_func, with_setup_args, random_string

import redlink
from redlink.format import Format


@with_setup_args(setup_func)
def test_sparql(key):
    data = redlink.create_data_client(key)
    assert_true(data.status["accessible"])
    results = data.sparql_tuple_query("select * where { ?s ?p ?o }", "test")
    assert_true(len(results["results"]["bindings"]) >= 0)


@with_setup_args(setup_func)
def test_count_after_insert(key):
    dataset = "test"
    data = redlink.create_data_client(key)
    assert_true(data.status["accessible"])
    assert_true(dataset in data.status["datasets"])

    results = data.sparql_tuple_query("select (count(*) as ?count) where { ?s ?p ?o }", dataset)
    assert_equals(1, len(results["results"]["bindings"]))
    size_before = int(results["results"]["bindings"][0]["count"]["value"])

    rnd = random_string()
    assert_true(data.import_dataset(
        "<http://example.org/%s> <http://example.org/label> '%s' ." % (rnd, rnd), Format.NT.mimetype, dataset))
    results = data.sparql_tuple_query("select (count(*) as ?count) where { ?s ?p ?o }", dataset)
    assert_equals(1, len(results["results"]["bindings"]))
    size_after = int(results["results"]["bindings"][0]["count"]["value"])
    assert_equals(size_before + 1, size_after)


@with_setup_args(setup_func)
def test_size_sparql_and_export(key):
    dataset = "test"
    data = redlink.create_data_client(key)
    assert_true(data.status["accessible"])
    assert_true(dataset in data.status["datasets"])

    results = data.sparql_tuple_query("select (count(*) as ?count) where { ?s ?p ?o }", dataset)
    assert_equals(1, len(results["results"]["bindings"]))
    size_sparql = int(results["results"]["bindings"][0]["count"]["value"])

    graph = data.export_dataset(dataset)
    size_export = len(graph)

    assert_equals(size_sparql, size_export)


@with_setup_args(setup_func)
def test_clean_before_insert(key):
    dataset = "test"
    data = redlink.create_data_client(key)
    assert_true(data.status["accessible"])
    assert_true(dataset in data.status["datasets"])

    assert_true(data.import_dataset(
        "<http://example.org/foo> <http://example.org/label> 'foo' .", Format.NT.mimetype, dataset, True))
    graph = data.export_dataset(dataset)
    assert_equals(1, len(graph))
