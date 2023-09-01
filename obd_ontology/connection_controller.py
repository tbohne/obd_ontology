#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import re
from typing import List, Dict, Union

import requests
from rdflib import Namespace, RDF, Literal, Graph, URIRef
from termcolor import colored

from obd_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL, SPARQL_ENDPOINT, DATA_ENDPOINT, UPDATE_ENDPOINT
from obd_ontology.fact import Fact


class ConnectionController:
    """
    Establishes the connection to the knowledge graph hosted by the 'Apache Jena Fuseki' server.
    Performs queries as well as knowledge graph extensions via HTTP requests.
    """

    def __init__(self, namespace: str, fuseki_url: str = FUSEKI_URL) -> None:
        """
        Initializes the connection controller.

        :param namespace: ontology namespace (prefix URI)
        :param fuseki_url: URL of the 'Fuseki' server hosting the knowledge graph
        """
        self.namespace = Namespace(namespace)
        self.fuseki_url = fuseki_url
        self.graph = Graph()
        self.graph.bind("", self.namespace)

    def query_knowledge_graph(self, query: str, verbose: bool) -> List[Dict[Dict[str]]]:
        """
        Sends an HTTP request containing the specified query to the knowledge graph server.

        :param query: query to be sent to knowledge graph server
        :param verbose: if true, queries are logged
        :return: query results (JSON list)
        """
        if verbose:
            print("query knowledge graph..")
            print(query)
        res = requests.post(self.fuseki_url + SPARQL_ENDPOINT, query.encode(),
                            headers={'Content-Type': 'application/sparql-query', 'Accept': 'application/json'})
        if res.status_code != 200:
            print("HTTP status code:", res.status_code)
        return res.json()["results"]["bindings"]

    def extend_knowledge_graph(self, facts: List[Fact]) -> None:
        """
        Sends an HTTP request containing the facts to be entered into the knowledge graph to the knowledge graph server.

        :param facts: facts to be entered into the knowledge graph
        """
        print(colored("\nextending knowledge graph..", "green", "on_grey", ["bold"]))
        graph = Graph()
        for fact in facts:
            # for very long facts, only print the first segment (e.g. heatmaps)
            print("fact:", str(fact)[:200] + "..." if len(str(fact)) > 0 else fact)
            if fact.property_fact:
                graph.add((self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), Literal(fact.triple[2])))
            else:
                graph.add((self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), self.get_uri(fact.triple[2])))

        res = requests.post(self.fuseki_url + DATA_ENDPOINT, data=graph.serialize(format="ttl").encode(),
                            headers={'Content-Type': 'text/turtle'})
        if res.status_code != 200:
            print("HTTP status code:", res.status_code)

    def remove_outdated_facts_from_knowledge_graph(self, facts: List[Fact]) -> None:
        """
        Sends an HTTP request containing the facts to be removed from the knowledge graph.

        :param facts: facts to be removed from the knowledge graph
        """
        print(colored("\nremoving facts from knowledge graph..", "green", "on_grey", ["bold"]))
        for fact in facts:
            print("fact:", fact)
            if fact.property_fact:
                f = (self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), Literal(fact.triple[2]))
                # TODO: check for better ways to handle these special cases
                if "<http://www.w3.org/2001/XMLSchema#boolean>" in f[2]:
                    query = f"DELETE DATA {{ <{f[0]}> <{f[1]}> {f[2]} . }}"
                else:
                    query = f"DELETE DATA {{ <{f[0]}> <{f[1]}> \"{f[2]}\" . }}"
            else:
                f = (self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), self.get_uri(fact.triple[2]))
                query = f"DELETE DATA {{ <{f[0]}> <{f[1]}> <{f[2]}> . }}"
            print("*** DELETION QUERY:", query)
            res = requests.post(
                self.fuseki_url + UPDATE_ENDPOINT,
                data=query.encode(),
                headers={'Content-Type': 'application/sparql-update'}
            )
            if res.status_code != 200 and res.status_code != 204:
                print("HTTP status code:", res.status_code)

    def get_uri(self, triple_ele: str) -> Union[URIRef, str]:
        """
        Returns the specified triple element as feasible URI reference.

        :param triple_ele: triple element to get URI reference for
        :return: URI reference for triple element
        """
        if re.match("(http|https)://([\w_-]+(?:\.[\w_-]+)+)([\w.,@?^=%&:/~+]*[\w@?^=%&/~+])", triple_ele):
            return URIRef(triple_ele)
        elif triple_ele == "http://www.w3.org/1999/02/22-rdf-syntax-ns#type":
            return triple_ele
        else:
            return URIRef(self.namespace[triple_ele])


if __name__ == '__main__':
    connection = ConnectionController(ONTOLOGY_PREFIX)
    # query example
    q = "SELECT ?s ?p ?o WHERE { ?s ?p ?o } LIMIT 25"
    response = connection.query_knowledge_graph(q, True)
    print(response)
    # extension example
    onto_namespace = Namespace(ONTOLOGY_PREFIX)
    fact_list = [
        Fact(('car_1', RDF.type, onto_namespace["Vehicle"].toPython())),
        Fact(("car_1", onto_namespace.model, 'Mazda3'), property_fact=True),
        Fact(("car_1", onto_namespace.HSN, '847984'), property_fact=True),
        Fact(("car_1", onto_namespace.TSN, '45539'), property_fact=True),
        Fact(("car_1", onto_namespace.VIN, '2342813'), property_fact=True)
    ]
    connection.extend_knowledge_graph(fact_list)
