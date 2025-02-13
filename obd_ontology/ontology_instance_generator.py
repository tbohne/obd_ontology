#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import List, Union

from owlready2 import *
from rdflib import Namespace, RDF

from obd_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL
from obd_ontology.connection_controller import ConnectionController
from obd_ontology.fact import Fact
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


class OntologyInstanceGenerator:
    """
    Enhances the KG with diagnosis-specific instance data, i.e., it connects the OBD data (model, HSN, TSN, VIN, DTCs)
    recorded in a particular vehicle, as well as sensor readings, classifications, etc. generated during the diagnostic
    process, with corresponding background knowledge stored in the KG.
    """

    def __init__(self, kg_url: str = FUSEKI_URL) -> None:
        """
        Initializes the ontology instance generator.

        :param kg_url: URL for the knowledge graph server
        """
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url)
        self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(kg_url=kg_url)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)

    def extend_knowledge_graph_with_vehicle_data(self, model: str, hsn: str, tsn: str, vin: str) -> None:
        """
        Extends the knowledge graph with semantic facts based on the present vehicle information.

        :param model: model of the specified car
        :param hsn: manufacturer key ("Herstellerschlüsselnummer")
        :param tsn: type number ("Typschlüsselnummer")
        :param vin: vehicle identification number
        """
        vehicle_uuid = "vehicle_" + str(uuid.uuid4())
        fact_list = []
        vehicle_instance = self.knowledge_graph_query_tool.query_vehicle_instance_by_vin(vin)
        if len(vehicle_instance) > 0:
            print("Vehicle (" + vin + ") already part of the KG")
        else:
            fact_list = [
                Fact((vehicle_uuid, RDF.type, self.onto_namespace["Vehicle"].toPython())),
                Fact((vehicle_uuid, self.onto_namespace.model, model), property_fact=True),
                Fact((vehicle_uuid, self.onto_namespace.HSN, hsn), property_fact=True),
                Fact((vehicle_uuid, self.onto_namespace.TSN, tsn), property_fact=True),
                Fact((vehicle_uuid, self.onto_namespace.VIN, vin), property_fact=True)
            ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_knowledge_graph_with_diag_log(
            self, diag_date: str, max_num_of_parallel_rec: int, dtc_instances: List[str],
            fault_path_instances: List[str], classification_instances: List[str], vehicle_id: str
    ) -> str:
        """
        Extends the knowledge graph with semantic facts for a diagnosis log.

        :param diag_date: date of the diagnosis
        :param max_num_of_parallel_rec: max number of parallel recordings based on workshop equipment
        :param dtc_instances: DTC instances part of the diagnosis (stored in vehicle ECU)
        :param fault_path_instances: IDs of fault path instances part of the diagnosis
        :param classification_instances: IDs of classification instances part of the diagnosis
        :param vehicle_id: ID of the vehicle the diag log is created for
        :return ID of diagnosis log
        """
        diag_log_uuid = "diag_log_" + uuid.uuid4().hex
        fact_list = [
            Fact((diag_log_uuid, RDF.type, self.onto_namespace["DiagLog"].toPython())),
            Fact((diag_log_uuid, self.onto_namespace.date, diag_date), property_fact=True),
            Fact((
                diag_log_uuid, self.onto_namespace.max_num_of_parallel_rec, max_num_of_parallel_rec), property_fact=True
            )
        ]
        for dtc in dtc_instances:
            dtc_uuid = self.knowledge_graph_query_tool.query_dtc_instance_by_code(dtc)
            if len(dtc_uuid) == 1:
                fact_list.append(
                    Fact((dtc_uuid[0].split("#")[1], self.onto_namespace.appearsIn, diag_log_uuid))
                )
        for fault_path_id in fault_path_instances:
            fact_list.append(Fact((diag_log_uuid, self.onto_namespace.entails, fault_path_id)))
        for classification_id in classification_instances:
            fact_list.append(Fact((classification_id, self.onto_namespace.diagStep, diag_log_uuid)))
        fact_list.append(Fact((diag_log_uuid, self.onto_namespace.createdFor, vehicle_id)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return diag_log_uuid

    def extend_knowledge_graph_with_fault_path(self, description: str, fault_cond_id: str) -> str:
        """
        Extends the knowledge graph with semantic facts for a fault path.

        :param description: fault path description
        :param fault_cond_id: UUID of fault condition
        :return: fault path UUID
        """
        fault_path_uuid = "fault_path_" + uuid.uuid4().hex
        fact_list = [
            Fact((fault_path_uuid, RDF.type, self.onto_namespace["FaultPath"].toPython())),
            Fact((fault_path_uuid, self.onto_namespace.path_description, description), property_fact=True),
            Fact((fault_cond_id, self.onto_namespace.resultedIn, fault_path_uuid))
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return fault_path_uuid

    def extend_knowledge_graph_with_oscillogram_classification(self, prediction: bool, classification_reason: str,
                                                               comp: str, uncertainty: float, model_id: str,
                                                               osci_ids: Union[str, List[str]],
                                                               heatmap_ids: Union[str, List[str]]) -> str:
        """
        Extends the knowledge graph with semantic facts for an oscillogram classification.

        :param prediction: prediction for the considered oscillogram (classification result)
        :param classification_reason: either a different classification or a diagnostic association
        :param comp: classified component
        :param uncertainty: uncertainty of the prediction
        :param model_id: ID of the used classification model
        :param osci_ids: ID(s) of the classified oscillogram(s)
        :param heatmap_ids: ID(s) of the generated heatmap(s)
        :return ID of oscillogram classification instance
        """
        # either ID of DA or ID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "oscillogram_classification_" in classification_reason
        comp_id = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]

        classification_uuid = "oscillogram_classification_" + uuid.uuid4().hex
        fact_list = [
            Fact((classification_uuid, RDF.type, self.onto_namespace["OscillogramClassification"].toPython())),
            # properties
            Fact((classification_uuid, self.onto_namespace.prediction, prediction), property_fact=True),
            Fact((classification_uuid, self.onto_namespace.uncertainty, uncertainty), property_fact=True),
            Fact((classification_uuid, self.onto_namespace.model_id, model_id), property_fact=True),
            # relations
            Fact((classification_uuid, self.onto_namespace.checks, comp_id))
        ]
        if isinstance(osci_ids, str):
            osci_ids = [osci_ids]
        if isinstance(heatmap_ids, str):
            heatmap_ids = [heatmap_ids]
        for osci_id in osci_ids:
            fact_list.append(Fact((classification_uuid, self.onto_namespace.classifies, osci_id)))
        for heatmap_id in heatmap_ids:
            fact_list.append(Fact((classification_uuid, self.onto_namespace.produces, heatmap_id)))
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, self.onto_namespace.ledTo, classification_uuid)))
        else:  # the reason is a classification instance (manual or osci)
            fact_list.append(Fact((classification_reason, self.onto_namespace.reasonFor, classification_uuid)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return classification_uuid

    def extend_knowledge_graph_with_heatmap(self, gen_method: str, heatmap: List[float]) -> str:
        """
        Extends the knowledge graph with semantic facts for a heatmap.

        :param gen_method: used heatmap generation method, e.g., GradCAM
        :param heatmap: generated heatmap (values)
        :return: heatmap ID
        """
        heatmap_uuid = "heatmap_" + uuid.uuid4().hex
        fact_list = [
            Fact((heatmap_uuid, RDF.type, self.onto_namespace["Heatmap"].toPython())),
            Fact((heatmap_uuid, self.onto_namespace.generation_method, gen_method), property_fact=True),
            Fact((heatmap_uuid, self.onto_namespace.generated_heatmap, str(heatmap)), property_fact=True)
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return heatmap_uuid

    def extend_knowledge_graph_with_oscillogram(self, time_series: List[float], parallel_rec_set_id: str = "") -> str:
        """
        Extends the knowledge graph with semantic facts for an oscillogram.

        :param time_series: time series (voltage values), i.e., the oscillogram
        :param parallel_rec_set_id: optional ID of a set of parallel recordings this oscillogram should be assigned to
        :return: oscillogram ID
        """
        osci_uuid = "oscillogram_" + uuid.uuid4().hex
        fact_list = [
            Fact((osci_uuid, RDF.type, self.onto_namespace["Oscillogram"].toPython())),
            Fact((osci_uuid, self.onto_namespace.time_series, str(time_series)), property_fact=True)
        ]
        if parallel_rec_set_id != "":  # oscillogram part of parallel recorded set?
            fact_list.append(Fact((osci_uuid, self.onto_namespace.partOf, parallel_rec_set_id)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return osci_uuid

    def extend_knowledge_graph_with_overlays_relation(self, heatmap_id: str, osci_id: str) -> None:
        """
        Extends the knowledge graph with the semantic fact about an "overlays" relation between a heatmap and an
        oscillogram.

        :param heatmap_id: ID of the heatmap that overlays the oscillogram
        :param osci_id: ID of the oscillogram
        """
        fact_list = [Fact((heatmap_id, self.onto_namespace.overlays, osci_id))]
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_knowledge_graph_with_parallel_rec_osci_set(self) -> str:
        """
        Extends the knowledge graph with semantic facts about a set of parallel recorded oscillograms.

        :return: oscillogram set ID
        """
        osci_set_uuid = "parallel_rec_oscillogram_set_" + uuid.uuid4().hex
        fact_list = [Fact((osci_set_uuid, RDF.type, self.onto_namespace["ParallelRecOscillogramSet"].toPython()))]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return osci_set_uuid

    def extend_knowledge_graph_with_manual_inspection(
            self, prediction: bool, classification_reason: str, comp: str
    ) -> str:
        """
        Extends the knowledge graph with semantic facts for a manual inspection.

        :param prediction: prediction for the considered component (classification result)
        :param classification_reason: either a different classification or a diagnostic association
        :param comp: classified component
        :return ID of manual inspection instance
        """
        # either ID of DA or ID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "oscillogram_classification_" in classification_reason

        comp_id = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]
        classification_uuid = "manual_inspection_" + uuid.uuid4().hex
        fact_list = [
            Fact((classification_uuid, RDF.type, self.onto_namespace["ManualInspection"].toPython())),
            Fact((classification_uuid, self.onto_namespace.prediction, prediction), property_fact=True),
            Fact((classification_uuid, self.onto_namespace.checks, comp_id))
        ]
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, self.onto_namespace.ledTo, classification_uuid)))
        else:  # the reason is a classification instance (manual or osci)
            fact_list.append(Fact((classification_reason, self.onto_namespace.reasonFor, classification_uuid)))
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return classification_uuid


if __name__ == '__main__':
    instance_gen = OntologyInstanceGenerator()
    instance_gen.extend_knowledge_graph_with_vehicle_data(
        "Mazda 3", "847984", "45539", "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    )
    # create some test instances
    causing_dtc = "P2563"
    fault_cond_uuid = instance_gen.knowledge_graph_query_tool.query_fault_condition_instance_by_code(
        causing_dtc)[0].split("#")[1]
    list_of_dtcs = ["P2563", "P0333", "P1234", "P0987"]
    fault_path = "VTG-Abgasturbolader -> Ladedruck-Magnetventil -> Ladedruck-Regelventil"
    osci_set_id = instance_gen.extend_knowledge_graph_with_parallel_rec_osci_set()
    oscillogram = [13.3, 13.6, 14.6, 16.7, 8.5, 9.7, 5.5, 3.6, 12.5, 12.7]
    test_heatmap = [0.4, 0.3, 0.7, 0.7, 0.8, 0.9, 0.3, 0.2]
    sus_comp = "VTG-Abgasturbolader"
    manual_sus_comp = "Ladedruck-Magnetventil"
    test_osci_id = instance_gen.extend_knowledge_graph_with_oscillogram(oscillogram)
    test_heatmap_id = instance_gen.extend_knowledge_graph_with_heatmap("GradCAM", test_heatmap)
    test_fault_path_id = instance_gen.extend_knowledge_graph_with_fault_path(fault_path, fault_cond_uuid)

    test_classification_instances = [
        instance_gen.extend_knowledge_graph_with_oscillogram_classification(
            True, "diag_association_3592495", sus_comp, 0.45, "test_model_id", test_osci_id, test_heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_oscillogram_classification(
            True, "oscillogram_classification_3543595", sus_comp, 0.85, "test_model_id", test_osci_id, test_heatmap_id
        ),
        instance_gen.extend_knowledge_graph_with_manual_inspection(
            False, "oscillogram_classification_45395859345", manual_sus_comp
        )
    ]
    log_uuid = instance_gen.extend_knowledge_graph_with_diag_log(
        "03.07.2023", 4, list_of_dtcs, [test_fault_path_id], test_classification_instances, "vehicle_39458359345382458"
    )
