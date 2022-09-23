#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from datetime import date

from owlready2 import *

from config import KNOWLEDGE_GRAPH_FILE, ONTOLOGY_PREFIX
from connection_controller import ConnectionController


class OntologyInstanceGenerator:
    """
    Facilitates ontology instance generation based on on-board diagnosis information.

    Enhances the knowledge graph with vehicle-specific instance data.

    TODO: not yet clear whether this is still useful
        - based on the current state, we won't use live DB access
        - thus, the ontology instances are created 'manually' by experts (at least initially)
    """

    def __init__(self, vehicle, hsn, tsn, vin, dtc, ontology_path, local_kb=False):
        self.vehicle = vehicle
        self.hsn = hsn
        self.tsn = tsn
        self.vin = vin
        self.dtc = dtc

        self.local_kb = local_kb

        if self.local_kb:
            # load ontology
            onto_path.append(ontology_path)
            self.onto = get_ontology(KNOWLEDGE_GRAPH_FILE)
            self.onto.load()
        else:
            # establish connection to Apache Jena Fuseki server
            self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)

    def create_ontology_instance(self):
        """
        Creates an OBD ontology instance based on the present vehicle information and performs a consistency check.
        """
        self.add_vehicle()
        self.check_consistency_and_save_to_file()

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

    def add_vehicle(self):
        fault_condition = list(self.dtc_obj.represents)[0]
        vehicle = self.onto.Vehicle()
        vehicle.model.append(self.vehicle)
        vehicle.HSN.append(self.hsn)
        vehicle.TSN.append(self.tsn)
        vehicle.VIN.append(self.vin)
        fault_condition.occurredIn.append(vehicle)


if __name__ == '__main__':
    instance_gen = OntologyInstanceGenerator(
        "Mazda 3", "847984", "45539", "1234567890ABCDEFGHJKLMNPRSTUVWXYZ", "P1111", "."
    )
    instance_gen.create_ontology_instance()
