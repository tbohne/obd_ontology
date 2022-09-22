#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import re

import requests
from rdflib import Namespace, RDF, Literal, Graph, URIRef

from config import ONTOLOGY_PREFIX, FUSEKI_URL
from fact import Fact


class ConnectionController:

    def __init__(self, namespace, fuseki_url=FUSEKI_URL) -> None:
        self.namespace = Namespace(namespace)
        self.fuseki_url = fuseki_url
        self.graph = Graph()
        self.graph.bind("", self.namespace)

    def query_knowledge_graph(self, query: str):
        print("query knowledge graph..")
        print(query)
        res = requests.post(self.fuseki_url + "/OBD/sparql", query,
                            headers={'Content-Type': 'application/sparql-query', 'Accept': 'application/json'})
        if res.status_code != 200:
            print("HTTP status code:", res.status_code)
        return res.json()["results"]["bindings"]

    def extend_knowledge_graph(self, facts: list) -> None:
        print("extend knowledge graph..")
        graph = Graph()
        for fact in facts:
            print("fact:", fact)
            if fact.property_fact:
                graph.add((self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), Literal(fact.triple[2])))
            else:
                graph.add((self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), self.get_uri(fact.triple[2])))

        res = requests.post(self.fuseki_url + "/OBD/data", data=graph.serialize(format="ttl"),
                            headers={'Content-Type': 'text/turtle'})
        if res.status_code != 200:
            print("HTTP status code:", res.status_code)

    def get_uri(self, triple_ele: str) -> URIRef:
        if re.match("(http|https):\/\/([\w_-]+(?:(?:\.[\w_-]+)+))([\w.,@?^=%&:\/~+#-]*[\w@?^=%&\/~+#-])", triple_ele):
            return URIRef(triple_ele)
        else:
            return URIRef(self.namespace[triple_ele])


if __name__ == '__main__':
    connection = ConnectionController(ONTOLOGY_PREFIX)

    # q = """
    #     SELECT ?s ?p ?o
    #     WHERE {
    #         ?s ?p ?o
    #     }
    #     LIMIT 25
    #     """
    # response = connection.query_knowledge_graph(q)
    # print("number of res:", len(response))
    # print("RES:")
    # print(response)

    ########################################################

    onto_namespace = Namespace(ONTOLOGY_PREFIX)

    dummy_object = Fact(('car_1', RDF.type, onto_namespace["Vehicle"].toPython()))

    dummy_fact_0 = Fact(("car_1", onto_namespace.model, 'Mazda3'), property_fact=True)

    dummy_fact = Fact(("OWLNamedIndividual_181b81a8_3e76_4ab8_bee8_33d7508ac04a",
                       onto_namespace.occurredIn, 'car_1'))

    fact_list = [dummy_object, dummy_fact_0, dummy_fact]
    connection.extend_knowledge_graph(fact_list)
