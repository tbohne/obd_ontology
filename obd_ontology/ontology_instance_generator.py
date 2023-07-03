#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from datetime import date
from typing import List

from owlready2 import *
from rdflib import Namespace, RDF

from obd_ontology.config import KNOWLEDGE_GRAPH_FILE, ONTOLOGY_PREFIX, FUSEKI_URL
from obd_ontology.connection_controller import ConnectionController
from obd_ontology.fact import Fact
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


class OntologyInstanceGenerator:
    """
    Enhances the knowledge graph with vehicle- and diagnosis-specific instance data. Connects the on-board diagnosis
    data recorded in a particular car with corresponding background knowledge stored in the knowledge graph.
    E.g.: A particular DTC is recorded in a car:
        - vehicle is added to knowledge graph (with all its properties)
        - vehicle is connected to knowledge about the particular DTC (symptoms etc.) via the DiagLog
    """

    def __init__(self, ontology_path: str, local_kb: bool = False, kg_url: str = FUSEKI_URL) -> None:
        self.local_kb = local_kb

        if self.local_kb:
            # load ontology
            onto_path.append(ontology_path)
            self.onto = get_ontology(KNOWLEDGE_GRAPH_FILE)
            self.onto.load()
        else:
            # establish connection to Apache Jena Fuseki server
            self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url)
            self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(local_kb=False, kg_url=kg_url)

    def extend_knowledge_graph_with_vehicle_data(
            self, model: str, hsn: str, tsn: str, vin: str, dtc: str, max_num_of_parallel_rec: int, diag_date: str
    ) -> None:
        """
        Extends the knowledge graph based on the present vehicle information and performs a consistency check.

        :param model: model of the specified car
        :param hsn: manufacturer key ("Herstellerschlüsselnummer")
        :param tsn:  type number ("Typschlüsselnummer")
        :param vin: vehicle identification number
        :param dtc: specified diagnostic trouble code
        :param max_num_of_parallel_rec: max number of parallel recordings based on workshop equipment
        :param diag_date: date of the diagnosis
        """
        if self.local_kb:
            print("LOCAL KB NO LONGER SUPPORTED - USE FUSEKI SERVER INSTEAD")
        else:
            onto_namespace = Namespace(ONTOLOGY_PREFIX)

            fault_condition_instance = self.knowledge_graph_query_tool.query_fault_condition_instance_by_code(dtc)
            fault_condition_id = ""
            if len(fault_condition_instance) > 0:
                # identifier of the FaultCondition instance in the knowledge graph corresponding to the specified code
                fault_condition_id = fault_condition_instance[0].split("#")[1]
                fault_condition = self.knowledge_graph_query_tool.query_fault_condition_by_dtc(dtc)
                print("FAULT CONDITION:", fault_condition[0])
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
            # the connection to diag log should be entered either way (if the fault condition is part of the KG)
            if fault_condition_id != "":
                diag_log_uuid = "diag_log_" + str(uuid.uuid4())
                fact_list.append(Fact((diag_log_uuid, RDF.type, onto_namespace["DiagLog"].toPython())))
                fact_list.append(
                    Fact((diag_log_uuid, onto_namespace.max_num_of_parallel_rec, max_num_of_parallel_rec),
                         property_fact=True)
                )
                fact_list.append(Fact((diag_log_uuid, onto_namespace.date, diag_date), property_fact=True))
                dtc_id = self.knowledge_graph_query_tool.query_dtc_instance_by_code(dtc)[0].split("#")[1]
                fact_list.append(Fact((dtc_id, onto_namespace.appearsIn, diag_log_uuid)))
                fact_list.append(Fact((diag_log_uuid, onto_namespace.createdFor, vehicle_uuid)))
            self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_knowledge_graph_with_diag_log(
            self, diag_date: str, max_num_of_parallel_rec: int, dtc_instances: List[str],
            fault_path_instances: List[str], classification_instances: List[str], vehicle_id: str
    ) -> str:
        """
        Extends the knowledge graph with diagnosis log facts.

        :param diag_date: date of the diagnosis
        :param max_num_of_parallel_rec: max number of parallel recordings based on workshop equipment
        :param dtc_instances: DTC instances part of the diagnosis (stored in vehicle ECU)
        :param fault_path_instances: IDs of fault path instances part of the diagnosis
        :param classification_instances: IDs of classification instances part of the diagnosis
        :param vehicle_id: ID of the vehicle the diag log is created for
        :return ID of diagnosis log
        """
        onto_namespace = Namespace(ONTOLOGY_PREFIX)
        diag_log_uuid = "diag_log_" + uuid.uuid4().hex
        fact_list = [
            Fact((diag_log_uuid, RDF.type, onto_namespace["DiagLog"].toPython())),
            Fact((diag_log_uuid, onto_namespace.date, diag_date), property_fact=True),
            Fact((diag_log_uuid, onto_namespace.max_num_of_parallel_rec, max_num_of_parallel_rec), property_fact=True)
        ]
        for dtc in dtc_instances:
            dtc_uuid = self.knowledge_graph_query_tool.query_dtc_instance_by_code(dtc)
            if len(dtc_uuid) == 1:
                fact_list.append(
                    Fact((dtc_uuid[0].split("#")[1], onto_namespace.appearsIn, diag_log_uuid))
                )

        for fault_path_id in fault_path_instances:
            fact_list.append(Fact((diag_log_uuid, onto_namespace.entails, fault_path_id)))

        for classification_id in classification_instances:
            fact_list.append(Fact((classification_id, onto_namespace.diagStep, diag_log_uuid)))

        fact_list.append(Fact((diag_log_uuid, onto_namespace.createdFor, vehicle_id)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return diag_log_uuid

    def extend_knowledge_graph_with_fault_path(self, description: str, fault_cond_id: str) -> str:
        """
        Extends the knowledge graph with fault path facts.

        :param description: fault path description
        :param fault_cond_id: UUID of fault condition
        :return: fault path UUID
        """
        onto_namespace = Namespace(ONTOLOGY_PREFIX)
        fault_path_uuid = "fault_path_" + uuid.uuid4().hex
        fact_list = [
            Fact((fault_path_uuid, RDF.type, onto_namespace["FaultPath"].toPython())),
            Fact((fault_path_uuid, onto_namespace.path_description, description), property_fact=True),
            Fact((fault_cond_id, onto_namespace.resultedIn, fault_path_uuid))
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return fault_path_uuid

    def extend_knowledge_graph_with_oscillogram_classification(
            self, prediction: bool, classification_reason: str, comp_id: str, uncertainty: float, model_id: str,
            osci_id: str, heatmap_id: str
    ) -> str:
        """
        Extends the knowledge graph with oscillogram classification facts.

        :param prediction: prediction for the considered oscillogram (classification result)
        :param classification_reason: either a different classification or a diagnostic association
        :param comp_id: ID of the classified component
        :param uncertainty: uncertainty of the prediction
        :param model_id: ID of the used classification model
        :param osci_id: ID of the classified oscillogram
        :param heatmap_id: ID of the generated heatmap
        :return ID of oscillogram classification instance
        """
        # either ID of DA or ID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "oscillogram_classification_" in classification_reason

        onto_namespace = Namespace(ONTOLOGY_PREFIX)
        classification_uuid = "oscillogram_classification_" + uuid.uuid4().hex
        fact_list = [
            Fact((classification_uuid, RDF.type, onto_namespace["OscillogramClassification"].toPython())),
            # properties
            Fact((classification_uuid, onto_namespace.prediction, prediction), property_fact=True),
            Fact((classification_uuid, onto_namespace.uncertainty, uncertainty), property_fact=True),
            Fact((classification_uuid, onto_namespace.model_id, model_id), property_fact=True),
            # relations
            Fact((classification_uuid, onto_namespace.checks, comp_id)),
            Fact((classification_uuid, onto_namespace.classifies, osci_id)),
            Fact((classification_uuid, onto_namespace.produces, heatmap_id))
        ]
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, onto_namespace.ledTo, classification_uuid)))
        else:  # the reason is a classification instance (manual or osci)
            fact_list.append(Fact((classification_reason, onto_namespace.reasonFor, classification_uuid)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return classification_uuid

    def extend_knowledge_graph_with_heatmap(self, gen_method: str, heatmap: List[float]) -> str:
        """
        Extends the knowledge graph with heatmap facts.

        :param gen_method: used heatmap generation method, e.g. GradCAM
        :param heatmap: generated heatmap (values)
        :return: heatmap ID
        """
        onto_namespace = Namespace(ONTOLOGY_PREFIX)
        heatmap_uuid = "heatmap_" + uuid.uuid4().hex
        fact_list = [
            Fact((heatmap_uuid, RDF.type, onto_namespace["Heatmap"].toPython())),
            Fact((heatmap_uuid, onto_namespace.generation_method, gen_method), property_fact=True),
            Fact((heatmap_uuid, onto_namespace.generated_heatmap, str(heatmap)), property_fact=True)
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return heatmap_uuid

    def extend_knowledge_graph_with_oscillogram(self, time_series: List[float], parallel_rec_set_id: str = "") -> str:
        """
        Extends the knowledge graph with oscillogram facts.

        :param time_series: time series (voltage values), i.e., the oscillogram
        :param parallel_rec_set_id: optional ID of a set of parallel recordings this oscillogram should be assigned to
        :return: oscillogram ID
        """
        onto_namespace = Namespace(ONTOLOGY_PREFIX)
        osci_uuid = "oscillogram_" + uuid.uuid4().hex
        fact_list = [
            Fact((osci_uuid, RDF.type, onto_namespace["Oscillogram"].toPython())),
            Fact((osci_uuid, onto_namespace.time_series, str(time_series)), property_fact=True)
        ]
        if parallel_rec_set_id != "":  # oscillogram part of parallel recorded set?
            fact_list.append(Fact((osci_uuid, onto_namespace.partOf, parallel_rec_set_id)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return osci_uuid

    def extend_knowledge_graph_with_parallel_rec_osci_set(self) -> str:
        """
        Extends the knowledge graph with facts about a set of parallel recorded oscillograms.

        :return: oscillogram set ID
        """
        onto_namespace = Namespace(ONTOLOGY_PREFIX)
        osci_set_uuid = "parallel_rec_oscillogram_set_" + uuid.uuid4().hex
        fact_list = [Fact((osci_set_uuid, RDF.type, onto_namespace["ParallelRecOscillogramSet"].toPython()))]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return osci_set_uuid

    def extend_knowledge_graph_with_manual_inspection(
            self, prediction: bool, classification_reason: str, comp_id: str
    ) -> str:
        """
        Extends the knowledge graph with manual inspection facts.

        :param prediction: prediction for the considered component (classification result)
        :param classification_reason: either a different classification or a diagnostic association
        :param comp_id: ID of the classified component
        :return ID of manual inspection instance
        """
        # either ID of DA or ID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "oscillogram_classification_" in classification_reason

        onto_namespace = Namespace(ONTOLOGY_PREFIX)
        classification_uuid = "manual_inspection_" + uuid.uuid4().hex
        fact_list = [
            Fact((classification_uuid, RDF.type, onto_namespace["ManualInspection"].toPython())),
            Fact((classification_uuid, onto_namespace.prediction, prediction), property_fact=True),
            Fact((classification_uuid, onto_namespace.checks, comp_id))
        ]
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, onto_namespace.ledTo, classification_uuid)))
        else:  # the reason is a classification instance (manual or osci)
            fact_list.append(Fact((classification_reason, onto_namespace.reasonFor, classification_uuid)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return classification_uuid

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
    instance_gen.extend_knowledge_graph_with_vehicle_data(
        "Mazda 3", "847984", "45539", "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ", "P2563", 4, str(date.today())
    )
    # create some test instances
    causing_dtc = "P2563"
    fault_cond_uuid = instance_gen.knowledge_graph_query_tool.query_fault_condition_instance_by_code(
        causing_dtc)[0].split("#")[1]
    list_of_dtcs = ["P2563", "P0333", "P1234", "P0987"]
    fault_path = "VTG-Abgasturbolader -> Ladedruck-Magnetventil -> Ladedruck-Regelventil"
    osci_set_id = instance_gen.extend_knowledge_graph_with_parallel_rec_osci_set()
    oscillogram = [13.3, 13.6, 14.6, 16.7, 8.5, 9.7, 5.5, 3.6, 12.5, 12.7]
    heatmap = [0.4, 0.3, 0.7, 0.7, 0.8, 0.9, 0.3, 0.2]
    sus_comp = "VTG-Abgasturbolader"
    manual_sus_comp = "Ladedruck-Magnetventil"
    comp_id = instance_gen.knowledge_graph_query_tool.query_suspect_component_by_name(sus_comp)[0].split("#")[1]
    manual_sus_comp_id = instance_gen.knowledge_graph_query_tool.query_suspect_component_by_name(
        manual_sus_comp)[0].split("#")[1]
    osci_id = instance_gen.extend_knowledge_graph_with_oscillogram(oscillogram)
    heatmap_id = instance_gen.extend_knowledge_graph_with_heatmap("GradCAM", heatmap)
    fault_path_id = instance_gen.extend_knowledge_graph_with_fault_path(fault_path, fault_cond_uuid)

    classification_instances = [
        instance_gen.extend_knowledge_graph_with_oscillogram_classification(
            True, "diag_association_3592495", comp_id, 0.45, "test_model_id", osci_id, heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_oscillogram_classification(
            True, "oscillogram_classification_3543595", comp_id, 0.85, "test_model_id", osci_id, heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_manual_inspection(
            False, "oscillogram_classification_45395859345", manual_sus_comp_id
        )
    ]
    diag_log_uuid = instance_gen.extend_knowledge_graph_with_diag_log(
        "03.07.2023", 4, list_of_dtcs, [fault_path_id], classification_instances, "vehicle_39458359345382458"
    )
