#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import requests
from rdflib import Graph

from config import ONTOLOGY_PREFIX, FUSEKI_URL


class ConnectionController:

    def __init__(self, namespace, fuseki_url=FUSEKI_URL) -> None:
        self.namespace = namespace
        self.fuseki_url = fuseki_url
        self.graph = Graph()
        self.graph.bind("", self.namespace)

    def query_knowledge_graph(self, query: str):
        print("query knowledge graph..")
        print(query)
        res = requests.post(self.fuseki_url + "/OBD/sparql", query,
                            headers={'Content-Type': 'application/sparql-query', 'Accept': 'application/json'})
        return res.json()["results"]["bindings"]


if __name__ == '__main__':
    connection = ConnectionController(ONTOLOGY_PREFIX)

    q = """
        SELECT ?s ?p ?o
        WHERE {
            ?s ?p ?o
        }
        LIMIT 25
        """
    response = connection.query_knowledge_graph(q)
    print("number of res:", len(response))
    print("RES:")
    print(response)
