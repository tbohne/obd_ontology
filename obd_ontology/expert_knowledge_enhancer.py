#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from typing import List
from typing import Tuple

from dtc_parser.parser import DTCParser
from rdflib import Namespace, RDF

from obd_ontology.component_knowledge import ComponentKnowledge
from obd_ontology.component_set_knowledge import ComponentSetKnowledge
from obd_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL
from obd_ontology.connection_controller import ConnectionController
from obd_ontology.dtc_knowledge import DTCKnowledge
from obd_ontology.fact import Fact
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


class ExpertKnowledgeEnhancer:
    """
    Extends the knowledge graph hosted by the Fuseki server with vehicle-agnostic expert knowledge.

    The acquisition of expert knowledge is accomplished via a web interface (collaborative knowledge acquisition
    component) through which the knowledge is entered, stored in the Resource Description Framework (RDF) format,
    and hosted on an Apache Jena Fuseki server (cf. `app.py`).

    This class deals with semantic fact generation for the vehicle-agnostic expert knowledge.
    """

    def __init__(self, kg_url: str = FUSEKI_URL) -> None:
        """
        Initializes the expert knowledge enhancer.

        :param kg_url: URL for the knowledge graph server
        """
        # establish connection to 'Apache Jena Fuseki' server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)
        self.knowledge_graph_query_tool = KnowledgeGraphQueryTool()

    def generate_condition_description_fact(self, fc_uuid: str, fault_cond: str, prop: bool) -> Fact:
        """
        Generates a `condition_description` fact (RDF) based on the provided properties.

        :param fc_uuid: UUID of the fault condition instance to generate fact for
        :param fault_cond: the fault condition description
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((fc_uuid, self.onto_namespace.condition_description, fault_cond), property_fact=prop)

    def generate_co_occurring_dtc_fact(self, dtc_uuid: str, code: str, prop: bool) -> Fact:
        """
        Generates an `occurs_with_DTC` fact (RDF) based on the provided properties.

        :param dtc_uuid: UUID of the DTC to generate fact for
        :param code: code of the co-occurring DTC
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((dtc_uuid, self.onto_namespace.occurs_with_DTC, code), property_fact=prop)

    def generate_generated_heatmap_fact(self, heatmap_uuid: str, heatmap: str, prop: bool) -> Fact:
        """
        Generates a `generated_heatmap` fact (RDF) based on the provided properties.

        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param heatmap: heatmap string
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((heatmap_uuid, self.onto_namespace.generated_heatmap, heatmap), property_fact=prop)

    def generate_heatmap_generation_method_fact(self, heatmap_uuid: str, gen_method: str, prop: bool) -> Fact:
        """
        Generates a `generation_method` fact (RDF) based on the provided properties.

        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param gen_method: heatmap generation method (e.g. tf-keras-gradcam)
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((heatmap_uuid, self.onto_namespace.generation_method, gen_method), property_fact=prop)

    def generate_symptom_fact(self, fc_uuid: str, symptom_uuid: str, prop: bool) -> Fact:
        """
        Generates a `manifestedBy` fact (RDF) based on the provided properties.

        :param fc_uuid: UUID of the fault condition to generate the fact for
        :param symptom_uuid: UUID of the symptom to generate the fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((fc_uuid, self.onto_namespace.manifestedBy, symptom_uuid), property_fact=prop)

    def generate_has_association_fact(self, dtc_uuid: str, da_uuid: str, prop: bool) -> Fact:
        """
        Generates a `hasAssociation` fact (RDF) based on the provided properties.

        :param dtc_uuid: UUID of the DTC to generate fact for
        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((dtc_uuid, self.onto_namespace.hasAssociation, da_uuid), property_fact=prop)

    def generate_points_to_fact(self, da_uuid: str, comp_uuid: str, prop: bool) -> Fact:
        """
        Generates a `pointsTo` fact (RDF) based on the provided properties.

        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param comp_uuid: UUID of the suspect component to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((da_uuid, self.onto_namespace.pointsTo, comp_uuid), property_fact=prop)

    def generate_diagnostic_association_fact(self, da_uuid: str, prop: bool) -> Fact:
        """
        Generates a `DiagnosticAssociation` fact (RDF) based on the provided properties.

        :param da_uuid: UUID of the diagnostic association to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact(
            (da_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", self.onto_namespace.DiagnosticAssociation),
            property_fact=prop
        )

    def generate_heatmap_fact(self, heatmap_uuid: str, prop: bool) -> Fact:
        """
        Generates a `Heatmap` fact (RDF) based on the provided properties.

        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact(
            (heatmap_uuid, "http://www.w3.org/1999/02/22-rdf-syntax-ns#type", self.onto_namespace.Heatmap),
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
        return Fact((subsystem_uuid, self.onto_namespace.contains, comp_uuid), property_fact=prop)

    def generate_produces_fact(self, classification_uuid: str, heatmap_uuid: str, prop: bool) -> Fact:
        """
        Generates a `produces` fact (RDF) based on the provided properties.

        :param classification_uuid: UUID of the oscillogram classification to generate fact for
        :param heatmap_uuid: UUID of the heatmap to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((classification_uuid, self.onto_namespace.produces, heatmap_uuid), property_fact=prop)

    def generate_includes_fact(self, component_set_uuid: str, comp_uuid: str, prop: bool) -> Fact:
        """
        Generates an `includes` fact (RDF) based on the provided properties.

        :param component_set_uuid: UUID of the component set to generate fact for
        :param comp_uuid: UUID of the suspect component to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((component_set_uuid, self.onto_namespace.includes, comp_uuid), property_fact=prop)

    def generate_verifies_fact(self, comp_uuid: str, subsystem_uuid: str, prop: bool) -> Fact:
        """
        Generates a `verifies` fact (RDF) based on the provided properties.

        :param comp_uuid: UUID of the component to generate fact for
        :param subsystem_uuid: UUID of the subsystem to generate fact for
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((comp_uuid, self.onto_namespace.verifies, subsystem_uuid), property_fact=prop)

    def generate_use_oscilloscope_fact(self, comp_uuid: str, osci_usage: bool, prop: bool) -> Fact:
        """
        Generates a `use_oscilloscope` fact (RDF) based on the provided properties.

        :param comp_uuid: UUID of the component to generate fact for
        :param osci_usage: oscilloscope usage value (literal)
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((comp_uuid, self.onto_namespace.use_oscilloscope, osci_usage), property_fact=prop)

    def generate_affected_by_fact(self, comp_uuid: str, comp_name: str, prop: bool) -> Fact:
        """
        Generates an `affected_by` fact (RDF) based on the provided properties.

        :param comp_uuid: UUID of the component to generate fact for
        :param comp_name: name of the affecting component
        :param prop: determines whether it's a property fact
        :return: generated fact
        """
        return Fact((comp_uuid, self.onto_namespace.affected_by, comp_name), property_fact=prop)

    def generate_dtc_facts(self, dtc_knowledge: DTCKnowledge) -> Tuple[str, str, List[Fact]]:
        """
        Generates the DTC-related facts to be entered into the knowledge graph.

        :param dtc_knowledge: parsed DTC knowledge
        :return: (DTC UUID, subsystem UUID, generated fact list)
        """
        dtc_uuid = "dtc_" + uuid.uuid4().hex
        fact_list = []
        dtc_parser = DTCParser()
        parsed_code = dtc_parser.parse_code_machine_readable(dtc_knowledge.dtc)
        subsystem_name = parsed_code["vehicle_subsystem"]
        subsystem_instance = self.knowledge_graph_query_tool.query_vehicle_subsystem_by_name(subsystem_name)
        vehicle_part = parsed_code["vehicle_part"]

        # check whether DTC to be added is already part of the KG
        dtc_instance = self.knowledge_graph_query_tool.query_dtc_instance_by_code(dtc_knowledge.dtc)
        if len(dtc_instance) > 0:
            print("Specified DTC (" + dtc_knowledge.dtc + ") already present in KG")
            dtc_uuid = dtc_instance[0].split("#")[1]
            assert len(subsystem_instance) > 0  # subsystem already part of KG
            subsystem_uuid = subsystem_instance[0].split("#")[1]
        else:
            code_type = parsed_code["code_type"]
            code_type = "generic" if "generic" in code_type else "manufacturer-specific"
            fact_list = [
                Fact((dtc_uuid, RDF.type, self.onto_namespace["DTC"].toPython())),
                Fact((dtc_uuid, self.onto_namespace.code, dtc_knowledge.dtc), property_fact=True),
                Fact((dtc_uuid, self.onto_namespace.code_type, code_type), property_fact=True)
            ]
            if len(subsystem_instance) > 0:  # subsystems already part of KG
                subsystem_uuid = subsystem_instance[0].split("#")[1]
            else:  # creating new subsystem
                subsystem_uuid = "vehicle_subsystem_" + uuid.uuid4().hex
                fact_list.append(Fact((subsystem_uuid, RDF.type, self.onto_namespace["VehicleSubsystem"].toPython())))
                fact_list.append(
                    Fact((subsystem_uuid, self.onto_namespace.subsystem_name, subsystem_name), property_fact=True))
                fact_list.append(
                    Fact((subsystem_uuid, self.onto_namespace.vehicle_part, vehicle_part), property_fact=True))
            fact_list.append(Fact((dtc_uuid, self.onto_namespace.indicates, subsystem_uuid)))

        for code in dtc_knowledge.occurs_with:
            fact_list.append(Fact((dtc_uuid, self.onto_namespace.occurs_with_DTC, code), property_fact=True))
        return dtc_uuid, subsystem_uuid, fact_list

    def generate_fault_cat_facts(self, dtc_uuid: str, dtc_knowledge: DTCKnowledge) -> Tuple[str, List[Fact]]:
        """
        Generates the `FaultCategory`-related facts to be entered into the knowledge graph.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :param dtc_knowledge: parsed DTC knowledge
        :return: (fault category UUID, generated fact list)
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

    def generate_fault_cond_facts(self, dtc_uuid: str, dtc_knowledge: DTCKnowledge) -> Tuple[str, List[Fact]]:
        """
        Generates the `FaultCondition`-related facts to be entered into the knowledge graph.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :param dtc_knowledge: parsed DTC knowledge
        :return: (fault condition UUID, generated fact list)
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

    def generate_symptom_facts(self, fault_cond_uuid: str, dtc_knowledge: DTCKnowledge) -> List[Fact]:
        """
        Generates the `Symptom`-related facts to be entered into the knowledge graph.

        :param fault_cond_uuid: fault condition UUID used to draw the connection to a fault condition
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
                    Fact((symptom_uuid, self.onto_namespace.symptom_description, symptom), property_fact=True)
                )
            # there can be more than one `manifestedBy` relation per symptom
            fault_condition_instances_already_present = \
                self.knowledge_graph_query_tool.query_fault_condition_instances_by_symptom(symptom)
            if fault_cond_uuid not in [fc.split("#")[1] for fc in fault_condition_instances_already_present]:
                # symptom can already be present, but not associated with this fault condition
                fact_list.append(Fact((fault_cond_uuid, self.onto_namespace.manifestedBy, symptom_uuid)))
        return fact_list

    def generate_facts_to_connect_components_and_dtc(self, dtc_uuid: str, subsystem_uuid: str,
                                                     dtc_knowledge: DTCKnowledge) -> List[Fact]:
        """
        Generates the facts that connect the present DTC with associated suspect components, i.e., generating
        the diagnostic associations.

        :param dtc_uuid: DTC UUID used to draw the connection to the trouble code
        :param subsystem_uuid: subsystem UUID used to draw the connection to the subsystem
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
            diag_association = self.knowledge_graph_query_tool.query_priority_id_by_dtc_and_sus_comp(
                dtc_knowledge.dtc, comp
            )
            if len(diag_association) > 0:
                print("Diagnostic association between", dtc_knowledge.dtc, "and", comp, "already defined in KG")
            else:
                # TODO: shouldn't the diagnostic association be deletable, too?
                # creating diagnostic association between DTC and SuspectComponent
                diag_association_uuid = "diag_association_" + uuid.uuid4().hex
                fact_list.append(
                    Fact((diag_association_uuid, RDF.type, self.onto_namespace["DiagnosticAssociation"].toPython()))
                )
                fact_list.append(Fact((dtc_uuid, self.onto_namespace.hasAssociation, diag_association_uuid)))
                fact_list.append(
                    Fact((diag_association_uuid, self.onto_namespace.priority_id, idx), property_fact=True)
                )
                fact_list.append(Fact((diag_association_uuid, self.onto_namespace.pointsTo, comp_uuid)))

                # automatically adding the suspect component to the vehicle subsystem associated with the DTC
                dtc_parser = DTCParser()
                subsystem_name = dtc_parser.parse_code_machine_readable(dtc_knowledge.dtc)["vehicle_subsystem"]
                # only add fact if it's not already part of the KG (important because suspect components can be
                # associated with many DTCs)
                components_by_subsystem = self.knowledge_graph_query_tool.query_suspect_components_by_subsystem_name(
                    subsystem_name, False
                )
                if comp in components_by_subsystem:
                    print("comp:", comp, "already in:", subsystem_name, "- not adding it..")
                else:
                    print("comp:", comp, "not yet part of:", subsystem_name, "- adding it..")
                    fact_list.append(Fact((subsystem_uuid, self.onto_namespace.contains, comp_uuid)))
        return fact_list

    def generate_suspect_component_facts(self, comp_knowledge_list: List[ComponentKnowledge]) -> List[Fact]:
        """
        Generates the `SuspectComponent`-related facts to be entered into the knowledge graph.

        :param comp_knowledge_list: list of parsed suspect components
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

    def generate_component_set_facts(self, comp_set_knowledge: ComponentSetKnowledge) -> List[Fact]:
        """
        Generates vehicle component set facts to be entered into the knowledge graph.

        :param comp_set_knowledge: parsed component set knowledge
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

    def generate_dtc_related_facts(self, dtc_knowledge: DTCKnowledge) -> List[Fact]:
        """
        Generates all facts obtained from the DTC form / template to be entered into the knowledge graph and extends
        it with automatically obtained information from the DTC parser.

        :param dtc_knowledge: parsed DTC knowledge
        :return: generated fact list
        """
        dtc_uuid, subsystem_uuid, dtc_facts = self.generate_dtc_facts(dtc_knowledge)
        _, fault_cat_facts = self.generate_fault_cat_facts(dtc_uuid, dtc_knowledge)
        fault_cond_uuid, fault_cond_facts = self.generate_fault_cond_facts(dtc_uuid, dtc_knowledge)
        symptom_facts = self.generate_symptom_facts(fault_cond_uuid, dtc_knowledge)
        diag_association_facts = self.generate_facts_to_connect_components_and_dtc(dtc_uuid, subsystem_uuid,
                                                                                   dtc_knowledge)
        fact_list = dtc_facts + fault_cat_facts + fault_cond_facts + symptom_facts + diag_association_facts
        return fact_list

    def add_dtc_to_knowledge_graph(self, dtc: str, occurs_with: List[str], fault_condition: str, symptoms: List[str],
                                   suspect_components: List[str]) -> None:
        """
        Adds a DTC instance with the given properties to the knowledge graph.

        :param dtc: diagnostic trouble code to be considered
        :param occurs_with: other DTCs frequently occurring with the considered one
        :param fault_condition: fault condition associated with the considered DTC
        :param symptoms: symptoms associated with the considered DTC
        :param suspect_components: components that should be checked when this DTC occurs
                                   (order defines suggestion priority)
        """
        assert isinstance(dtc, str)
        assert isinstance(occurs_with, list)
        assert isinstance(fault_condition, str)
        assert isinstance(symptoms, list)
        assert isinstance(suspect_components, list)

        new_dtc_knowledge = DTCKnowledge(dtc=dtc, occurs_with=occurs_with, fault_condition=fault_condition,
                                         symptoms=symptoms, suspect_components=suspect_components)
        fact_list = self.generate_dtc_related_facts(new_dtc_knowledge)
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def add_component_to_knowledge_graph(self, suspect_component: str, affected_by: List[str],
                                         oscilloscope: bool) -> None:
        """
        Adds a component instance with the given properties to the knowledge graph.

        :param suspect_component: component to be checked
        :param affected_by: list of components whose misbehavior could affect the correct functioning of the component
                            under consideration
        :param oscilloscope: whether oscilloscope measurement possible / reasonable
        """
        assert isinstance(suspect_component, str)
        assert isinstance(affected_by, list)
        assert isinstance(oscilloscope, bool)

        new_component_knowledge = ComponentKnowledge(suspect_component=suspect_component, oscilloscope=oscilloscope,
                                                     affected_by=affected_by)
        fact_list = self.generate_suspect_component_facts([new_component_knowledge])
        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def add_component_set_to_knowledge_graph(self, component_set: str, includes: List[str],
                                             verified_by: List[str]) -> None:
        """
        Adds a component set instance to the knowledge graph.

        :param component_set: vehicle component set to be represented
        :param includes: suspect components assigned to this component set
        :param verified_by: component set can be verified by checking this suspect component
        """
        assert isinstance(component_set, str)
        assert isinstance(includes, list)
        assert isinstance(verified_by, list)

        new_comp_set_knowledge = ComponentSetKnowledge(component_set=component_set, includes=includes,
                                                       verified_by=verified_by)
        fact_list = self.generate_component_set_facts(new_comp_set_knowledge)
        self.fuseki_connection.extend_knowledge_graph(fact_list)


if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()
