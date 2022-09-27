#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from datetime import date

from owlready2 import *
from rdflib import Namespace, RDF

from config import KNOWLEDGE_GRAPH_FILE, ONTOLOGY_PREFIX
from connection_controller import ConnectionController
from fact import Fact
from knowledge_graph_query_tool import KnowledgeGraphQueryTool


class OntologyInstanceGenerator:
    """
    Enhances the knowledge graph with vehicle-specific instance data. Connects the on-board diagnosis data recorded in
    a particular car with corresponding background knowledge stored in the knowledge graph.
    E.g.: A particular DTC is recorded in a car:
        - vehicle is added to knowledge graph (with all its properties)
        - vehicle is connected to knowledge about the particular DTC (symptoms etc.) via the `occurredIn` relation
    """

    def __init__(self, ontology_path, local_kb=False):
        self.local_kb = local_kb

        if self.local_kb:
            # load ontology
            onto_path.append(ontology_path)
            self.onto = get_ontology(KNOWLEDGE_GRAPH_FILE)
            self.onto.load()
        else:
            # establish connection to Apache Jena Fuseki server
            self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)
            self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(local_kb=False)

    def extend_knowledge_graph(self, model, hsn, tsn, vin, dtc):
        """
        Extends the knowledge graph based on the present vehicle information and performs a consistency check.

        :param model: model of the specified car
        :param hsn: manufacturer key ("Herstellerschlüsselnummer")
        :param tsn:  type number ("Typschlüsselnummer")
        :param vin: vehicle identification number
        :param dtc: specified diagnostic trouble code
        """
        if self.local_kb:
            # TODO: to be implemented..
            pass
            # fault_condition = list(self.dtc_obj.represents)[0]
            # vehicle = self.onto.Vehicle()
            # vehicle.model.append(self.model)
            # vehicle.HSN.append(self.hsn)
            # vehicle.TSN.append(self.tsn)
            # vehicle.VIN.append(self.vin)
            # fault_condition.occurredIn.append(vehicle)
            # self.check_consistency_and_save_to_file()
        else:
            onto_namespace = Namespace(ONTOLOGY_PREFIX)
            # identifier of the FaultCondition instance in the knowledge graph corresponding to the specified code
            fault_condition_id = self.knowledge_graph_query_tool.query_fault_condition_instance_by_code(dtc)[0].split("#")[1]
            vehicle_uuid = "vehicle_" + str(uuid.uuid4())

            fact_list = [
                Fact((vehicle_uuid, RDF.type, onto_namespace["Vehicle"].toPython())),
                Fact((vehicle_uuid, onto_namespace.model, model), property_fact=True),
                Fact((vehicle_uuid, onto_namespace.HSN, hsn), property_fact=True),
                Fact((vehicle_uuid, onto_namespace.TSN, tsn), property_fact=True),
                Fact((vehicle_uuid, onto_namespace.VIN, vin), property_fact=True),
                Fact((fault_condition_id, onto_namespace.occurredIn, vehicle_uuid))
            ]
            self.fuseki_connection.extend_knowledge_graph(fact_list)

    def check_consistency_and_save_to_file(self):
        """
        Checks the consistency of the generated ontology instance and saves it to file.
        """
        with self.onto:
            try:
                sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True, debug=2)
            except owlready2.base.OwlReadyInconsistentOntologyError as e:
                print("### reasoner determined inconsistency ###")
                print(list(default_world.inconsistent_classes()))
                print("-->", e)

        file = "ontology_instance_{}_{}_{}_{}.owl".format(self.hsn, self.tsn, self.vin, date.today())
        self.onto.save(file)


if __name__ == '__main__':
    instance_gen = OntologyInstanceGenerator(".", local_kb=False)
    instance_gen.extend_knowledge_graph("Mazda 3", "847984", "45539", "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", "P2563")
