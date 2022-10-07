#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import Tuple

from dtc_parser.parser import DTCParser
from rdflib import Namespace, RDF

import expert_knowledge_parser
from config import ONTOLOGY_PREFIX
from connection_controller import ConnectionController
from expert_knowledge_parser import DTCKnowledge, SubsystemKnowledge
from fact import Fact
from knowledge_graph_query_tool import KnowledgeGraphQueryTool


class ExpertKnowledgeEnhancer:
    """
    Extends the knowledge graph hosted by the Fuseki server with vehicle-agnostic OBD knowledge (codes, symptoms, etc.)
    provided in the form of `templates/dtc_expert_template.txt`, `templates/component_expert_template.txt`, and
    `templates/subsystem_expert_template.txt`.
    """

    def __init__(self, knowledge_file: str) -> None:
        self.knowledge_file = knowledge_file
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)
        self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(local_kb=False)

    def generate_dtc_facts(self, dtc_knowledge: DTCKnowledge) -> Tuple[str, list]:
        """
        Generates the DTC-related facts to be entered into the knowledge graph.

        :param dtc_knowledge: parsed DTC knowledge
        :return: [DTC UUID, generated fact list]
        """
        dtc_uuid = "dtc_" + uuid.uuid4().hex
        fact_list = []
        # check whether DTC to be added is already part of the KG
        if len(self.knowledge_graph_query_tool.query_dtc_instance_by_code(dtc_knowledge.dtc)) > 0:
            print("Specified component (" + dtc_knowledge.dtc + ") already present in KG")
        else:
            fact_list = [
                Fact((dtc_uuid, RDF.type, self.onto_namespace["DTC"].toPython())),
                Fact((dtc_uuid, self.onto_namespace.code, dtc_knowledge.dtc), property_fact=True)
            ]
            for code in dtc_knowledge.occurs_with:
                fact_list.append(Fact((dtc_uuid, self.onto_namespace.occurs_with_DTC, code), property_fact=True))

        return dtc_uuid, fact_list

    def generate_fault_cat_facts(self, dtc_uuid: str, dtc_knowledge: DTCKnowledge) -> Tuple[str, list]:
        """
        Generates the FaultCategory-related facts to be entered into the knowledge graph.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :param dtc_knowledge: parsed DTC knowledge
        :return: [fault category UUID, generated fact list]
        """
        fault_cat_uuid = "fault_cat_" + uuid.uuid4().hex
        dtc_parser = DTCParser()
        cat_desc = dtc_parser.parse_code_machine_readable(dtc_knowledge.dtc)
        fact_list = []
        # check whether fault category to be added is already part of the KG
        if len(self.knowledge_graph_query_tool.query_fault_cat_by_description(cat_desc)) > 0:
            print("Specified fault cat (" + cat_desc + ") already present in KG")
        else:
            fact_list = [
                Fact((fault_cat_uuid, RDF.type, self.onto_namespace["FaultCategory"].toPython())),
                Fact((fault_cat_uuid, self.onto_namespace.category_description, cat_desc), property_fact=True),
                Fact((dtc_uuid, self.onto_namespace.hasCategory, fault_cat_uuid))
            ]
        return fault_cat_uuid, fact_list

    def generate_fault_cond_facts(self, dtc_uuid: str, dtc_knowledge: DTCKnowledge) -> Tuple[str, list]:
        """
        Generates the FaultCondition-related facts to be entered into the knowledge graph.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :param dtc_knowledge: parsed DTC knowledge
        :return: [fault condition UUID, generated fact list]
        """
        fault_cond_uuid = "fault_cond_" + uuid.uuid4().hex
        fault_cond = dtc_knowledge.fault_condition
        fact_list = []
        # check whether fault condition to be added is already part of the KG
        if len(self.knowledge_graph_query_tool.query_fault_condition_by_description(fault_cond)) > 0:
            print("Specified fault condition (" + fault_cond + ") already present in KG")
        else:
            fact_list = [
                Fact((fault_cond_uuid, RDF.type, self.onto_namespace["FaultCondition"].toPython())),
                Fact((fault_cond_uuid, self.onto_namespace.condition_description, fault_cond), property_fact=True),
                Fact((dtc_uuid, self.onto_namespace.represents, fault_cond_uuid))
            ]
        return fault_cond_uuid, fact_list

    def generate_symptom_facts(self, fault_cond_uuid: str, dtc_knowledge: DTCKnowledge) -> list:
        """
        Generates the Symptom-related facts to be entered into the knowledge graph.

        :param fault_cond_uuid: FaultCondition UUID used to draw the connection to a fault condition
        :param dtc_knowledge: parsed DTC knowledge
        :return: generated fact list
        """
        fact_list = []
        # there can be more than one symptom instance per DTC
        for symptom in dtc_knowledge.symptoms:
            symptom_uuid = "symptom_" + uuid.uuid4().hex
            # check whether symptom to be added is already part of the KG
            if len(self.knowledge_graph_query_tool.query_symptoms_by_desc(symptom)) > 0:
                print("Specified symptom (" + symptom + ") already present in KG")
            else:
                fact_list.append(Fact((symptom_uuid, RDF.type, self.onto_namespace["Symptom"].toPython())))
                fact_list.append(
                    Fact((symptom_uuid, self.onto_namespace.symptom_description, symptom), property_fact=True))
                fact_list.append(Fact((fault_cond_uuid, self.onto_namespace.manifestedBy, symptom_uuid)))
        return fact_list

    def generate_facts_to_connect_components_and_dtc(self, dtc_uuid: str, dtc_knowledge: DTCKnowledge) -> list:
        """
        Generates the facts that connect the present DTC with associated suspect components, i.e., generating
        the diagnostic associations.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :param dtc_knowledge: parsed DTC knowledge
        :return: generated fact list
        """
        fact_list = []
        # there can be more than one suspect component instance per DTC
        for idx, comp in enumerate(dtc_knowledge.suspect_components):
            component_by_name = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)
            # ensure that all the suspect components considered here are already part of the KG
            assert len(component_by_name) == 1
            comp_uuid = component_by_name[0].split("#")[1]
            # creating diagnostic association between DTC and SuspectComponents
            diag_association_uuid = "diag_association_" + uuid.uuid4().hex
            fact_list.append(
                Fact((diag_association_uuid, RDF.type, self.onto_namespace["DiagnosticAssociation"].toPython())))
            fact_list.append(Fact((dtc_uuid, self.onto_namespace.has, diag_association_uuid)))
            fact_list.append(Fact((diag_association_uuid, self.onto_namespace.priority_id, idx), property_fact=True))
            fact_list.append(Fact((diag_association_uuid, self.onto_namespace.pointsTo, comp_uuid)))
        return fact_list

    def generate_suspect_component_facts(self, comp_knowledge_list: list) -> list:
        """
        Generates the SuspectComponent-related facts to be entered into the knowledge graph.

        :param comp_knowledge_list: list of parsed SuspectComponents
        :return: generated fact list
        """
        fact_list = []
        for comp_knowledge in comp_knowledge_list:
            comp_name = comp_knowledge.suspect_component
            # check whether component to be added is already part of the KG
            if len(self.knowledge_graph_query_tool.query_suspect_component_by_name(comp_name)) > 0:
                print("Specified component (" + comp_name + ") already present in KG")
            else:
                comp_uuid = "comp_" + uuid.uuid4().hex
                fact_list.append(Fact((comp_uuid, RDF.type, self.onto_namespace["SuspectComponent"].toPython())))
                fact_list.append(Fact((comp_uuid, self.onto_namespace.component_name, comp_name), property_fact=True))
                fact_list.append(Fact((comp_uuid, self.onto_namespace.use_oscilloscope, comp_knowledge.oscilloscope),
                                      property_fact=True))

                for comp in comp_knowledge.affected_by:
                    # all components in the affected_by list should be defined in the KG, i.e., should have ex. 1 result
                    assert len(self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)) == 1
                    fact_list.append(Fact((comp_uuid, self.onto_namespace.affected_by, comp), property_fact=True))
        return fact_list

    def generate_subsystem_facts(self, subsystem_knowledge: SubsystemKnowledge) -> list:
        """
        Generates vehicle subsystem facts to be entered into the knowledge graph.

        :param subsystem_knowledge: parsed VehicleSubsystem knowledge
        :return: generated fact list
        """
        fact_list = []
        subsystem_name = subsystem_knowledge.vehicle_subsystem
        # check whether subsystem to be added is already part of the KG
        if len(self.knowledge_graph_query_tool.query_vehicle_subsystem_by_name(subsystem_name)) > 0:
            print("Specified subsystem (" + subsystem_name + ") already present in KG")
        else:
            subsystem_uuid = "subsystem_" + uuid.uuid4().hex
            fact_list = [
                Fact((subsystem_uuid, RDF.type, self.onto_namespace["VehicleSubsystem"].toPython())),
                Fact((subsystem_uuid, self.onto_namespace.subsystem_name, subsystem_name), property_fact=True)
            ]
            for containing_comp in subsystem_knowledge.contains:
                # relate knowledge to already existing facts
                sus_comp = self.knowledge_graph_query_tool.query_suspect_component_by_name(containing_comp)
                assert len(sus_comp) == 1
                comp_uuid = sus_comp[0].split("#")[1]
                fact_list.append(Fact((subsystem_uuid, self.onto_namespace.contains, comp_uuid)))

            verifying_comp = subsystem_knowledge.verified_by
            # relate knowledge to already existing facts
            verifying_comp_instance = self.knowledge_graph_query_tool.query_suspect_component_by_name(verifying_comp)
            assert len(verifying_comp_instance) == 1
            verifying_comp_uuid = verifying_comp_instance[0].split("#")[1]
            fact_list.append(Fact((verifying_comp_uuid, self.onto_namespace.verifies, subsystem_uuid)))
        return fact_list

    def extend_knowledge_graph(self) -> None:
        """
        Parses the expert knowledge from the specified file and extends the knowledge graph with it.
        """
        print("parse expert knowledge..")

        fact_list = []

        if "dtc" in self.knowledge_file:
            dtc_knowledge = expert_knowledge_parser.parse_knowledge(self.knowledge_file)
            dtc_uuid, dtc_facts = self.generate_dtc_facts(dtc_knowledge)
            _, fault_cat_facts = self.generate_fault_cat_facts(dtc_uuid, dtc_knowledge)
            fault_cond_uuid, fault_cond_facts = self.generate_fault_cond_facts(dtc_uuid, dtc_knowledge)
            symptom_facts = self.generate_symptom_facts(fault_cond_uuid, dtc_knowledge)
            diag_association_facts = self.generate_facts_to_connect_components_and_dtc(dtc_uuid, dtc_knowledge)
            fact_list = dtc_facts + fault_cat_facts + fault_cond_facts + symptom_facts + diag_association_facts

        elif "component" in self.knowledge_file:
            comp_knowledge_list = expert_knowledge_parser.parse_knowledge(self.knowledge_file)
            fact_list = self.generate_suspect_component_facts(comp_knowledge_list)

        elif "subsystem" in self.knowledge_file:
            subsystem_knowledge = expert_knowledge_parser.parse_knowledge(self.knowledge_file)
            fact_list = self.generate_subsystem_facts(subsystem_knowledge)

        # enter facts into knowledge graph
        self.fuseki_connection.extend_knowledge_graph(fact_list)


if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer("templates/dtc_expert_template.txt")
    expert_knowledge_enhancer.extend_knowledge_graph()
