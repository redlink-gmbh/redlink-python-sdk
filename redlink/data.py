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

    def importDataset(self, data, mimetype, dataset):
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

    def exportDataset(self, dataset):
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

