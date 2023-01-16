#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import pathlib

import rdflib
from obd_ontology.config import ONTOLOGY_PREFIX, KNOWLEDGE_GRAPH_FILE
from obd_ontology.connection_controller import ConnectionController
from termcolor import colored


class KnowledgeGraphQueryTool:
    """
    Library of predefined queries for accessing useful information stored in the knowledge graph.
    Works with both local knowledge graph (specified .owl file) and hosted knowledge graph on Fuseki server.
    """

    def __init__(self, local_kb=False) -> None:
        self.ontology_prefix = ONTOLOGY_PREFIX
        self.graph = rdflib.Graph()
        self.local_kb = local_kb
        if local_kb:
            self.init_local_knowledge_base()
        else:
            self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)

    def init_local_knowledge_base(self) -> None:
        """
        Initializes the local knowledge base (locally stored .owl file).
        """
        self.graph = self.graph.parse(str(pathlib.Path(__file__).parent.resolve()) + "/" + KNOWLEDGE_GRAPH_FILE,
                                      format='xml')

    def complete_ontology_entry(self, entry: str) -> str:
        """
        Completes the ontology entry for the specified concept / relation.

        :param entry: ontology entry (concept / relation) to be completed
        :return: completed ontology entry
        """
        return "<" + self.ontology_prefix.replace('#', '#' + entry) + ">"

    def query_fault_causes_by_dtc(self, dtc: str) -> list:
        """
        Queries the fault causes for the specified DTC.

        :param dtc: diagnostic trouble code to query fault causes for
        :return: fault causes
        """
        print("########################################################################")
        print(colored("QUERY: fault causes for " + dtc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        represents_entry = self.complete_ontology_entry('represents')
        fault_cause_entry = self.complete_ontology_entry('FaultCause')
        has_cause_entry = self.complete_ontology_entry('hasCause')
        cause_desc_entry = self.complete_ontology_entry('cause_description')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?cause_desc WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {represents_entry} ?condition .
                ?dtc {code_entry} ?dtc_code .
                ?cause a {fault_cause_entry} .
                ?condition {has_cause_entry} ?cause .
                ?cause {cause_desc_entry} ?cause_desc .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.cause_desc for row in self.graph.query(s)]
        return [row['cause_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_fault_condition_by_dtc(self, dtc: str, verbose: bool = True) -> list:
        """
        Queries the fault condition for the specified DTC.

        :param dtc: diagnostic trouble code to query fault condition for
        :param verbose: if true, logging is activated
        :return: fault condition
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: fault condition description for " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        represents_entry = self.complete_ontology_entry('represents')
        condition_desc_entry = self.complete_ontology_entry('condition_description')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?condition_desc WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {represents_entry} ?condition .
                ?dtc {code_entry} ?dtc_code .
                ?condition {condition_desc_entry} ?condition_desc .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.condition_desc for row in self.graph.query(s)]
        return [row['condition_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_by_description(self, desc: str) -> list:
        """
        Queries the fault condition instance for the specified description.

        :param desc: description to query fault condition instance for
        :return: fault condition instance
        """
        print("########################################################################")
        print(colored("QUERY: fault condition for " + desc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        fault_condition_entry = self.complete_ontology_entry('FaultCondition')
        condition_desc_entry = self.complete_ontology_entry('condition_description')
        s = f"""
            SELECT ?fc WHERE {{
                ?fc a {fault_condition_entry} .
                ?fc {condition_desc_entry} ?desc
                FILTER(STR(?desc) = "{desc}")
            }}
            """
        if self.local_kb:
            return [row.condition_desc for row in self.graph.query(s)]
        return [row['fc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_symptoms_by_dtc(self, dtc: str, verbose: bool = True) -> list:
        """
        Queries the symptoms for the specified DTC.

        :param dtc: diagnostic trouble code to query symptoms for
        :param verbose: if true, logging is activated
        :return: symptoms
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: symptoms for " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        represents_entry = self.complete_ontology_entry('represents')
        symptom_entry = self.complete_ontology_entry('Symptom')
        manifested_by_entry = self.complete_ontology_entry('manifestedBy')
        symptom_desc_entry = self.complete_ontology_entry('symptom_description')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?symptom_desc WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {represents_entry} ?condition .
                ?dtc {code_entry} ?dtc_code .
                ?symptom a {symptom_entry} .
                ?condition {manifested_by_entry} ?symptom .
                ?symptom {symptom_desc_entry} ?symptom_desc .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.symptom_desc for row in self.graph.query(s)]
        return [row['symptom_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_symptoms_by_desc(self, desc: str) -> list:
        """
        Queries the symptom instance for the specified description.

        :param desc: symptom description to query instance for
        :return: symptom instance
        """
        print("########################################################################")
        print(colored("QUERY: symptom instance for " + desc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        symptom_entry = self.complete_ontology_entry('Symptom')
        symptom_desc_entry = self.complete_ontology_entry('symptom_description')
        s = f"""
            SELECT ?symptom WHERE {{
                ?symptom a {symptom_entry} .
                ?symptom {symptom_desc_entry} ?symptom_desc .
                FILTER(STR(?symptom_desc) = "{desc}")
            }}
            """
        if self.local_kb:
            return [row.symptom_desc for row in self.graph.query(s)]
        return [row['symptom']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_corrective_actions_by_dtc(self, dtc: str) -> list:
        """
        Queries the corrective actions for the specified DTC.

        :param dtc: diagnostic trouble code to query corrective actions for
        :return: corrective actions
        """
        print("########################################################################")
        print(colored("QUERY: corrective actions for " + dtc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        represents_entry = self.complete_ontology_entry('represents')
        deletes_entry = self.complete_ontology_entry('deletes')
        resolves_entry = self.complete_ontology_entry('resolves')
        condition_entry = self.complete_ontology_entry('FaultCondition')
        action_entry = self.complete_ontology_entry('CorrectiveAction')
        action_desc_entry = self.complete_ontology_entry('action_description')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?action_desc WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {represents_entry} ?condition .
                ?dtc {code_entry} ?dtc_code .
                ?action {deletes_entry} ?dtc .
                ?action {resolves_entry} ?condition .
                ?condition a {condition_entry} .
                ?action a {action_entry} .
                ?action {action_desc_entry} ?action_desc .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.action_desc for row in self.graph.query(s)]
        return [row['action_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_fault_cat_by_dtc(self, dtc: str, verbose: bool = True) -> list:
        """
        Queries the fault category of the specified DTC.

        :param dtc: diagnostic trouble code to query fault category for
        :param verbose: if true, logging is activated
        :return: fault category
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: fault category for " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        has_cat_entry = self.complete_ontology_entry('hasCategory')
        fault_cat = self.complete_ontology_entry('FaultCategory')
        cat_desc_entry = self.complete_ontology_entry('category_description')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?cat_desc WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {has_cat_entry} ?cat .
                ?dtc {code_entry} ?dtc_code .
                ?cat a {fault_cat} .
                ?cat {cat_desc_entry} ?cat_desc .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.cat_name for row in self.graph.query(s)]
        return [row['cat_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_cat_by_description(self, desc: str) -> list:
        """
        Queries the fault category instance by the specified fault description.

        :param desc: fault description to query fault category instance for
        :return: fault category instance
        """
        print("########################################################################")
        print(colored("QUERY: fault category instance for " + desc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        fault_cat = self.complete_ontology_entry('FaultCategory')
        cat_desc_entry = self.complete_ontology_entry('category_description')
        s = f"""
            SELECT ?fc WHERE {{
                ?fc a {fault_cat} .
                ?fc {cat_desc_entry} ?fc_desc .
                FILTER(STR(?fc_desc) = "{desc}")
            }}
            """
        if self.local_kb:
            return [row.cat_name for row in self.graph.query(s)]
        return [row['fc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_measuring_pos_by_dtc(self, dtc: str) -> list:
        """
        Queries the measuring positions for the specified DTC.

        :param dtc: diagnostic trouble code to query measuring positions for
        :return: measuring positions
        """
        print("########################################################################")
        print(colored("QUERY: measuring pos for " + dtc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        implies_entry = self.complete_ontology_entry('implies')
        measuring_pos = self.complete_ontology_entry('MeasuringPos')
        pos_desc_entry = self.complete_ontology_entry('position_description')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?measuring_pos_desc WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc  {implies_entry} ?measuring_pos .
                ?dtc {code_entry} ?dtc_code .
                ?measuring_pos a {measuring_pos} .
                ?measuring_pos {pos_desc_entry} ?measuring_pos_desc .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.measuring_pos_desc for row in self.graph.query(s)]
        return [row['measuring_pos_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_suspect_component_by_dtc(self, dtc: str, verbose: bool = True) -> list:
        """
        Queries the suspect components associated with the specified DTC.

        :param dtc: diagnostic trouble codes to query suspect components for
        :param verbose: if true, logging is activated
        :return: suspect components
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: suspect components for " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        has_entry = self.complete_ontology_entry('has')
        component_name_entry = self.complete_ontology_entry('component_name')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?dtc a {dtc_entry} .
                ?comp a {suspect_comp_entry} .
                ?comp {component_name_entry} ?comp_name .
                ?da a {diag_association_entry} .
                ?dtc {code_entry} "{dtc}" .
                ?da {points_to_entry} ?comp .
                ?dtc {has_entry} ?da .
            }}
            """
        if self.local_kb:
            return [row.comp_name for row in self.graph.query(s)]
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_by_name(self, component_name: str) -> list:
        """
        Queries a suspect component by its component name.

        :param component_name: name to query suspect component for
        :return: suspect component
        """
        print("########################################################################")
        print(colored("QUERY: suspect components by name - " + component_name, "green", "on_grey", ["bold"]))
        print("########################################################################")
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        component_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp WHERE {{
                ?comp a {suspect_comp_entry} .
                ?comp {component_name_entry} ?comp_name .
                FILTER(STR(?comp_name) = "{component_name}")
            }}
            """
        if self.local_kb:
            return [row.comp_name for row in self.graph.query(s)]
        return [row['comp']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_vehicle_subsystem_by_name(self, subsystem_name: str) -> list:
        """
        Queries a vehicle subsystem by its name.

        :param subsystem_name: name to query subsystem for
        :return: subsystem
        """
        print("########################################################################")
        print(colored("QUERY: vehicle subsystem by name - " + subsystem_name, "green", "on_grey", ["bold"]))
        print("########################################################################")
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        subsystem_name_entry = self.complete_ontology_entry('subsystem_name')
        s = f"""
            SELECT ?subsystem WHERE {{
                ?subsystem a {subsystem_entry} .
                ?subsystem {subsystem_name_entry} ?subsystem_name .
                FILTER(STR(?subsystem_name) = "{subsystem_name}")
            }}
            """
        if self.local_kb:
            return [row.comp_name for row in self.graph.query(s)]
        return [row['subsystem']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_vehicle_instance_by_vin(self, vin: str) -> list:
        """
        Queries a vehicle instance by the vehicle identification number.

        :param vin: vehicle identification number to query specific instance for
        :return: vehicle instance
        """
        print("########################################################################")
        print(colored("QUERY: vehicle instance by VIN " + vin, "green", "on_grey", ["bold"]))
        print("########################################################################")
        vehicle_entry = self.complete_ontology_entry('Vehicle')
        vin_entry = self.complete_ontology_entry('VIN')
        s = f"""
            SELECT ?car WHERE {{
                ?car a {vehicle_entry} .
                ?car {vin_entry} "{vin}" .
            }}
            """
        if self.local_kb:
            return [row.comp_name for row in self.graph.query(s)]
        return [row['car']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_co_occurring_trouble_codes(self, dtc: str, verbose: bool = True) -> list:
        """
        Queries DTCs regularly occurring with the specified DTC.

        :param dtc: diagnostic trouble code to query associated other DTCs for
        :param verbose: if true, logging is activated
        :return: co-occurring DTCs
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: DTCs occurring with " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        occurs_with_dtc_entry = self.complete_ontology_entry('occurs_with_DTC')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?other WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {occurs_with_dtc_entry} ?other .
                ?dtc {code_entry} ?dtc_code .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.other for row in self.graph.query(s)]
        return [row['other']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_vehicle_by_dtc(self, dtc: str) -> list:
        """
        Queries vehicles where the specified DTC has occurred in the past.

        :param dtc: diagnostic trouble code to query vehicles for
        :return: vehicles
        """
        print("########################################################################")
        print(colored("QUERY: vehicle associated with DTC " + dtc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        occurred_in_entry = self.complete_ontology_entry('occurredIn')
        fault_cond_class = self.complete_ontology_entry('FaultCondition')
        vehicle_class = self.complete_ontology_entry('Vehicle')
        represents_entry = self.complete_ontology_entry('represents')
        hsn_entry = self.complete_ontology_entry('HSN')
        tsn_entry = self.complete_ontology_entry('TSN')
        vin_entry = self.complete_ontology_entry('VIN')
        model_entry = self.complete_ontology_entry('model')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?model ?hsn ?tsn ?vin WHERE {{
                ?fc {occurred_in_entry} ?vehicle .
                ?fc a {fault_cond_class} .
                ?vehicle a {vehicle_class} .
                ?dtc {represents_entry} ?fc .
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} ?dtc_code .
                ?vehicle {hsn_entry} ?hsn .
                ?vehicle {tsn_entry} ?tsn .
                ?vehicle {vin_entry} ?vin .
                ?vehicle {model_entry} ?model .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [(str(row.model), str(row.hsn), str(row.tsn), str(row.vin)) for row in self.graph.query(s)]
        return [(row['model']['value'], row['hsn']['value'], row['tsn']['value'], row['vin']['value']) for row in
                self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_all_dtc_instances(self, verbose: bool = True) -> list:
        """
        Queries all DTC instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all DTCs stored in the knowledge graph
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: all DTC instances:", "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?dtc WHERE {{
                ?instance a {dtc_entry} .
                ?instance {code_entry} ?dtc .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['dtc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_instance_by_code(self, dtc: str) -> list:
        """
        Queries the fault condition instance represented by the specified DTC.

        :param dtc: diagnostic trouble code to query fault condition instance for
        :return: fault condition instance
        """
        print("########################################################################")
        print(colored("QUERY: fault condition instance by code " + dtc, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        code_entry = self.complete_ontology_entry('code')
        represents_entry = self.complete_ontology_entry('represents')
        s = f"""
            SELECT ?fault_cond WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} "{dtc}" .
                ?dtc {represents_entry} ?fault_cond .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['fault_cond']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_fault_condition_instances_by_symptom(self, symptom: str) -> list:
        """
        Queries the fault condition instances manifested by the specified symptom.

        :param symptom: symptom to query fault condition instances for
        :return: fault condition instances
        """
        print("########################################################################")
        print(colored("QUERY: fault condition instances by symptom " + symptom, "green", "on_grey", ["bold"]))
        print("########################################################################")
        symptom_entry = self.complete_ontology_entry('Symptom')
        fault_cond_entry = self.complete_ontology_entry('FaultCondition')
        manifested_by_entry = self.complete_ontology_entry('manifestedBy')
        symptom_desc_entry = self.complete_ontology_entry('symptom_description')
        cond_desc_entry = self.complete_ontology_entry('condition_description')
        s = f"""
            SELECT ?fault_cond WHERE {{
                ?fault_cond a {fault_cond_entry} .
                ?symptom a {symptom_entry} .
                ?fault_cond {manifested_by_entry} ?symptom .
                ?symptom {symptom_desc_entry} "{symptom}" .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['fault_cond']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_dtc_instance_by_code(self, code: str) -> list:
        """
        Queries the DTC instance for the specified code.

        :param code: code to query DTC instance for
        :return: DTC instance
        """
        print("########################################################################")
        print(colored("QUERY: DTC instance by code " + code, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?dtc WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} "{code}" .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['dtc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_diagnostic_association_by_dtc_and_sus_comp(self, dtc: str, comp: str, verbose: bool = True) -> list:
        """
        Queries the diagnostic association, i.e., the priority, for the specified code and suspect component.

        :param dtc: diagnostic trouble code to query diagnostic association for
        :param comp: suspect component to query diagnostic association for
        :param verbose: if true, logging is activated
        :return: diagnostic association instance
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: diagnostic association (priority) by dtc + suspect component: " + dtc + ", " +
                          comp, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_entry = self.complete_ontology_entry('has')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        prio_entry = self.complete_ontology_entry('priority_id')
        s = f"""
            SELECT ?prio WHERE {{
                ?diag_association a {diag_association_entry} .
                ?diag_association  {prio_entry} ?prio .
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} "{dtc}" .
                ?dtc {has_entry} ?diag_association .
                ?sus a {suspect_component_entry} .
                ?sus {comp_name_entry} "{comp}" .
                ?diag_association {points_to_entry} ?sus .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['prio']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_dtcs_by_vin(self, vin: str) -> list:
        """
        Queries the DTCs (diagnostic trouble codes) for the specified VIN (vehicle identification number).

        :param vin: VIN to query DTCs for
        :return: DTCs
        """
        print("########################################################################")
        print(colored("QUERY: DTCs by VIN " + vin, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        vehicle_entry = self.complete_ontology_entry('Vehicle')
        code_entry = self.complete_ontology_entry('code')
        vin_entry = self.complete_ontology_entry('VIN')
        s = f"""
            SELECT ?code WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} ?code .
                ?vehicle a {vehicle_entry} .
                ?vehicle {vin_entry} "{vin}" .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_dtcs_by_model(self, model: str) -> list:
        """
        Queries the DTCs (diagnostic trouble codes) for the specified car model.

        :param model: car model to retrieve recorded DTCs for
        :return: DTCs
        """
        print("########################################################################")
        print(colored("QUERY: DTCs by car model " + model, "green", "on_grey", ["bold"]))
        print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        vehicle_entry = self.complete_ontology_entry('Vehicle')
        code_entry = self.complete_ontology_entry('code')
        model_entry = self.complete_ontology_entry('model')
        s = f"""
            SELECT ?code WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} ?code .
                ?vehicle a {vehicle_entry} .
                ?vehicle {model_entry} "{model}" .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_oscilloscope_usage_by_suspect_component(self, component_name: str, verbose: bool = True) -> list:
        """
        Queries whether an oscilloscope should be used to diagnose the specified component.

        :param component_name: suspect component to determine oscilloscope usage for
        :param verbose: if true, logging is activated
        :return: true / false
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: oscilloscope usage by component name " + component_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        oscilloscope_entry = self.complete_ontology_entry('use_oscilloscope')
        s = f"""
            SELECT ?use_oscilloscope WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} "{component_name}" .
                ?comp {oscilloscope_entry} ?use_oscilloscope .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [True if row['use_oscilloscope']['value'] == "true" else False
                for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_affected_by_relations_by_suspect_component(self, component_name: str, verbose: bool = True) -> list:
        """
        Queries the affecting components for the specified suspect component.

        :param component_name: suspect component to query affected_by relations for
        :param verbose: if true, logging is activated
        :return: affecting components
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: affecting components by component name "
                          + component_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        affected_by_entry = self.complete_ontology_entry('affected_by')
        s = f"""
            SELECT ?affected_by WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} "{component_name}" .
                ?comp {affected_by_entry} ?affected_by .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['affected_by']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_verifies_relation_by_suspect_component(self, component_name: str, verbose: bool = True) -> list:
        """
        Queries the vehicle subsystem that can be verified by the specified suspect component.

        :param component_name: suspect component to query verified subsystem for
        :param verbose: if true, logging is activated
        :return: subsystem name
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: verified subsystem by component name "
                          + component_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        sub_name_entry = self.complete_ontology_entry('subsystem_name')
        verifies_entry = self.complete_ontology_entry('verifies')
        s = f"""
            SELECT ?sub_name WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} "{component_name}" .
                ?sub a {subsystem_entry} .
                ?sub {sub_name_entry} ?sub_name .
                ?comp {verifies_entry} ?sub .
            }}
            """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['sub_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_all_component_instances(self) -> list:
        """
        Queries all component instances stored in the knowledge graph.

        :return: all components stored in the knowledge graph
        """
        print("####################################")
        print("QUERY: all component instances")
        print("####################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        s = f"""
        SELECT ?name WHERE {{
            ?comp a {comp_entry} .
            ?comp {name_entry} ?name.
        }}
        """
        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_all_symptom_instances(self) -> list:
        """
        Queries all symptom instances stored in the knowledge graph.

        :return: all symptoms stored in the knowledge graph
        """
        print("####################################")
        print("QUERY: all symptom instances")
        print("####################################")
        symptom_entry = self.complete_ontology_entry('Symptom')
        symptom_desc_entry = self.complete_ontology_entry('symptom_description')
        s = f"""
        SELECT ?desc WHERE {{
            ?symp a {symptom_entry} .
            ?symp {symptom_desc_entry} ?desc.
        }}
        """

        if self.local_kb:
            return [row.dtc for row in self.graph.query(s)]
        return [row['desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_all_vehicle_subsystem_instances(self) -> list:
        """
        Queries all subsystem instances stored in the knowledge graph.

        :return: all vehicle subsystems stored in the knowledge graph
        """
        print("####################################")
        print("QUERY: all vehicle subsystem instances")
        print("####################################")
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        subsystem_name_entry = self.complete_ontology_entry('subsystem_name')
        s = f"""
            SELECT ?subsystem_name WHERE {{
                ?subsystem a {subsystem_entry} .
                ?subsystem {subsystem_name_entry} ?subsystem_name .
            }}
            """
        if self.local_kb:
            return [row.comp_name for row in self.graph.query(s)]
        return [row['subsystem_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    @staticmethod
    def print_res(res: list) -> None:
        """
        Prints the specified query results.

        :param res: list of query results
        """
        for row in res:
            print("--> ", row)


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool(local_kb=False)
    qt.print_res(qt.query_all_dtc_instances())
    error_code = "P2563"
    suspect_comp_name = "Ladedruck-Regelventil"
    vehicle_subsystem_name = "SubsystemA"
    fault_category_desc = "{powertrain (engine, transmission, and associated accessories)," \
                          " ---, vehicle speed control, idle control systems, and auxiliary inputs, ---}"
    fault_cond_desc = "Ladedrucksteller-Positionssensor / Signal unplausibel"
    symptom_desc = "Glühkontrollleuchte leuchtet"
    vin = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    model = "Mazda 3"
    qt.print_res(qt.query_fault_causes_by_dtc(error_code))
    qt.print_res(qt.query_fault_condition_by_dtc(error_code))
    qt.print_res(qt.query_symptoms_by_dtc(error_code))
    qt.print_res(qt.query_corrective_actions_by_dtc(error_code))
    qt.print_res(qt.query_fault_cat_by_dtc(error_code))
    qt.print_res(qt.query_measuring_pos_by_dtc(error_code))
    qt.print_res(qt.query_suspect_component_by_dtc(error_code))
    qt.print_res(qt.query_co_occurring_trouble_codes(error_code))
    qt.print_res(qt.query_vehicle_by_dtc(error_code))
    qt.print_res(qt.query_fault_condition_instance_by_code(error_code))
    qt.print_res(qt.query_suspect_component_by_name(suspect_comp_name))
    qt.print_res(qt.query_vehicle_subsystem_by_name(vehicle_subsystem_name))
    qt.print_res(qt.query_dtc_instance_by_code(error_code))
    qt.print_res(qt.query_fault_cat_by_description(fault_category_desc))
    qt.print_res(qt.query_fault_condition_by_description(fault_cond_desc))
    qt.print_res(qt.query_symptoms_by_desc(symptom_desc))
    qt.print_res(qt.query_fault_condition_instances_by_symptom(symptom_desc))
    qt.print_res(qt.query_diagnostic_association_by_dtc_and_sus_comp(error_code, suspect_comp_name))
    qt.print_res(qt.query_vehicle_instance_by_vin(vin))
    qt.print_res(qt.query_dtcs_by_vin(vin))
    qt.print_res(qt.query_dtcs_by_model(model))
    qt.print_res(qt.query_oscilloscope_usage_by_suspect_component(suspect_comp_name))
    qt.print_res(qt.query_affected_by_relations_by_suspect_component(suspect_comp_name))
