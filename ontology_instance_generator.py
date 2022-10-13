#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from datetime import date

from OBDOntology.config import KNOWLEDGE_GRAPH_FILE, ONTOLOGY_PREFIX
from OBDOntology.connection_controller import ConnectionController
from OBDOntology.fact import Fact
from OBDOntology.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from owlready2 import *
from rdflib import Namespace, RDF


class OntologyInstanceGenerator:
    """
    Enhances the knowledge graph with vehicle-specific instance data. Connects the on-board diagnosis data recorded in
    a particular car with corresponding background knowledge stored in the knowledge graph.
    E.g.: A particular DTC is recorded in a car:
        - vehicle is added to knowledge graph (with all its properties)
        - vehicle is connected to knowledge about the particular DTC (symptoms etc.) via the `occurredIn` relation
    """

    def __init__(self, ontology_path: str, local_kb=False) -> None:
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

    def extend_knowledge_graph(self, model: str, hsn: str, tsn: str, vin: str, dtc: str) -> None:
        """
        Extends the knowledge graph based on the present vehicle information and performs a consistency check.

        :param model: model of the specified car
        :param hsn: manufacturer key ("Herstellerschlüsselnummer")
        :param tsn:  type number ("Typschlüsselnummer")
        :param vin: vehicle identification number
        :param dtc: specified diagnostic trouble code
        """
        if self.local_kb:
            dtc_obj = self.onto.DTC()
            fault_condition = list(dtc_obj.represents)[0]
            vehicle = self.onto.Vehicle()
            vehicle.model.append(model)
            vehicle.HSN.append(hsn)
            vehicle.TSN.append(tsn)
            vehicle.VIN.append(vin)
            fault_condition.occurredIn.append(vehicle)
            self.check_consistency_and_save_to_file(hsn, tsn, vin)
        else:
            onto_namespace = Namespace(ONTOLOGY_PREFIX)

            fault_condition_instance = self.knowledge_graph_query_tool.query_fault_condition_instance_by_code(dtc)
            fault_condition_id = ""
            if len(fault_condition_instance) > 0:
                # identifier of the FaultCondition instance in the knowledge graph corresponding to the specified code
                fault_condition_id = fault_condition_instance[0].split("#")[1]
            else:
                print("Presented fault condition (" + dtc + ") not yet part of KG -- should be entered in advance")

            vehicle_uuid = "vehicle_" + str(uuid.uuid4())
            fact_list = []
            vehicle_instance = self.knowledge_graph_query_tool.query_vehicle_instance_by_vin(vin)
            if len(vehicle_instance) > 0:
                print("Vehicle (" + vin + ") already part of the KG")
                vehicle_uuid = vehicle_instance[0].split("#")[1]
            else:
                fact_list = [
                    Fact((vehicle_uuid, RDF.type, onto_namespace["Vehicle"].toPython())),
                    Fact((vehicle_uuid, onto_namespace.model, model), property_fact=True),
                    Fact((vehicle_uuid, onto_namespace.HSN, hsn), property_fact=True),
                    Fact((vehicle_uuid, onto_namespace.TSN, tsn), property_fact=True),
                    Fact((vehicle_uuid, onto_namespace.VIN, vin), property_fact=True)
                ]
            # the "occurred in" relation should be entered either way (if the fault condition is part of the KG)
            if fault_condition_id != "":
                fact_list.append(Fact((fault_condition_id, onto_namespace.occurredIn, vehicle_uuid)))

            self.fuseki_connection.extend_knowledge_graph(fact_list)

    def check_consistency_and_save_to_file(self, hsn, tsn, vin) -> None:
        """
        Checks the consistency of the generated ontology instance and saves it to file.

        :param hsn: manufacturer key ("Herstellerschlüsselnummer")
        :param tsn: type number ("Typschlüsselnummer")
        :param vin: vehicle identification number
        """
        with self.onto:
            try:
                sync_reasoner_pellet(infer_property_values=True, infer_data_property_values=True, debug=2)
            except owlready2.base.OwlReadyInconsistentOntologyError as e:
                print("### reasoner determined inconsistency ###")
                print(list(default_world.inconsistent_classes()))
                print("-->", e)

        file = "ontology_instance_{}_{}_{}_{}.owl".format(hsn, tsn, vin, date.today())
        self.onto.save(file)


if __name__ == '__main__':
    instance_gen = OntologyInstanceGenerator(".", local_kb=False)
    instance_gen.extend_knowledge_graph("Mazda 3", "847984", "45539", "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", "P2563")
