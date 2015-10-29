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

import logging
from rdflib.graph import Graph
from SPARQLWrapper import SPARQLWrapper, JSON, POST, POSTDIRECTLY

from .client import RedlinkClient
from .format import from_mimetype, Format

class RedlinkData(RedlinkClient):

    path = "data"
    release_path = "release"
    resource_path = "resource"
    sparql_path = "sparql"
    sparql_select_path = "select"
    sparql_update_path = "update"
    ldpath_path = "ldpath"

    def __init__(self, key):
        super(RedlinkData, self).__init__(key)

    def release(self, dataset):
        resource = self._build_url("/%s/%s/%s" % (self.path, dataset, self.release_path))
        response = self._post(resource, accept="application/json")
        return 200 <= response.status_code < 300

    def import_dataset(self, data, mimetype, dataset):
        resource = self._build_url("/%s/%s" % (self.path, dataset))

        # TODO: do this in a more pythonic way
        if (data):
            rdf_format = from_mimetype(mimetype)
            if not rdf_format:
                rdf_format = Format.TURTLE

            if type(data) == str:
                payload = data
            elif type(data) == file:
                payload = data.read()
            elif type(data) == Graph:
                payload = data.serialize(format=rdf_format.rdflibMapping)
            else:
                raise ValueError("unsupported type %s as data payload" % type(data))
        else:
            payload = None

        response = self._post(resource, payload, contentType=rdf_format.mimetype)
        return 200 <= response.status_code < 300

    def export_dataset(self, dataset):
        resource = self._build_url("/%s/%s" % (self.path, dataset))
        rdf_format = Format.TURTLE
        response = self._get(resource, accept=rdf_format.mimetype)
        contentType = from_mimetype(response.headers["Content-Type"])
        if contentType.rdflibMapping:
            g = Graph()
            g.parse(data=response.text, format=contentType.rdflibMapping)
            return g
        else:
            logging.warn("Handler not found for parsing %s as RDF, so returning raw text response..." % contentType.mimetype)
            return response.text

    def sparql_tuple_query(self, query, dataset):
        return self._sparql_query(dataset, query, Format.JSON.name)

    def sparql_graph_query(self, query, dataset):
        return self._sparql_query(dataset, query, Format.TURTLE.name)

    def sparql_update(self, query, dataset):
        path = "/%s/%s/%s/%s" % (self.path, dataset, self.sparql_path, self.sparql_update_path)
        return self._sparql_query(path, query, Format.JSON.name)

    def _sparql_query(self, dataset, query, format=JSON):
        sparql_endpoint_select = "%s/%s/%s/%s/%s/%s" % (self.endpoint, self.version, self.path, dataset, self.sparql_path, self.sparql_select_path)
        sparql_endpoint_update = "%s/%s/%s/%s/%s/%s" % (self.endpoint, self.version, self.path, dataset, self.sparql_path, self.sparql_update_path)
        print sparql_endpoint_select
        print sparql_endpoint_update
        sparql = SPARQLWrapper(sparql_endpoint_select, sparql_endpoint_update)
        sparql.addCustomParameter(self.param_key, self.key)
        sparql.setMethod(POST)
        sparql.setRequestMethod(POSTDIRECTLY)
        sparql.setReturnFormat(format)
        sparql.setQuery(query)
        print sparql.isSparqlUpdateRequest()
        return sparql.query().convert()
