#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import re

import requests
from obd_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL, SPARQL_ENDPOINT, DATA_ENDPOINT, UPDATE_ENDPOINT
from obd_ontology.fact import Fact
from rdflib import Namespace, RDF, Literal, Graph, URIRef
from termcolor import colored


class ConnectionController:
    """
    Establishes the connection to the knowledge graph hosted by the Apache Jena Fuseki server.
    Performs queries as well as knowledge graph extensions via HTTP requests.
    """

    def __init__(self, namespace: str, fuseki_url=FUSEKI_URL) -> None:
        self.namespace = Namespace(namespace)
        self.fuseki_url = fuseki_url
        self.graph = Graph()
        self.graph.bind("", self.namespace)

    def query_knowledge_graph(self, query: str, verbose: bool) -> list:
        """
        Sends an HTTP request containing the specified query to the knowledge graph server.

        :param query: query to be sent to knowledge graph server
        :param verbose: if true, queries are logged
        :return: query results
        """
        if verbose:
            print("query knowledge graph..")
            print(query)
        res = requests.post(self.fuseki_url + SPARQL_ENDPOINT, query.encode(),
                            headers={'Content-Type': 'application/sparql-query', 'Accept': 'application/json'})
        if res.status_code != 200:
            print("HTTP status code:", res.status_code)
        return res.json()["results"]["bindings"]

    def extend_knowledge_graph(self, facts: list) -> None:
        """
        Sends an HTTP request containing the facts to be entered into the knowledge graph to the knowledge graph server.

        :param facts: facts to be entered into the knowledge graph
        """
        print(colored("\nextending knowledge graph..", "green", "on_grey", ["bold"]))
        graph = Graph()
        for fact in facts:
            print("fact:", fact)
            if fact.property_fact:
                graph.add((self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), Literal(fact.triple[2])))
            else:
                graph.add((self.get_uri(fact.triple[0]), self.get_uri(fact.triple[1]), self.get_uri(fact.triple[2])))

        res = requests.post(self.fuseki_url + DATA_ENDPOINT, data=graph.serialize(format="ttl").encode(),
                            headers={'Content-Type': 'text/turtle'})
        if res.status_code != 200:
            print("HTTP status code:", res.status_code)

    def generate_condition_description_fact(self, fc_uuid: str, fault_cond: str, prop: bool) -> Fact:
        """
        Generates a `condition_description` fact (RDF) based on the provided properties.

        :param fc_uuid: UUID of the fault condition instance to generate fact for
        :param fault_cond: the fault condition description
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((fc_uuid, self.namespace.condition_description, fault_cond), property_fact=prop)

    def generate_co_occurring_dtc_fact(self, dtc_uuid: str, code: str, prop: bool) -> Fact:
        """
        Generates an `occurs_with_DTC` fact (RDF) based on the provided properties.

        :param dtc_uuid: UUID of the DTC to generate fact for
        :param code: code of the co-occurring DTC
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((dtc_uuid, self.namespace.occurs_with_DTC, code), property_fact=prop)

    def generate_symptom_fact(self, fc_uuid: str, symptom_uuid: str, prop: bool) -> Fact:
        """
        Generates a `manifestedBy` fact (RDF) based on the provided properties.

        :param fc_uuid: UUID of the fault condition to generate the fact for
        :param symptom_uuid: UUID of the symptom to generate the fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((fc_uuid, self.namespace.manifestedBy, symptom_uuid), property_fact=prop)

    def generate_has_fact(self, dtc_uuid: str, da_uuid: str, prop: bool) -> Fact:
        """
        Generates a `has` fact (RDF) based on the provided properties.

        :param dtc_uuid: UUID of the DTC to generate fact for
        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((dtc_uuid, self.namespace.has, da_uuid), property_fact=prop)

    def generate_points_to_fact(self, da_uuid: str, comp_uuid: str, prop: bool) -> Fact:
        """
        Generates a `pointsTo` fact (RDF) based on the provided properties.

        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param comp_uuid: UUID of the suspect component to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((da_uuid, self.namespace.pointsTo, comp_uuid), property_fact=prop)

    def generate_diagnostic_association_fact(self, da_uuid: str, prop: bool) -> Fact:
        """
        Generates a `DiagnosticAssociation` fact (RDF) based on the provided properties.

        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact(
            (da_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", self.namespace.DiagnosticAssociation),
            property_fact=prop
        )

    def generate_contains_fact(self, subsystem_uuid: str, comp_uuid: str, prop: bool) -> Fact:
        """
        Generates a `contains` fact (RDF) based on the provided properties.

        :param subsystem_uuid: UUID of the subsystem to generate fact for
        :param comp_uuid: UUID of the suspect component to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((subsystem_uuid, self.namespace.contains, comp_uuid), property_fact=prop)

    def generate_verifies_fact(self, comp_uuid: str, subsystem_uuid: str, prop: bool) -> Fact:
        """
        Generates a `verifies` fact (RDF) based on the provided properties.

        :param comp_uuid: UUID of the component to generate fact for
        :param subsystem_uuid: UUID of the subsystem to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((comp_uuid, self.namespace.verifies, subsystem_uuid), property_fact=prop)

    def generate_use_oscilloscope_fact(self, comp_uuid: str, osci_usage: bool, prop: bool) -> Fact:
        """
        Generates a `use_oscilloscope` fact (RDF) based on the provided properties.

        :param comp_uuid: UUID of the component to generate fact for
        :param osci_usage: oscilloscope usage value (literal)
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((comp_uuid, self.namespace.use_oscilloscope, osci_usage), property_fact=prop)

    def remove_outdated_facts_from_knowledge_graph(self, facts: list) -> None:
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

            print("******************************************** DELETION QUERY:", query)

            res = requests.post(
                self.fuseki_url + UPDATE_ENDPOINT, data=query, headers={'Content-Type': 'application/sparql-update'}
            )
            if res.status_code != 200 and res.status_code != 204:
                print("HTTP status code:", res.status_code)

    def get_uri(self, triple_ele: str) -> URIRef:
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
        Fact(("car_1", onto_namespace.VIN, '1234567890ABCDEFGHJKLMNPRSTUVWXYZ'), property_fact=True),
        Fact(("OWLNamedIndividual_181b81a8_3e76_4ab8_bee8_33d7508ac04a", onto_namespace.occurredIn, 'car_1'))
    ]
    connection.extend_knowledge_graph(fact_list)
