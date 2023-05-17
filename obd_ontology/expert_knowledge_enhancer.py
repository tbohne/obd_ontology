#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import uuid
from datetime import date
from typing import Tuple, List

from dtc_parser.parser import DTCParser
from rdflib import Namespace, RDF

from obd_ontology import expert_knowledge_parser
from obd_ontology.component_set_knowledge import ComponentSetKnowledge
from obd_ontology.config import ONTOLOGY_PREFIX
from obd_ontology.connection_controller import ConnectionController
from obd_ontology.dtc_knowledge import DTCKnowledge
from obd_ontology.fact import Fact
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


class ExpertKnowledgeEnhancer:
    """
    Extends the knowledge graph hosted by the Fuseki server with vehicle-agnostic OBD knowledge (codes, symptoms, etc.).

    The knowledge can be provided in the form of `templates/dtc_expert_template.txt`,
    `templates/component_expert_template.txt`, and `templates/subsystem_expert_template.txt`.

    Furthermore, new knowledge can be provided as input to a web interface (cf. `app.py`).
    """

    def __init__(self, knowledge_file: str = None) -> None:
        self.knowledge_file = knowledge_file
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)
        self.onto_namespace = Namespace(ONTOLOGY_PREFIX)
        self.knowledge_graph_query_tool = KnowledgeGraphQueryTool(local_kb=False)

    def generate_dtc_facts(self, dtc_knowledge: DTCKnowledge) -> Tuple[str, str, list]:
        """
        Generates the DTC-related facts to be entered into the knowledge graph.

        :param dtc_knowledge: parsed DTC knowledge
        :return: [DTC UUID, subsystem UUID, generated fact list]
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
            # subsystem already part of KG
            assert len(subsystem_instance) > 0
            subsystem_uuid = subsystem_instance[0].split("#")[1]
        else:
            code_type = parsed_code["code_type"]
            code_type = "generic" if "generic" in code_type else "manufacturer-specific"
            fact_list = [
                Fact((dtc_uuid, RDF.type, self.onto_namespace["DTC"].toPython())),
                Fact((dtc_uuid, self.onto_namespace.code, dtc_knowledge.dtc), property_fact=True),
                Fact((dtc_uuid, self.onto_namespace.code_type, code_type), property_fact=True)
            ]
            # subsystems already part of KG
            if len(subsystem_instance) > 0:
                subsystem_uuid = subsystem_instance[0].split("#")[1]
            else:
                # creating new subsystem
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

    def generate_facts_to_connect_components_and_dtc(self, dtc_uuid: str, subsystem_uuid: str,
                                                     dtc_knowledge: DTCKnowledge) -> list:
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
                    Fact((diag_association_uuid, RDF.type, self.onto_namespace["DiagnosticAssociation"].toPython())))
                fact_list.append(Fact((dtc_uuid, self.onto_namespace.hasAssociation, diag_association_uuid)))
                fact_list.append(
                    Fact((diag_association_uuid, self.onto_namespace.priority_id, idx), property_fact=True))
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

    def extend_kg_with_heatmap_facts(self, heatmap: List[float], gen_method: str) -> str:
        """
        Extends the knowledge graph with facts for the specified heatmap.

        :param heatmap: heatmap do be added to the KG
        :param gen_method: heatmap generation method, e.g. GradCAM
        :return: heatmap UUID
        """
        heatmap_uuid = "heatmap_" + uuid.uuid4().hex
        fact_list = [
            Fact((heatmap_uuid, RDF.type, self.onto_namespace["Heatmap"].toPython())),
            Fact((heatmap_uuid, self.onto_namespace.generated_heatmap, str(heatmap)), property_fact=True),
            Fact((heatmap_uuid, self.onto_namespace.generation_method, gen_method), property_fact=True)
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return heatmap_uuid

    def extend_kg_with_oscillogram_classification_facts(
            self, uncertainty: float, model_id: str, prediction: bool, oscillogram: List[float], heatmap: List[float],
            osci_set_id: str, gen_method: str, classification_reason: str, suspect_comp: str, diag_log_uuid: str
    ) -> None:
        """
        Extends the knowledge graph with facts for the specified oscillogram classification.

        :param uncertainty: uncertainty of the classification
        :param model_id: ID of the model that performed the classification
        :param prediction: prediction of the classification model (True -> POS, False -> NEG)
        :param oscillogram: classified oscillogram
        :param heatmap: generated heatmap
        :param osci_set_id: optional ID of a corresponding set of parallel recorded oscillograms
        :param gen_method: heatmap generation method
        :param classification_reason: diagnostic association or another classification instance
        :param suspect_comp: vehicle component to which the oscillogram belongs
        :param diag_log_uuid: ID of the diagnosis log to which the classification belongs
        """
        # either UUID of DA or UUID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "oscillogram_classification_" in classification_reason

        osci_classification_uuid = "oscillogram_classification_" + uuid.uuid4().hex
        fact_list = [
            Fact((osci_classification_uuid, RDF.type, self.onto_namespace["OscillogramClassification"].toPython())),
            Fact((osci_classification_uuid, self.onto_namespace.model_id, model_id), property_fact=True),
            Fact((osci_classification_uuid, self.onto_namespace.uncertainty, uncertainty), property_fact=True),
            Fact((osci_classification_uuid, self.onto_namespace.prediction, prediction), property_fact=True),
            Fact((osci_classification_uuid, self.onto_namespace.diagStep, diag_log_uuid))
        ]
        osci_uuid = self.extend_kg_with_oscillogram_recording(oscillogram)
        fact_list.append(
            Fact((osci_classification_uuid, self.onto_namespace.classifies, osci_uuid))
        )

        # if parallel osci set ID present, assign osci to set
        if len(osci_set_id) > 0:
            fact_list.append(
                Fact((osci_uuid, self.onto_namespace.partOf, osci_set_id))
            )

        # connect to heatmap
        heatmap_uuid = self.extend_kg_with_heatmap_facts(heatmap, gen_method)
        fact_list.append(
            Fact((osci_classification_uuid, self.onto_namespace.produces, heatmap_uuid))
        )

        # connect to component
        sus_comp_uuid = self.knowledge_graph_query_tool.query_suspect_component_by_name(suspect_comp)[0].split("#")[1]
        fact_list.append(
            Fact((osci_classification_uuid, self.onto_namespace.checks, sus_comp_uuid))
        )

        # set reason
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, self.onto_namespace.ledTo, osci_classification_uuid)))
        else:  # the reason is a classification instance (manual or osci)
            fact_list.append(Fact((classification_reason, self.onto_namespace.reasonFor, osci_classification_uuid)))

        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_kg_with_manual_inspection_facts(
            self, prediction: bool, classification_reason: str, suspect_comp: str, diag_log_uuid: str
    ) -> None:
        """
        Extends the knowledge graph with facts for the specified manual inspection.

        :param prediction: prediction of the classification model (True -> POS, False -> NEG)
        :param classification_reason: diagnostic association or another classification instance
        :param suspect_comp: vehicle component to which the oscillogram belongs
        :param diag_log_uuid: ID of the diagnosis log to which the classification belongs
        """
        # either UUID of DA or UUID of another classification
        assert "diag_association_" in classification_reason or "manual_inspection_" in classification_reason \
               or "oscillogram_classification_" in classification_reason

        manual_inspection_uuid = "manual_inspection_" + uuid.uuid4().hex
        fact_list = [
            Fact((manual_inspection_uuid, RDF.type, self.onto_namespace["ManualInspection"].toPython())),
            Fact((manual_inspection_uuid, self.onto_namespace.prediction, prediction), property_fact=True),
            Fact((manual_inspection_uuid, self.onto_namespace.diagStep, diag_log_uuid))
        ]

        # connect to component
        sus_comp_uuid = self.knowledge_graph_query_tool.query_suspect_component_by_name(suspect_comp)[0].split("#")[1]
        fact_list.append(
            Fact((manual_inspection_uuid, self.onto_namespace.checks, sus_comp_uuid))
        )

        # set reason
        if "diag_association_" in classification_reason:
            fact_list.append(Fact((classification_reason, self.onto_namespace.ledTo, manual_inspection_uuid)))
        else:  # the reason is a classification instance (manual or osci)
            fact_list.append(Fact((classification_reason, self.onto_namespace.reasonFor, manual_inspection_uuid)))

        self.fuseki_connection.extend_knowledge_graph(fact_list)

    def extend_kg_with_parallel_rec_oscillogram_set_facts(self) -> str:
        """
        Extends the knowledge graph with facts for parallel recorded oscillograms.

        :return: UUID of oscillogram set
        """
        parallel_rec_osci_set_uuid = "parallel_rec_oscillogram_set_" + uuid.uuid4().hex
        fact_list = [
            Fact((parallel_rec_osci_set_uuid, RDF.type, self.onto_namespace["ParallelRecOscillogramSet"].toPython()))
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return parallel_rec_osci_set_uuid

    def extend_kg_with_oscillogram_recording(self, time_series: List[float]) -> str:
        """
        Extends the knowledge graph with facts for oscillogram recordings.

        :param time_series: oscillogram recording (voltage values)
        :return: UUID of generated oscillogram instance
        """
        osci_uuid = "oscillogram_" + uuid.uuid4().hex
        fact_list = [
            Fact((osci_uuid, RDF.type, self.onto_namespace["Oscillogram"].toPython())),
            Fact((osci_uuid, self.onto_namespace.time_series, str(time_series)), property_fact=True),
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return osci_uuid

    def extend_kg_with_fault_path(self, description: str, fault_cond_uuid: str, diag_log_uuid: str) -> str:
        """
        Extends the knowledge graph with fault path facts.

        :param description: fault path description
        :param fault_cond_uuid: UUID of fault condition
        :param diag_log_uuid: UUID of diagnosis log
        :return: fault path UUID
        """
        fault_path_uuid = "fault_path_" + uuid.uuid4().hex
        fact_list = [
            Fact((fault_path_uuid, RDF.type, self.onto_namespace["FaultPath"].toPython())),
            Fact((fault_path_uuid, self.onto_namespace.path_description, description), property_fact=True),
            Fact((fault_cond_uuid, self.onto_namespace.resultedIn, fault_path_uuid)),
            Fact((diag_log_uuid, self.onto_namespace.entails, fault_path_uuid))
        ]
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return fault_path_uuid

    def extend_kg_with_diag_log(self, max_num_of_parallel_rec: int, vehicle_uuid: str, dtc_list: List[str]) -> str:
        """
        Extends the knowledge graph with diagnosis log facts.

        :param max_num_of_parallel_rec: maximum number of parallel recordings based on workshop equipment
        :param vehicle_uuid: UUID of associated vehicle
        :param dtc_list: number of DTCs that are part of the diagnostic process (stored in vehicle ECU)
        :return: UUID of diagnosis log
        """
        diag_log_uuid = "diag_log_" + uuid.uuid4().hex
        fact_list = [
            Fact((diag_log_uuid, RDF.type, self.onto_namespace["DiagLog"].toPython())),
            Fact((diag_log_uuid, self.onto_namespace.date, date.today()), property_fact=True),
            Fact((diag_log_uuid, self.onto_namespace.max_num_of_parallel_rec, max_num_of_parallel_rec),
                 property_fact=True),
            Fact((diag_log_uuid, self.onto_namespace.createdFor, vehicle_uuid))
        ]
        for dtc in dtc_list:
            dtc_uuid = self.knowledge_graph_query_tool.query_dtc_instance_by_code(dtc)
            if len(dtc_uuid) == 1:
                fact_list.append(
                    Fact((dtc_uuid[0].split("#")[1], self.onto_namespace.appearsIn, diag_log_uuid))
                )
        self.fuseki_connection.extend_knowledge_graph(fact_list)
        return diag_log_uuid

    def generate_dtc_related_facts(self, dtc_knowledge: DTCKnowledge) -> list:
        """
        Generates all facts obtained from the DTC form / template to be entered into the knowledge graph and extends
        it with automatically obtained information from the dtc_parser.

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
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()

    # create some test instances
    list_of_dtcs = ["P2563", "P0333", "P1234", "P0987"]
    fault_path = "VTG-Abgasturbolader -> Ladedruck-Magnetventil -> Ladedruck-Regelventil"
    causing_dtc = "P2563"
    fault_cond_uuid = expert_knowledge_enhancer.knowledge_graph_query_tool.query_fault_condition_instance_by_code(
        causing_dtc
    )[0].split("#")[1]

    diag_log_uuid = expert_knowledge_enhancer.extend_kg_with_diag_log(4, "vehicle_39458359345382458", list_of_dtcs)
    expert_knowledge_enhancer.extend_kg_with_fault_path(fault_path, fault_cond_uuid, diag_log_uuid)
    osci_set_id = expert_knowledge_enhancer.extend_kg_with_parallel_rec_oscillogram_set_facts()
    oscillogram = [13.3, 13.6, 14.6, 16.7, 8.5, 9.7, 5.5, 3.6, 12.5, 12.7]
    heatmap = [0.4, 0.3, 0.7, 0.7, 0.8, 0.9, 0.3, 0.2]
    sus_comp = "VTG-Abgasturbolader"
    expert_knowledge_enhancer.extend_kg_with_oscillogram_classification_facts(0.45, "test_model_id", True, oscillogram,
                                                                              heatmap, osci_set_id, "GradCAM",
                                                                              "diag_association_3592495", sus_comp,
                                                                              diag_log_uuid)
    expert_knowledge_enhancer.extend_kg_with_oscillogram_classification_facts(0.85, "test_model_id", True, oscillogram,
                                                                              heatmap, osci_set_id, "GradCAM",
                                                                              "oscillogram_classification_3543595",
                                                                              sus_comp, diag_log_uuid)
    expert_knowledge_enhancer.extend_kg_with_manual_inspection_facts(False, "oscillogram_classification_45395859345",
                                                                     "Ladedruck-Magnetventil", diag_log_uuid)
