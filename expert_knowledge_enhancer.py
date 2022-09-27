#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import Tuple

from dtc_parser.parser import DTCParser
from rdflib import Namespace, RDF

from config import ONTOLOGY_PREFIX
from connection_controller import ConnectionController
from expert_knowledge_parser import ExpertKnowledgeParser
from fact import Fact


class ExpertKnowledgeEnhancer:
    """
    Extends the knowledge graph hosted by the Fuseki server with vehicle-agnostic OBD knowledge (codes, symptoms, etc.)
    provided in the form of `templates/expert_knowledge_template.txt`.
    """

    def __init__(self, knowledge_file: str) -> None:
        self.knowledge_parser = ExpertKnowledgeParser(knowledge_file)
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)

    def generate_dtc_facts(self) -> Tuple[str, list]:
        """
        Generates the DTC-related facts to be entered into the knowledge graph.

        :return: [DTC UUID, generated fact list]
        """
        dtc_uuid = "dtc_" + uuid.uuid4().hex
        fact_list = [
            Fact((dtc_uuid, RDF.type, self.onto_namespace["DTC"].toPython())),
            Fact((dtc_uuid, self.onto_namespace.code, self.knowledge_parser.dtc), property_fact=True)
        ]
        for code in self.knowledge_parser.occurs_with:
            fact_list.append(Fact((dtc_uuid, self.onto_namespace.occurs_with_DTC, code), property_fact=True))
        return dtc_uuid, fact_list

    def generate_fault_cat_facts(self, dtc_uuid: str) -> Tuple[str, list]:
        """
        Generates the FaultCategory-related facts to be entered into the knowledge graph.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :return: [fault category UUID, generated fact list]
        """
        fault_cat_uuid = "fault_cat_" + uuid.uuid4().hex
        dtc_parser = DTCParser()
        category_name = dtc_parser.parse_code_machine_readable(self.knowledge_parser.dtc)
        fact_list = [
            Fact((fault_cat_uuid, RDF.type, self.onto_namespace["FaultCategory"].toPython())),
            Fact((fault_cat_uuid, self.onto_namespace.category_name, category_name), property_fact=True),
            Fact((dtc_uuid, self.onto_namespace.hasCategory, fault_cat_uuid))
        ]
        return fault_cat_uuid, fact_list

    def generate_fault_cond_facts(self, dtc_uuid: str) -> Tuple[str, list]:
        """
        Generates the FaultCondition-related facts to be entered into the knowledge graph.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :return: [fault condition UUID, generated fact list]
        """
        fault_cond_uuid = "fault_cond_" + uuid.uuid4().hex
        fact_list = [
            Fact((fault_cond_uuid, RDF.type, self.onto_namespace["FaultCondition"].toPython())),
            Fact((fault_cond_uuid, self.onto_namespace.condition_description, self.knowledge_parser.fault_condition),
                 property_fact=True),
            Fact((dtc_uuid, self.onto_namespace.represents, fault_cond_uuid))
        ]
        return fault_cond_uuid, fact_list

    def generate_symptom_facts(self, fault_cond_uuid: str) -> list:
        """
        Generates the Symptom-related facts to be entered into the knowledge graph.

        :param fault_cond_uuid: FaultCondition UUID used to draw the connection to a fault condition
        :return: generated fact list
        """
        fact_list = []
        # there can be more than one symptom instance per DTC
        for symptom in self.knowledge_parser.symptoms:
            symptom_uuid = "symptom_" + uuid.uuid4().hex
            fact_list.append(Fact((symptom_uuid, RDF.type, self.onto_namespace["Symptom"].toPython())))
            fact_list.append(Fact((symptom_uuid, self.onto_namespace.symptom_description, symptom), property_fact=True))
            fact_list.append(Fact((fault_cond_uuid, self.onto_namespace.manifestedBy, symptom_uuid)))
        return fact_list

    def generate_suspect_component_facts(self, dtc_uuid: str) -> list:
        """
        Generates the SuspectComponent-related facts to be entered into the knowledge graph.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :return: generated fact list
        """
        fact_list = []
        # there can be more than one suspect component instance per DTC
        for idx, comp in enumerate(self.knowledge_parser.suspect_components):
            comp_name, use_oscilloscope = comp.split(" (")
            comp_name = comp_name.strip()
            use_oscilloscope = use_oscilloscope.replace(")", "").strip()
            use_oscilloscope = True if "ja" in use_oscilloscope.lower() else False

            comp_uuid = "comp_" + uuid.uuid4().hex
            fact_list.append(Fact((comp_uuid, RDF.type, self.onto_namespace["SuspectComponent"].toPython())))
            fact_list.append(Fact((comp_uuid, self.onto_namespace.component_name, comp_name), property_fact=True))
            fact_list.append(Fact((comp_uuid, self.onto_namespace.priority_id, idx), property_fact=True))
            fact_list.append(
                Fact((comp_uuid, self.onto_namespace.use_oscilloscope, use_oscilloscope), property_fact=True))
            fact_list.append(Fact((dtc_uuid, self.onto_namespace.pointsTo, comp_uuid)))
        return fact_list

    def extend_knowledge_graph(self) -> None:
        """
        Parses the expert knowledge from the specified file and extends the knowledge graph with it.
        """
        self.knowledge_parser.parse_knowledge()
        print("parsed expert knowledge..")
        print(self.knowledge_parser)

        dtc_uuid, dtc_facts = self.generate_dtc_facts()
        _, fault_cat_facts = self.generate_fault_cat_facts(dtc_uuid)
        fault_cond_uuid, fault_cond_facts = self.generate_fault_cond_facts(dtc_uuid)
        symptom_facts = self.generate_symptom_facts(fault_cond_uuid)
        suspect_comp_facts = self.generate_suspect_component_facts(dtc_uuid)

        fact_list = dtc_facts + fault_cat_facts + fault_cond_facts + symptom_facts + suspect_comp_facts
        self.fuseki_connection.extend_knowledge_graph(fact_list)


if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer("templates/dummy.txt")
    expert_knowledge_enhancer.extend_knowledge_graph()
