#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import Tuple

from dtc_parser.parser import DTCParser
from rdflib import Namespace, RDF

import expert_knowledge_parser
from component_set_knowledge import ComponentSetKnowledge
from config import ONTOLOGY_PREFIX
from connection_controller import ConnectionController
from dtc_knowledge import DTCKnowledge
from fact import Fact
from knowledge_graph_query_tool import KnowledgeGraphQueryTool


class ExpertKnowledgeEnhancer:
    """
    Extends the knowledge graph hosted by the Fuseki server with vehicle-agnostic OBD knowledge (codes, symptoms, etc.).

    The knowledge can be provided in the form of `templates/dtc_expert_template.txt`,
    `templates/component_expert_template.txt`, and `templates/subsystem_expert_template.txt`.

    Furthermore, new knowledge can be provided as input to a web interface (cf. `app.py`).
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
        dtc_instance = self.knowledge_graph_query_tool.query_dtc_instance_by_code(dtc_knowledge.dtc)
        if len(dtc_instance) > 0:
            print("Specified DTC (" + dtc_knowledge.dtc + ") already present in KG")
            dtc_uuid = dtc_instance[0].split("#")[1]
        else:
            dtc_parser = DTCParser()
            code_type = dtc_parser.parse_code_machine_readable(dtc_knowledge.dtc)["code_type"]
            code_type = "generic" if "generic" in code_type else "manufacturer-specific"
            fact_list = [
                Fact((dtc_uuid, RDF.type, self.onto_namespace["DTC"].toPython())),
                Fact((dtc_uuid, self.onto_namespace.code, dtc_knowledge.dtc), property_fact=True),
                Fact((dtc_uuid, self.onto_namespace.code_type, code_type), property_fact=True)
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
        cat_desc = dtc_parser.parse_code_machine_readable(dtc_knowledge.dtc)["fault_description"]
        fact_list = []
        # check whether fault category to be added is already part of the KG
        fault_cat_instance = self.knowledge_graph_query_tool.query_fault_cat_by_description(cat_desc)
        if len(fault_cat_instance) > 0:
            print("Specified fault cat (" + cat_desc + ") already present in KG")
            fault_cat_uuid = fault_cat_instance[0].split("#")[1]
        else:
            fact_list = [
                Fact((fault_cat_uuid, RDF.type, self.onto_namespace["FaultCategory"].toPython())),
                Fact((fault_cat_uuid, self.onto_namespace.category_description, cat_desc), property_fact=True)
            ]
        fact_list.append(Fact((dtc_uuid, self.onto_namespace.hasCategory, fault_cat_uuid)))
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
        fault_cond_instance = self.knowledge_graph_query_tool.query_fault_condition_by_description(fault_cond)
        if len(fault_cond_instance) > 0:
            print("Specified fault condition (" + fault_cond + ") already present in KG, updating description")
            fault_cond_uuid = fault_cond_instance[0].split("#")[1]
            fact_list.append(Fact(
                (fault_cond_uuid, self.onto_namespace.condition_description, fault_cond), property_fact=True)
            )
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
            symptom_instance = self.knowledge_graph_query_tool.query_symptoms_by_desc(symptom)
            if len(symptom_instance) > 0:
                print("Specified symptom (" + symptom + ") already present in KG")
                symptom_uuid = symptom_instance[0].split("#")[1]
            else:
                fact_list.append(Fact((symptom_uuid, RDF.type, self.onto_namespace["Symptom"].toPython())))
                fact_list.append(
                    Fact((symptom_uuid, self.onto_namespace.symptom_description, symptom), property_fact=True))

            # there can be more than one `manifestedBy` relation per symptom
            fault_condition_instances_already_present = \
                self.knowledge_graph_query_tool.query_fault_condition_instances_by_symptom(symptom)

            if fault_cond_uuid not in [fc.split("#")[1] for fc in fault_condition_instances_already_present]:
                # symptom can already be present, but not associated with this fault condition
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

            # making sure that there is only one diagnostic association, i.e. one priority ID, between any pair
            # of DTC and suspect component
            diag_association = self.knowledge_graph_query_tool.query_diagnostic_association_by_dtc_and_sus_comp(
                dtc_knowledge.dtc, comp
            )
            if len(diag_association) > 0:
                print("Diagnostic association between", dtc_knowledge.dtc, "and", comp, "already defined in KG")
            else:
                # creating diagnostic association between DTC and SuspectComponent
                diag_association_uuid = "diag_association_" + uuid.uuid4().hex
                fact_list.append(
                    Fact((diag_association_uuid, RDF.type, self.onto_namespace["DiagnosticAssociation"].toPython())))

                fact_list.append(Fact((dtc_uuid, self.onto_namespace.hasAssociation, diag_association_uuid)))
                fact_list.append(
                    Fact((diag_association_uuid, self.onto_namespace.priority_id, idx), property_fact=True))
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
            comp_uuid = "comp_" + uuid.uuid4().hex
            # check whether component to be added is already part of the KG
            comp_instance = self.knowledge_graph_query_tool.query_suspect_component_by_name(comp_name)
            if len(comp_instance) > 0:
                print("Specified component (" + comp_name + ") already present in KG")
                comp_uuid = comp_instance[0].split("#")[1]
            else:
                fact_list.append(Fact((comp_uuid, RDF.type, self.onto_namespace["SuspectComponent"].toPython())))
                fact_list.append(Fact((comp_uuid, self.onto_namespace.component_name, comp_name), property_fact=True))

            fact_list.append(
                Fact((comp_uuid, self.onto_namespace.use_oscilloscope, comp_knowledge.oscilloscope), property_fact=True)
            )
            for comp in comp_knowledge.affected_by:
                # all components in the affected_by list should be defined in the KG, i.e., should have ex. 1 result
                assert len(self.knowledge_graph_query_tool.query_suspect_component_by_name(comp)) == 1
                fact_list.append(Fact((comp_uuid, self.onto_namespace.affected_by, comp), property_fact=True))

        return fact_list

    def generate_component_set_facts(self, comp_set_knowledge: ComponentSetKnowledge) -> list:
        """
        Generates vehicle component set facts to be entered into the knowledge graph.

        :param comp_set_knowledge: parsed ComponentSet knowledge
        :return: generated fact list
        """
        fact_list = []
        comp_set_name = comp_set_knowledge.component_set
        comp_set_uuid = "component_set_" + uuid.uuid4().hex
        # check whether component set to be added is already part of the KG
        comp_set_instance = self.knowledge_graph_query_tool.query_component_set_by_name(comp_set_name)
        if len(comp_set_instance) > 0:
            print("Specified component set (" + comp_set_name + ") already present in KG")
            comp_set_uuid = comp_set_instance[0].split("#")[1]
        else:
            fact_list = [
                Fact((comp_set_uuid, RDF.type, self.onto_namespace["ComponentSet"].toPython())),
                Fact((comp_set_uuid, self.onto_namespace.set_name, comp_set_name), property_fact=True)
            ]

        for containing_comp in comp_set_knowledge.includes:
            # relate knowledge to already existing facts
            sus_comp = self.knowledge_graph_query_tool.query_suspect_component_by_name(containing_comp)
            # should already be defined in KG
            assert len(sus_comp) == 1
            comp_uuid = sus_comp[0].split("#")[1]
            fact_list.append(Fact((comp_set_uuid, self.onto_namespace.includes, comp_uuid)))

        assert isinstance(comp_set_knowledge.verified_by, list)
        for verifying_comp in comp_set_knowledge.verified_by:
            # relate knowledge to already existing facts
            verifying_comp_instance = self.knowledge_graph_query_tool.query_suspect_component_by_name(verifying_comp)
            assert len(verifying_comp_instance) == 1
            verifying_comp_uuid = verifying_comp_instance[0].split("#")[1]
            fact_list.append(Fact((verifying_comp_uuid, self.onto_namespace.verifies, comp_set_uuid)))

        return fact_list

    def generate_dtc_related_facts(self, dtc_knowledge: DTCKnowledge) -> list:
        """
        Generates all facts obtained from the DTC form / template to be entered into the knowledge graph and extends
        it with automatically obtained information from the dtc_parser.

        :param dtc_knowledge: parsed DTC knowledge
        :return: generated fact list
        """
        dtc_uuid, dtc_facts = self.generate_dtc_facts(dtc_knowledge)
        _, fault_cat_facts = self.generate_fault_cat_facts(dtc_uuid, dtc_knowledge)
        fault_cond_uuid, fault_cond_facts = self.generate_fault_cond_facts(dtc_uuid, dtc_knowledge)
        symptom_facts = self.generate_symptom_facts(fault_cond_uuid, dtc_knowledge)
        diag_association_facts = self.generate_facts_to_connect_components_and_dtc(dtc_uuid, dtc_knowledge)
        fact_list = dtc_facts + fault_cat_facts + fault_cond_facts + symptom_facts + diag_association_facts
        return fact_list

    def extend_knowledge_graph(self) -> None:
        """
        Parses the expert knowledge from the specified file and extends the knowledge graph with it.
        """
        print("parse expert knowledge..")

        fact_list = []

        if "dtc" in self.knowledge_file:
            dtc_knowledge = expert_knowledge_parser.parse_knowledge(self.knowledge_file)
            fact_list = self.generate_dtc_related_facts(self, dtc_knowledge)

        elif "component" in self.knowledge_file:
            comp_knowledge_list = expert_knowledge_parser.parse_knowledge(self.knowledge_file)
            fact_list = self.generate_suspect_component_facts(comp_knowledge_list)

        elif "subsystem" in self.knowledge_file:
            subsystem_knowledge = expert_knowledge_parser.parse_knowledge(self.knowledge_file)
            fact_list = self.generate_component_set_facts(subsystem_knowledge)

        # enter facts into knowledge graph
        self.fuseki_connection.extend_knowledge_graph(fact_list)


if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer("templates/dtc_expert_template.txt")
    expert_knowledge_enhancer.extend_knowledge_graph()
