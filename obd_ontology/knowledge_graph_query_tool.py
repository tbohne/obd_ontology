#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List, Tuple

from termcolor import colored

from obd_ontology.config import ONTOLOGY_PREFIX, FUSEKI_URL
from obd_ontology.connection_controller import ConnectionController


class KnowledgeGraphQueryTool:
    """
    Library of numerous predefined SPARQL queries and response processing for accessing useful information stored in
    the knowledge graph hosted on a Fuseki server.
    """

    def __init__(self, kg_url: str = FUSEKI_URL) -> None:
        """
        Initializes the KG query tool.

        :param kg_url: URL for the server hosting the knowledge graph
        """
        self.ontology_prefix = ONTOLOGY_PREFIX
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX, fuseki_url=kg_url)

    def complete_ontology_entry(self, entry: str) -> str:
        """
        Completes the ontology entry for the specified concept / relation.

        :param entry: ontology entry (concept / relation) to be completed
        :return: completed ontology entry
        """
        return "<" + self.ontology_prefix.replace('#', '#' + entry) + ">"

    def query_fault_causes_by_dtc(self, dtc: str) -> List[str]:
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
        return [row['cause_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_fault_condition_by_dtc(self, dtc: str, verbose: bool = True) -> List[str]:
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
        return [row['condition_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_by_description(self, desc: str) -> List[str]:
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
        return [row['fc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_symptoms_by_dtc(self, dtc: str, verbose: bool = True) -> List[str]:
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
                ?dtc {code_entry} "{dtc}" .
                ?symptom a {symptom_entry} .
                ?condition {manifested_by_entry} ?symptom .
                ?symptom {symptom_desc_entry} ?symptom_desc .
            }}
            """
        return [row['symptom_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_indicates_by_dtc(self, dtc: str, verbose: bool = True) -> List[str]:
        """
        Queries the indicated subsystem for the specified DTC.

        :param dtc: diagnostic trouble code to query indicated subsystem for
        :param verbose: if true, logging is activated
        :return: indicated subsystem
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: indicated subsystem for " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        indicates_entry = self.complete_ontology_entry('indicates')
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        sub_name_entry = self.complete_ontology_entry('subsystem_name')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?sub_name WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {indicates_entry} ?subsystem .
                ?dtc {code_entry} "{dtc}" .
                ?subsystem a {subsystem_entry} .
                ?subsystem {sub_name_entry} ?sub_name .
            }}
            """
        return [row['sub_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_vehicle_part_by_subsystem(self, subsystem: str, verbose: bool = True) -> List[str]:
        """
        Queries the vehicle parts for the specified subsystem.

        :param subsystem: vehicle subsystem to query vehicle part(s) for
        :param verbose: if true, logging is activated
        :return: vehicle part(s)
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: vehicle part(s) for " + subsystem, "green", "on_grey", ["bold"]))
            print("########################################################################")
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        vehicle_part_entry = self.complete_ontology_entry('vehicle_part')
        sub_name_entry = self.complete_ontology_entry('subsystem_name')
        s = f"""
            SELECT ?vehicle_part WHERE {{
                ?subsystem a {subsystem_entry} .
                ?subsystem {sub_name_entry} "{subsystem}" .
                ?subsystem {vehicle_part_entry} ?vehicle_part .
            }}
            """
        return [row['vehicle_part']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_symptoms_by_desc(self, desc: str) -> List[str]:
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
        return [row['symptom']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_fault_cat_by_dtc(self, dtc: str, verbose: bool = True) -> List[str]:
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
        return [row['cat_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_cat_by_description(self, desc: str) -> List[str]:
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
        return [row['fc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_suspect_components_by_dtc(self, dtc: str, verbose: bool = True) -> List[str]:
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
        has_association_entry = self.complete_ontology_entry('hasAssociation')
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
                ?dtc {has_association_entry} ?da .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_components_by_subsystem_name(self, subsystem_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect components associated with the specified subsystem.

        :param subsystem_name: subsystem to query suspect components for
        :param verbose: if true, logging is activated
        :return: suspect components
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: suspect components for " + subsystem_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        contains_entry = self.complete_ontology_entry('contains')
        sus_comp_entry = self.complete_ontology_entry('SuspectComponent')
        subsystem_name_entry = self.complete_ontology_entry('subsystem_name')
        comp_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?sub a {subsystem_entry} .
                ?sub {contains_entry} ?comp .
                ?comp a {sus_comp_entry} .
                ?sub {subsystem_name_entry} "{subsystem_name}" .
                ?comp {comp_name_entry} ?comp_name .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_by_name(self, component_name: str) -> List[str]:
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
        return [row['comp']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_channel_by_name(self, chan_name: str) -> List[str]:
        """
        Queries an oscilloscope channel by its name.

        :param chan_name: name to query channel for
        :return: osci channel
        """
        print("########################################################################")
        print(colored("QUERY: osci channel by name - " + chan_name, "green", "on_grey", ["bold"]))
        print("########################################################################")
        chan_entry = self.complete_ontology_entry('Channel')
        chan_name_entry = self.complete_ontology_entry('channel_name')
        s = f"""
            SELECT ?chan WHERE {{
                ?chan a {chan_entry} .
                ?chan {chan_name_entry} ?chan_name .
                FILTER(STR(?chan_name) = "{chan_name}")
            }}
            """
        return [row['chan']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_vehicle_subsystem_by_name(self, subsystem_name: str) -> List[str]:
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
        return [row['subsystem']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_component_set_by_name(self, set_name: str) -> List[str]:
        """
        Queries a component set by its name.

        :param set_name: name to query component set for
        :return: component set
        """
        print("########################################################################")
        print(colored("QUERY: component set by name - " + set_name, "green", "on_grey", ["bold"]))
        print("########################################################################")
        component_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        s = f"""
            SELECT ?comp_set WHERE {{
                ?comp_set a {component_set_entry} .
                ?comp_set {set_name_entry} ?set_name .
                FILTER(STR(?set_name) = "{set_name}")
            }}
            """
        return [row['comp_set']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_vehicle_instance_by_vin(self, vin: str) -> List[str]:
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
        return [row['car']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_co_occurring_trouble_codes(self, dtc: str, verbose: bool = True) -> List[str]:
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
        return [row['other']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_vehicle_by_dtc(self, dtc: str, verbose: bool = True) -> List[Tuple[str, str, str, str]]:
        """
        Queries vehicles in which the specified DTC occurred in the past.

        :param dtc: diagnostic trouble code to query vehicles for
        :param verbose: if true, logging is activated
        :return: vehicles
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: vehicle associated with DTC " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        appears_in_entry = self.complete_ontology_entry('appearsIn')
        created_for_entry = self.complete_ontology_entry('createdFor')
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
                ?diag_log a {diag_log_entry} .
                ?dtc {appears_in_entry} ?diag_log .
                ?diag_log {created_for_entry} ?vehicle .
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
        return [(row['model']['value'], row['hsn']['value'], row['tsn']['value'], row['vin']['value']) for row in
                self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_dtc_instances(self, verbose: bool = True) -> List[str]:
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
        return [row['dtc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_fault_condition_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all fault condition instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all fault conditions stored in the knowledge graph
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: all fault condition instances:", "green", "on_grey", ["bold"]))
            print("########################################################################")
        fault_condition_entry = self.complete_ontology_entry('FaultCondition')
        condition_desc_entry = self.complete_ontology_entry('condition_description')
        s = f"""
            SELECT ?desc WHERE {{
                ?instance a {fault_condition_entry} .
                ?instance {condition_desc_entry} ?desc .
            }}
            """
        return [row['desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_instance_by_code(self, dtc: str) -> List[str]:
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
        return [row['fault_cond']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_fault_condition_instances_by_symptom(self, symptom: str) -> List[str]:
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
        s = f"""
            SELECT ?fault_cond WHERE {{
                ?fault_cond a {fault_cond_entry} .
                ?symptom a {symptom_entry} .
                ?fault_cond {manifested_by_entry} ?symptom .
                ?symptom {symptom_desc_entry} "{symptom}" .
            }}
            """
        return [row['fault_cond']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_dtc_instance_by_code(self, code: str) -> List[str]:
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
        return [row['dtc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_dtcs_by_suspect_comp_and_vehicle_subsystem(
            self, comp: str, subsystem: str, verbose: bool = True) -> List[str]:
        """
        Queries the DTCs associated with the specified suspect component and vehicle subsystem.

        :param comp: suspect component to query DTCs for
        :param subsystem: subsystem to query DTCs for
        :param verbose: if true, logging is activated
        :return: DTCs
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: DTCs by suspect component " + comp + " and subsystem " + subsystem,
                          "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        code_entry = self.complete_ontology_entry('code')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        comp_name_entry = self.complete_ontology_entry('component_name')
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        indicates_entry = self.complete_ontology_entry('indicates')
        sub_name_entry = self.complete_ontology_entry('subsystem_name')
        s = f"""
            SELECT ?code WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} ?code .
                ?diag_association a {diag_association_entry} .
                ?dtc {has_association_entry} ?diag_association .
                ?comp a {comp_entry} .
                ?diag_association {points_to_entry} ?comp .
                ?comp {comp_name_entry} "{comp}" .
                ?sub a {subsystem_entry} .
                ?dtc {indicates_entry} ?sub .
                ?sub {sub_name_entry} "{subsystem}" .
            }}
            """
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_diag_association_instance_by_dtc_and_sus_comp(
            self, dtc: str, comp: str, verbose: bool = True) -> List[str]:
        """
        Queries the diagnostic association instance for the specified code and suspect component.

        :param dtc: diagnostic trouble code to query diagnostic association for
        :param comp: suspect component to query diagnostic association for
        :param verbose: if true, logging is activated
        :return: diagnostic association instance
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: diagnostic association by dtc + suspect component: " + dtc + ", " +
                          comp, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        s = f"""
            SELECT ?diag_association WHERE {{
                ?diag_association a {diag_association_entry} .
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} "{dtc}" .
                ?dtc {has_association_entry} ?diag_association .
                ?sus a {suspect_component_entry} .
                ?sus {comp_name_entry} "{comp}" .
                ?diag_association {points_to_entry} ?sus .
            }}
            """
        return [row['diag_association']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_priority_id_by_dtc_and_sus_comp(self, dtc: str, comp: str, verbose: bool = True) -> List[str]:
        """
        Queries the priority ID of the diagnostic association for the specified code and suspect component.

        :param dtc: diagnostic trouble code to query priority ID for
        :param comp: suspect component to query priority ID for
        :param verbose: if true, logging is activated
        :return: priority ID
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: diagnostic association priority by dtc + suspect component: " + dtc + ", " +
                          comp, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        prio_entry = self.complete_ontology_entry('priority_id')
        s = f"""
            SELECT ?prio WHERE {{
                ?diag_association a {diag_association_entry} .
                ?diag_association  {prio_entry} ?prio .
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} "{dtc}" .
                ?dtc {has_association_entry} ?diag_association .
                ?sus a {suspect_component_entry} .
                ?sus {comp_name_entry} "{comp}" .
                ?diag_association {points_to_entry} ?sus .
            }}
            """
        return [row['prio']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_diag_association_by_dtc_and_sus_comp(self, dtc: str, comp: str, verbose: bool = True) -> List[str]:
        """
        Queries the diagnostic association for the specified code and suspect component.

        :param dtc: diagnostic trouble code to query diagnostic association for
        :param comp: suspect component to query diagnostic association for
        :param verbose: if true, logging is activated
        :return: diagnostic association instance
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: diagnostic association instance by dtc + suspect component: " + dtc + ", " +
                          comp, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        s = f"""
            SELECT ?diag_association WHERE {{
                ?diag_association a {diag_association_entry} .
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} "{dtc}" .
                ?dtc {has_association_entry} ?diag_association .
                ?sus a {suspect_component_entry} .
                ?sus {comp_name_entry} "{comp}" .
                ?diag_association {points_to_entry} ?sus .
            }}
            """
        return [row['diag_association']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_generated_heatmaps_by_dtc_and_sus_comp(self, dtc: str, comp: str, verbose: bool = True) -> List[str]:
        """
        Queries the generated heatmaps for the specified code and suspect component.

        :param dtc: diagnostic trouble code to query generated heatmaps for
        :param comp: suspect component to query generated heatmaps for
        :param verbose: if true, logging is activated
        :return: diagnostic association instance
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: generated heatmaps by dtc + suspect component: " + dtc + ", " +
                          comp, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        diag_association_entry = self.complete_ontology_entry('DiagnosticAssociation')
        suspect_component_entry = self.complete_ontology_entry('SuspectComponent')
        code_entry = self.complete_ontology_entry('code')
        has_association_entry = self.complete_ontology_entry('hasAssociation')
        comp_name_entry = self.complete_ontology_entry('component_name')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        heatmap_entry = self.complete_ontology_entry('generated_heatmap')
        s = f"""
            SELECT ?heatmap_entry WHERE {{
                ?diag_association a {diag_association_entry} .
                ?diag_association {heatmap_entry} ?heatmap_entry .
                ?dtc a {dtc_entry} .
                ?dtc {code_entry} "{dtc}" .
                ?dtc {has_association_entry} ?diag_association .
                ?sus a {suspect_component_entry} .
                ?sus {comp_name_entry} "{comp}" .
                ?diag_association {points_to_entry} ?sus .
            }}
            """
        return [row['heatmap_entry']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_dtcs_by_vin(self, vin: str) -> List[str]:
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
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_dtcs_by_model(self, model: str) -> List[str]:
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
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, True)]

    def query_oscilloscope_usage_by_suspect_component(self, component_name: str, verbose: bool = True) -> List[bool]:
        """
        Queries whether an oscilloscope should be used to diagnose the specified component.

        :param component_name: suspect component to determine oscilloscope usage for
        :param verbose: if true, logging is activated
        :return: true / false
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: oscilloscope usage by component name "
                          + component_name, "green", "on_grey", ["bold"]))
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
        return [True if row['use_oscilloscope']['value'] == "true" else False
                for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_affected_by_relations_by_suspect_component(self, component_name: str, verbose: bool = True) -> List[str]:
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
        return [row['affected_by']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_verifies_relation_by_suspect_component(self, component_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the vehicle component set that can be verified by the specified suspect component.

        :param component_name: suspect component to query verified component set for
        :param verbose: if true, logging is activated
        :return: vehicle component set name
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: verified component set by component name "
                          + component_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        verifies_entry = self.complete_ontology_entry('verifies')
        s = f"""
            SELECT ?set_name WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} "{component_name}" .
                ?set a {set_entry} .
                ?set {set_name_entry} ?set_name .
                ?comp {verifies_entry} ?set .
            }}
            """
        return [row['set_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_verifies_relations_by_component_set(self, set_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect components that can verify the specified component set.

        :param set_name: component set to query verifying suspect components for
        :param verbose: if true, logging is activated
        :return: suspect component names
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: verifying components by component set name "
                          + set_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        component_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        verifies_entry = self.complete_ontology_entry('verifies')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?comp_set a {component_set_entry} .
                ?comp_set {set_name_entry} "{set_name}" .
                ?comp a {comp_entry} .
                ?comp {name_entry} ?comp_name .
                ?comp {verifies_entry} ?comp_set .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_contains_relation_by_suspect_component(self, component_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the vehicle subsystem that the specified suspect component is part of.

        :param component_name: suspect component to query superior subsystem for
        :param verbose: if true, logging is activated
        :return: subsystem name
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: superior subsystem by component name "
                          + component_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        sub_name_entry = self.complete_ontology_entry('subsystem_name')
        contains_entry = self.complete_ontology_entry('contains')
        s = f"""
            SELECT ?sub_name WHERE {{
                ?comp a {comp_entry} .
                ?comp {name_entry} "{component_name}" .
                ?sub a {subsystem_entry} .
                ?sub {sub_name_entry} ?sub_name .
                ?sub {contains_entry} ?comp .
            }}
            """
        return [row['sub_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_contains_relation_by_subsystem(self, subsystem_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect components that are contained in the specified vehicle subsystem.

        :param subsystem_name: subsystem to query contained suspect components for
        :param verbose: if true, logging is activated
        :return: component names
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: components by subsystem name " + subsystem_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        subsystem_entry = self.complete_ontology_entry('VehicleSubsystem')
        sub_name_entry = self.complete_ontology_entry('subsystem_name')
        contains_entry = self.complete_ontology_entry('contains')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?sub a {subsystem_entry} .
                ?sub {sub_name_entry} "{subsystem_name}" .
                ?comp a {comp_entry} .
                ?comp {name_entry} ?comp_name .
                ?sub {contains_entry} ?comp .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_includes_relation_by_component_set(self, comp_set_name: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect components that are included in the specified component set.

        :param comp_set_name: component set to query included suspect components for
        :param verbose: if true, logging is activated
        :return: component names
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: components by component set name " + comp_set_name, "green", "on_grey", ["bold"]))
            print("########################################################################")
        comp_entry = self.complete_ontology_entry('SuspectComponent')
        name_entry = self.complete_ontology_entry('component_name')
        comp_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        includes_entry = self.complete_ontology_entry('includes')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?comp_set a {comp_set_entry} .
                ?comp_set {set_name_entry} "{comp_set_name}" .
                ?comp a {comp_entry} .
                ?comp {name_entry} ?comp_name .
                ?comp_set {includes_entry} ?comp .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_code_type_by_dtc(self, dtc: str, verbose: bool = True) -> List[str]:
        """
        Queries the code type for the specified DTC.

        :param dtc: DTC to query code type for
        :param verbose: if true, logging is activated
        :return: code type
        """
        if verbose:
            print("########################################################################")
            print(colored("QUERY: code type by DTC " + dtc, "green", "on_grey", ["bold"]))
            print("########################################################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        code_entry = self.complete_ontology_entry('code')
        type_entry = self.complete_ontology_entry('code_type')
        s = f"""
            SELECT ?code_type WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {type_entry} ?code_type .
                ?dtc {code_entry} "{dtc}" .
            }}
            """
        return [row['code_type']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_all_component_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all component instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all components stored in the knowledge graph
        """
        if verbose:
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
        return [row['name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_vehicle_instances(self, verbose: bool = True) -> List[Tuple[str, str, str, str, str]]:
        """
        Queries all vehicle instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all vehicles stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all vehicle instances")
            print("####################################")
        vehicle_entry = self.complete_ontology_entry('Vehicle')
        model_entry = self.complete_ontology_entry('model')
        hsn_entry = self.complete_ontology_entry('HSN')
        tsn_entry = self.complete_ontology_entry('TSN')
        vin_entry = self.complete_ontology_entry('VIN')
        s = f"""
            SELECT ?vehicle ?hsn ?tsn ?vin ?model WHERE {{
                ?vehicle a {vehicle_entry} .
                ?vehicle {hsn_entry} ?hsn .
                ?vehicle {tsn_entry} ?tsn .
                ?vehicle {vin_entry} ?vin .
                ?vehicle {model_entry} ?model .
            }}
            """
        return [
            (row['vehicle']['value'], row['hsn']['value'], row['tsn']['value'], row['vin']['value'],
             row['model']['value'])
            for row in self.fuseki_connection.query_knowledge_graph(s, verbose)
        ]

    def query_all_model_instances(self, verbose: bool = True) -> List[Tuple[str, str, str, str, str, str]]:
        """
        Queries all model instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all models stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all model instances")
            print("####################################")
        model_entry = self.complete_ontology_entry('Model')
        input_len_entry = self.complete_ontology_entry('input_length')
        exp_norm_meth_entry = self.complete_ontology_entry('exp_normalization_method')
        measuring_instruction_entry = self.complete_ontology_entry('measuring_instruction')
        model_id_entry = self.complete_ontology_entry('model_id')
        architecture_entry = self.complete_ontology_entry('architecture')
        s = f"""
            SELECT ?model ?input_len ?exp_norm_meth ?measuring_instruction ?model_id ?archi WHERE {{
                ?model a {model_entry} .
                ?model {input_len_entry} ?input_len .
                ?model {exp_norm_meth_entry} ?exp_norm_meth .
                ?model {measuring_instruction_entry} ?measuring_instruction .
                ?model {model_id_entry} ?model_id .
                ?model {architecture_entry} ?archi .
            }}
            """
        return [
            (row['model']['value'], row['input_len']['value'], row['exp_norm_meth']['value'],
             row['measuring_instruction']['value'], row['model_id']['value'], row['archi']['value'])
            for row in self.fuseki_connection.query_knowledge_graph(s, verbose)
        ]

    def query_all_channel_instances(self, verbose: bool = True) -> List[Tuple[str, str]]:
        """
        Queries all channel instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all channels stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all channel instances")
            print("####################################")
        channel_entry = self.complete_ontology_entry('Channel')
        channel_name_entry = self.complete_ontology_entry('channel_name')
        s = f"""
            SELECT ?chan ?chan_name WHERE {{
                ?chan a {channel_entry} .
                ?chan {channel_name_entry} ?chan_name .
            }}
            """
        return [
            (row['chan']['value'], row['chan_name']['value'])
            for row in self.fuseki_connection.query_knowledge_graph(s, verbose)
        ]

    def query_all_parallel_rec_oscillogram_set_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all parallel recorded oscillogram sets stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all parallel rec oscillogram sets stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all parallel rec oscillogram set instances")
            print("####################################")
        parallel_rec_set_entry = self.complete_ontology_entry('ParallelRecOscillogramSet')
        s = f"""
            SELECT ?osci_set WHERE {{
                ?osci_set a {parallel_rec_set_entry} .
            }}
            """
        return [row['osci_set']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_recorded_oscillograms(self, verbose: bool = True) -> List[str]:
        """
        Queries all recorded oscillograms stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all rec oscillograms stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all rec oscillogram instances")
            print("####################################")
        osci_entry = self.complete_ontology_entry('Oscillogram')
        s = f"""
            SELECT ?osci WHERE {{
                ?osci a {osci_entry} .
            }}
            """
        return [row['osci']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_oscillogram_classifications(self, verbose: bool = True) -> List[str]:
        """
        Queries all oscillogram classification instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all oscillogram classifications stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all oscillogram classification instances")
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        s = f"""
            SELECT ?osci_classification WHERE {{
                ?osci_classification a {osci_classification_entry} .
            }}
            """
        return [row['osci_classification']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_oscillogram_classification_by_heatmap(self, heatmap_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the oscillogram classification instance that produces the specified heatmap.

        :param heatmap_id: heatmap instance to query oscillogram classification for
        :param verbose: if true, logging is activated
        :return: all oscillogram classifications stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: oscillogram classification instances for the specified heatmap:", heatmap_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        produces_entry = self.complete_ontology_entry('produces')
        id_entry = self.complete_ontology_entry(heatmap_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        s = f"""
            SELECT ?osci_classification WHERE {{
                ?osci_classification a {osci_classification_entry} .
                ?heatmap a {heatmap_entry} .
                ?osci_classification {produces_entry} ?heatmap .
                FILTER(STR(?heatmap) = "{id_entry}") .
            }}
            """
        return [row['osci_classification']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_manual_inspection_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all manual inspection instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all manual inspections stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all manual inspection instances")
            print("####################################")
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        s = f"""
            SELECT ?manual_inspection WHERE {{
                ?manual_inspection a {manual_inspection_entry} .
            }}
            """
        return [row['manual_inspection']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_diag_log_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all diag log instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all diag logs stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all diag log instances")
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        s = f"""
            SELECT ?diag_log WHERE {{
                ?diag_log a {diag_log_entry} .
            }}
            """
        return [row['diag_log']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_fault_path_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all fault path instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all fault paths stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all fault path instances")
            print("####################################")
        fault_path_entry = self.complete_ontology_entry('FaultPath')
        s = f"""
            SELECT ?fault_path WHERE {{
                ?fault_path a {fault_path_entry} .
            }}
            """
        return [row['fault_path']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_model_id_by_osci_classification_id(self, osci_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the model ID for the specified oscillogram classification instance.

        :param osci_classification_id: ID of the oscillogram classification instance to query model ID for
        :param verbose: if true, logging is activated
        :return: model ID for oscillogram classification instance
        """
        if verbose:
            print("####################################")
            print("QUERY: model ID for the specified oscillogram classification:", osci_classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        id_entry = self.complete_ontology_entry(osci_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        model_id_entry = self.complete_ontology_entry('model_id')
        s = f"""
            SELECT ?model_id WHERE {{
                ?osci_classification a {osci_classification_entry} .
                FILTER(STR(?osci_classification) = "{id_entry}") .
                ?osci_classification {model_id_entry} ?model_id .
            }}
            """
        return [row['model_id']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_name_by_id(self, component_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect component name for the specified component ID.

        :param component_id: ID of the component instance to query name for
        :param verbose: if true, logging is activated
        :return: component name for component instance
        """
        if verbose:
            print("####################################")
            print("QUERY: suspect component name for the specified instance:", component_id)
            print("####################################")
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        id_entry = self.complete_ontology_entry(component_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        comp_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?sus_comp a {suspect_comp_entry} .
                FILTER(STR(?sus_comp) = "{id_entry}") .
                ?sus_comp {comp_name_entry} ?comp_name .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_uncertainty_by_osci_classification_id(
            self, osci_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the uncertainty for the specified oscillogram classification instance.

        :param osci_classification_id: ID of the oscillogram classification instance to query uncertainty for
        :param verbose: if true, logging is activated
        :return: uncertainty for oscillogram classification instance
        """
        if verbose:
            print("####################################")
            print("QUERY: uncertainty for the specified oscillogram classification:", osci_classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        id_entry = self.complete_ontology_entry(osci_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        uncertainty_entry = self.complete_ontology_entry('uncertainty')
        s = f"""
            SELECT ?uncertainty WHERE {{
                ?osci_classification a {osci_classification_entry} .
                FILTER(STR(?osci_classification) = "{id_entry}") .
                ?osci_classification {uncertainty_entry} ?uncertainty .
            }}
            """
        return [row['uncertainty']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_date_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the date for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query date for
        :param verbose: if true, logging is activated
        :return: date for diag log instance
        """
        if verbose:
            print("####################################")
            print("QUERY: date for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        date_entry = self.complete_ontology_entry('date')
        s = f"""
            SELECT ?date WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?diag_log {date_entry} ?date .
            }}
            """
        return [row['date']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_max_num_of_parallel_rec_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the max number of parallel recordings for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query max num of parallel rec for
        :param verbose: if true, logging is activated
        :return: max num of parallel rec for diag log instance
        """
        if verbose:
            print("####################################")
            print("QUERY: max num of parallel rec for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        max_num_of_parallel_rec_entry = self.complete_ontology_entry('max_num_of_parallel_rec')
        s = f"""
            SELECT ?max_num_of_parallel_rec WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?diag_log {max_num_of_parallel_rec_entry} ?max_num_of_parallel_rec .
            }}
            """
        return [row['max_num_of_parallel_rec']['value'] for row in
                self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_resulted_in_by_fault_path(self, fault_path_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault conditions resulting in the specified fault path instance.

        :param fault_path_id: ID of the fault path instance to query fault conditions for
        :param verbose: if true, logging is activated
        :return: fault conditions for fault path instance
        """
        if verbose:
            print("####################################")
            print("QUERY: fault conditions for the specified fault path:", fault_path_id)
            print("####################################")
        fault_path_entry = self.complete_ontology_entry('FaultPath')
        id_entry = self.complete_ontology_entry(fault_path_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        resulted_in_entry = self.complete_ontology_entry('resultedIn')
        s = f"""
            SELECT ?fault_cond WHERE {{
                ?fault_path a {fault_path_entry} .
                FILTER(STR(?fault_path) = "{id_entry}") .
                ?fault_cond {resulted_in_entry} ?fault_path .
            }}
            """
        return [row['fault_cond']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_dtcs_recorded_in_vehicle(self, vehicle_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the DTCs recorded in the specified vehicle.

        :param vehicle_id: ID of the vehicle to retrieve DTCs for
        :param verbose: if true, logging is activated
        :return: DTCs for the vehicle instance
        """
        if verbose:
            print("####################################")
            print("QUERY: DTCs for the specified vehicle:", vehicle_id)
            print("####################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        vehicle_entry = self.complete_ontology_entry('Vehicle')
        id_entry = self.complete_ontology_entry(vehicle_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        appears_in_entry = self.complete_ontology_entry('appearsIn')
        created_for_entry = self.complete_ontology_entry('createdFor')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?code WHERE {{
                ?vehicle a {vehicle_entry} .
                FILTER(STR(?vehicle) = "{id_entry}") .
                ?diag_log a {diag_log_entry} .
                ?dtc a {dtc_entry} .
                ?dtc {appears_in_entry} ?diag_log .
                ?diag_log {created_for_entry} ?vehicle .
                ?dtc {code_entry} ?code .
            }}
            """
        return [row['code']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_dtcs_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the DTCs for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query DTCs for
        :param verbose: if true, logging is activated
        :return: DTCs for diag log instance
        """
        if verbose:
            print("####################################")
            print("QUERY: DTCs for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        appears_in_entry = self.complete_ontology_entry('appearsIn')
        s = f"""
            SELECT ?dtc WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?dtc {appears_in_entry} ?diag_log .
            }}
            """
        return [row['dtc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_diag_steps_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the diagnostic steps for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query diag steps for
        :param verbose: if true, logging is activated
        :return: diag steps for diag log instance
        """
        if verbose:
            print("####################################")
            print("QUERY: diag steps for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        diag_step_entry = self.complete_ontology_entry('diagStep')
        s = f"""
            SELECT ?classification WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?classification {diag_step_entry} ?diag_log .
            }}
            """
        return [row['classification']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_path_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault path for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query fault path for
        :param verbose: if true, logging is activated
        :return: fault path for diag log instance
        """
        if verbose:
            print("####################################")
            print("QUERY: fault path for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        entails_entry = self.complete_ontology_entry('entails')
        s = f"""
            SELECT ?fault_path WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?diag_log {entails_entry} ?fault_path .
            }}
            """
        return [row['fault_path']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_path_description_by_id(self, fault_path_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault path description for the specified fault path ID.

        :param fault_path_id: ID of the fault path instance to query description for
        :param verbose: if true, logging is activated
        :return: fault path description for the specified ID
        """
        if verbose:
            print("####################################")
            print("QUERY: fault path description for the specified ID:", fault_path_id)
            print("####################################")
        fault_path_entry = self.complete_ontology_entry('FaultPath')
        id_entry = self.complete_ontology_entry(fault_path_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        desc_entry = self.complete_ontology_entry('path_description')
        s = f"""
            SELECT ?path_desc WHERE {{
                ?fault_path a {fault_path_entry} .
                FILTER(STR(?fault_path) = "{id_entry}") .
                ?fault_path {desc_entry} ?path_desc .
            }}
            """
        return [row['path_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_fault_condition_description_by_id(self, fault_condition_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the fault condition description for the specified fault condition ID.

        :param fault_condition_id: ID of the fault condition instance to query description for
        :param verbose: if true, logging is activated
        :return: fault condition description for the specified ID
        """
        if verbose:
            print("####################################")
            print("QUERY: fault condition description for the specified ID:", fault_condition_id)
            print("####################################")
        fault_condition_entry = self.complete_ontology_entry('FaultCondition')
        id_entry = self.complete_ontology_entry(fault_condition_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        desc_entry = self.complete_ontology_entry('condition_description')
        s = f"""
            SELECT ?cond_desc WHERE {{
                ?fault_cond a {fault_condition_entry} .
                FILTER(STR(?fault_cond) = "{id_entry}") .
                ?fault_cond {desc_entry} ?cond_desc .
            }}
            """
        return [row['cond_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_vehicle_by_diag_log(self, diag_log_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the vehicle for the specified diag log instance.

        :param diag_log_id: ID of the diag log instance to query vehicle for
        :param verbose: if true, logging is activated
        :return: vehicle for diag log instance
        """
        if verbose:
            print("####################################")
            print("QUERY: vehicle for the specified diag log:", diag_log_id)
            print("####################################")
        diag_log_entry = self.complete_ontology_entry('DiagLog')
        id_entry = self.complete_ontology_entry(diag_log_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        created_for_entry = self.complete_ontology_entry('createdFor')
        s = f"""
            SELECT ?vehicle WHERE {{
                ?diag_log a {diag_log_entry} .
                FILTER(STR(?diag_log) = "{id_entry}") .
                ?diag_log {created_for_entry} ?vehicle .
            }}
            """
        return [row['vehicle']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_time_series_by_oscillogram_instance(self, osci_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the time series for the specified oscillogram instance.

        :param osci_id: ID of the oscillogram instance to query time series for
        :param verbose: if true, logging is activated
        :return: time series for oscillogram instance
        """
        if verbose:
            print("####################################")
            print("QUERY: time series for the specified oscillogram:", osci_id)
            print("####################################")
        osci_entry = self.complete_ontology_entry('Oscillogram')
        id_entry = self.complete_ontology_entry(osci_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        time_series_entry = self.complete_ontology_entry('time_series')
        s = f"""
            SELECT ?time_series WHERE {{
                ?osci a {osci_entry} .
                FILTER(STR(?osci) = "{id_entry}") .
                ?osci {time_series_entry} ?time_series .
            }}
            """
        return [row['time_series']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_oscillograms_by_parallel_osci_set(self, osci_set_id: str, verbose: bool = True) -> List[str]:
        """
        Queries all parallel recorded oscillograms for the specified set.

        :param osci_set_id: ID of parallel recorded oscillogram set
        :param verbose: if true, logging is activated
        :return: parallel recorded oscillograms part of the set
        """
        if verbose:
            print("####################################")
            print("QUERY: all parallel rec oscillograms for the specified set:", osci_set_id)
            print("####################################")
        parallel_rec_set_entry = self.complete_ontology_entry('ParallelRecOscillogramSet')
        id_entry = self.complete_ontology_entry(osci_set_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        part_of_entry = self.complete_ontology_entry('partOf')
        s = f"""
            SELECT ?oscillogram WHERE {{
                ?osci_set a {parallel_rec_set_entry} .
                FILTER(STR(?osci_set) = "{id_entry}") .
                ?oscillogram {part_of_entry} ?osci_set .
            }}
            """
        return [row['oscillogram']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_oscillogram_by_classification_instance(
            self, osci_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the oscillogram instance for the specified classification.

        :param osci_classification_id: ID of oscillogram classification instance
        :param verbose: if true, logging is activated
        :return: oscillogram instance
        """
        if verbose:
            print("####################################")
            print("QUERY: oscillogram instance for the specified classification:", osci_classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        id_entry = self.complete_ontology_entry(osci_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        classifies_entry = self.complete_ontology_entry('classifies')
        s = f"""
            SELECT ?oscillogram WHERE {{
                ?osci_classification a {osci_classification_entry} .
                FILTER(STR(?osci_classification) = "{id_entry}") .
                ?osci_classification {classifies_entry} ?oscillogram .
            }}
            """
        return [row['oscillogram']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_by_classification(self, classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the suspect component for the specified classification.

        :param classification_id: ID of classification instance
        :param verbose: if true, logging is activated
        :return: suspect component
        """
        if verbose:
            print("####################################")
            print("QUERY: suspect component for the specified classification:", classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        checks_entry = self.complete_ontology_entry('checks')
        s = f"""
            SELECT ?comp WHERE {{
                {{ ?classification a {osci_classification_entry} . }}
                UNION
                {{ ?classification a {manual_inspection_entry} . }}
                FILTER(STR(?classification) = "{id_entry}") .
                ?classification {checks_entry} ?comp .
            }}
            """
        return [row['comp']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_name_by_model(self, model_id: str, verbose: bool = False) -> List[str]:
        """
        Queries the suspect component for the specified classification model.

        :param model_id: ID of model instance
        :param verbose: if true, logging is activated
        :return: suspect component
        """
        if verbose:
            print("####################################")
            print("QUERY: suspect component for the specified classification model:", model_id)
            print("####################################")
        model_entry = self.complete_ontology_entry('Model')
        id_entry = self.complete_ontology_entry(model_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        assesses_entry = self.complete_ontology_entry('assesses')
        comp_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp_name WHERE {{
                {{ ?model a {model_entry} . }}
                FILTER(STR(?model) = "{id_entry}") .
                ?model {assesses_entry} ?comp .
                ?comp {comp_name_entry} ?comp_name .
            }}
            """
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_input_chan_req_by_model(self, model_id: str, verbose: bool = False) -> List[Tuple[str, str]]:
        """
        Queries the input channel requirements for the specified model.

        :param model_id: ID of model instance
        :param verbose: if true, logging is activated
        :return: input channel requirements
        """
        if verbose:
            print("####################################")
            print("QUERY: input channel requirements for the specified model:", model_id)
            print("####################################")
        model_entry = self.complete_ontology_entry('Model')
        id_entry = self.complete_ontology_entry(model_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        has_req_entry = self.complete_ontology_entry('hasRequirement')
        chan_idx_entry = self.complete_ontology_entry('channel_idx')
        s = f"""
            SELECT ?input_chan_req ?chan_idx WHERE {{
                {{ ?model a {model_entry} . }}
                FILTER(STR(?model) = "{id_entry}") .
                ?model {has_req_entry} ?input_chan_req .
                ?input_chan_req {chan_idx_entry} ?chan_idx .
            }}
            """
        return [(row['input_chan_req']['value'], row['chan_idx']['value']) for row in
                self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_channel_by_input_req(self, input_req_id: str, verbose: bool = False) -> List[Tuple[str, str]]:
        """
        Queries the channel for the specified input requirements.

        :param input_req_id: ID of input req instance
        :param verbose: if true, logging is activated
        :return: channel
        """
        if verbose:
            print("####################################")
            print("QUERY: channel for the specified input requirements:", input_req_id)
            print("####################################")
        input_req_entry = self.complete_ontology_entry('InputChannelRequirement')
        id_entry = self.complete_ontology_entry(input_req_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        expects_entry = self.complete_ontology_entry('expects')
        channel_name_entry = self.complete_ontology_entry('channel_name')
        s = f"""
            SELECT ?chan ?chan_name WHERE {{
                {{ ?input_req a {input_req_entry} . }}
                FILTER(STR(?input_req) = "{id_entry}") .
                ?input_req {expects_entry} ?chan .
                ?chan {channel_name_entry} ?chan_name .
            }}
            """
        return [(row['chan']['value'], row['chan_name']['value']) for row in
                self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_component_name_by_channel(self, channel_id: str, verbose: bool = False) -> List[Tuple[str, str]]:
        """
        Queries the suspect component ('hasChannel') for the specified channel.

        :param channel_id: ID of channel
        :param verbose: if true, logging is activated
        :return: suspect component (via 'hasChannel')
        """
        if verbose:
            print("####################################")
            print("QUERY: suspect component ('hasChannel') for the specified channel:", channel_id)
            print("####################################")
        channel_entry = self.complete_ontology_entry('Channel')
        id_entry = self.complete_ontology_entry(channel_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        has_chan_entry = self.complete_ontology_entry('hasChannel')
        comp_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp ?comp_name WHERE {{
                ?chan a {channel_entry} .
                FILTER(STR(?chan) = "{id_entry}") .
                ?comp {has_chan_entry} ?chan .
                ?comp {comp_name_entry} ?comp_name .
            }}
            """
        return [(row['comp']['value'], row['comp_name']['value']) for row in
                self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_models_by_channel(self, channel_id: str, verbose: bool = False) -> List[Tuple[str]]:
        """
        Queries the classification models for the specified channel.

        :param channel_id: ID of channel
        :param verbose: if true, logging is activated
        :return: models
        """
        if verbose:
            print("####################################")
            print("QUERY: classification models for the specified channel:", channel_id)
            print("####################################")
        channel_entry = self.complete_ontology_entry('Channel')
        id_entry = self.complete_ontology_entry(channel_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        has_req_entry = self.complete_ontology_entry('hasRequirement')
        expects_entry = self.complete_ontology_entry('expects')
        model_entry = self.complete_ontology_entry('Model')
        s = f"""
            SELECT ?model WHERE {{
                ?chan a {channel_entry} .
                FILTER(STR(?chan) = "{id_entry}") .
                ?model a {model_entry} .
                ?model {has_req_entry} ?input_req .
                ?input_req {expects_entry} ?chan .
            }}
            """
        return [row['model']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_suspect_components_by_channel(self, channel_id: str, verbose: bool = False) -> List[Tuple[str, str]]:
        """
        Queries the suspect components ('hasCOI') for the specified channel.

        :param channel_id: ID of channel
        :param verbose: if true, logging is activated
        :return: suspect components (via 'hasCOI')
        """
        if verbose:
            print("####################################")
            print("QUERY: suspect components ('hasCOI') for the specified channel:", channel_id)
            print("####################################")
        channel_entry = self.complete_ontology_entry('Channel')
        id_entry = self.complete_ontology_entry(channel_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        has_coi_entry = self.complete_ontology_entry('hasCOI')
        comp_name_entry = self.complete_ontology_entry('component_name')
        s = f"""
            SELECT ?comp ?comp_name WHERE {{
                ?chan a {channel_entry} .
                FILTER(STR(?chan) = "{id_entry}") .
                ?comp {has_coi_entry} ?chan .
                ?comp {comp_name_entry} ?comp_name .
            }}
            """
        return [(row['comp']['value'], row['comp_name']['value']) for row in
                self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_reason_for_classification(self, osci_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (other classification) for the specified classification.

        :param osci_classification_id: ID of oscillogram classification instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose:
            print("####################################")
            print("QUERY: classification reason for the specified classification:", osci_classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        id_entry = self.complete_ontology_entry(osci_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        reason_for_entry = self.complete_ontology_entry('reasonFor')
        s = f"""
            SELECT ?reason_for WHERE {{
                ?osci_classification a {osci_classification_entry} .
                FILTER(STR(?osci_classification) = "{id_entry}") .
                ?reason_for {reason_for_entry} ?osci_classification .
            }}
            """
        return [row['reason_for']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_led_to_for_classification(self, osci_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (diag association) for the specified classification.

        :param osci_classification_id: ID of oscillogram classification instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose:
            print("####################################")
            print("QUERY: classification reason for the specified classification:", osci_classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        id_entry = self.complete_ontology_entry(osci_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        led_to_entry = self.complete_ontology_entry('ledTo')
        s = f"""
            SELECT ?led_to WHERE {{
                ?osci_classification a {osci_classification_entry} .
                FILTER(STR(?osci_classification) = "{id_entry}") .
                ?led_to {led_to_entry} ?osci_classification .
            }}
            """
        return [row['led_to']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_reason_for_inspection(self, manual_inspection_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (other classification) for the specified inspection.

        :param manual_inspection_id: ID of manual inspection instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose:
            print("####################################")
            print("QUERY: classification reason for the specified manual inspection:", manual_inspection_id)
            print("####################################")
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(manual_inspection_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        reason_for_entry = self.complete_ontology_entry('reasonFor')
        s = f"""
            SELECT ?reason_for WHERE {{
                ?manual_inspection a {manual_inspection_entry} .
                FILTER(STR(?manual_inspection) = "{id_entry}") .
                ?reason_for {reason_for_entry} ?manual_inspection .
            }}
            """
        return [row['reason_for']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_led_to_for_inspection(self, manual_inspection_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the reason (diag association) for the specified inspection.

        :param manual_inspection_id: ID of manual inspection instance
        :param verbose: if true, logging is activated
        :return: classification reason
        """
        if verbose:
            print("####################################")
            print("QUERY: classification reason for the specified manual inspection:", manual_inspection_id)
            print("####################################")
        manual_inspection_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(manual_inspection_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        led_to_entry = self.complete_ontology_entry('ledTo')
        s = f"""
            SELECT ?led_to WHERE {{
                ?manual_inspection a {manual_inspection_entry} .
                FILTER(STR(?manual_inspection) = "{id_entry}") .
                ?led_to {led_to_entry} ?manual_inspection .
            }}
            """
        return [row['led_to']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_prediction_by_classification(self, classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the prediction for the specified classification.

        :param classification_id: ID of classification instance
        :param verbose: if true, logging is activated
        :return: prediction
        """
        if verbose:
            print("####################################")
            print("QUERY: prediction for the specified classification:", classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        manual_classification_entry = self.complete_ontology_entry('ManualInspection')
        id_entry = self.complete_ontology_entry(classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        pred_entry = self.complete_ontology_entry('prediction')
        s = f"""
            SELECT ?pred WHERE {{
                {{ ?classification a {osci_classification_entry} . }}
                UNION
                {{ ?classification a {manual_classification_entry} . }}
                FILTER(STR(?classification) = "{id_entry}") .
                ?classification {pred_entry} ?pred .
            }}
            """
        return [row['pred']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_heatmap_by_classification_instance(self, osci_classification_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the heatmap instance for the specified classification.

        :param osci_classification_id: ID of oscillogram classification instance
        :param verbose: if true, logging is activated
        :return: generated heatmap
        """
        if verbose:
            print("####################################")
            print("QUERY: heatmap instance for the specified classification:", osci_classification_id)
            print("####################################")
        osci_classification_entry = self.complete_ontology_entry('OscillogramClassification')
        id_entry = self.complete_ontology_entry(osci_classification_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        produces_entry = self.complete_ontology_entry('produces')
        s = f"""
            SELECT ?heatmap WHERE {{
                ?osci_classification a {osci_classification_entry} .
                FILTER(STR(?osci_classification) = "{id_entry}") .
                ?osci_classification {produces_entry} ?heatmap .
            }}
            """
        return [row['heatmap']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_generation_method_by_heatmap(self, heatmap_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the heatmap generation method for the specified heatmap instance.

        :param heatmap_id: ID of heatmap instance
        :param verbose: if true, logging is activated
        :return: heatmap generation method
        """
        if verbose:
            print("####################################")
            print("QUERY: heatmap generation method for the specified heatmap instance:", heatmap_id)
            print("####################################")
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        id_entry = self.complete_ontology_entry(heatmap_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        generation_method_entry = self.complete_ontology_entry('generation_method')
        s = f"""
            SELECT ?gen_method WHERE {{
                ?heatmap a {heatmap_entry} .
                FILTER(STR(?heatmap) = "{id_entry}") .
                ?heatmap {generation_method_entry} ?gen_method .
            }}
            """
        return [row['gen_method']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_heatmap_string_by_heatmap(self, heatmap_id: str, verbose: bool = True) -> List[str]:
        """
        Queries the heatmap values for the specified heatmap instance.

        :param heatmap_id: ID of heatmap instance
        :param verbose: if true, logging is activated
        :return: heatmap values (string)
        """
        if verbose:
            print("####################################")
            print("QUERY: heatmap values for the specified heatmap instance:", heatmap_id)
            print("####################################")
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        id_entry = self.complete_ontology_entry(heatmap_id)
        id_entry = id_entry.replace('<', '').replace('>', '')
        heatmap_values_entry = self.complete_ontology_entry('generated_heatmap')
        s = f"""
            SELECT ?gen_heatmap WHERE {{
                ?heatmap a {heatmap_entry} .
                FILTER(STR(?heatmap) = "{id_entry}") .
                ?heatmap {heatmap_values_entry} ?gen_heatmap .
            }}
            """
        return [row['gen_heatmap']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_symptom_instances(self) -> List[str]:
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
        return [row['desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, False)]

    def query_all_vehicle_subsystem_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all subsystem instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all vehicle subsystems stored in the knowledge graph
        """
        if verbose:
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
        return [row['subsystem_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_heatmap_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all heatmap instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all heatmaps stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all heatmap instances")
            print("####################################")
        heatmap_entry = self.complete_ontology_entry('Heatmap')
        s = f"""
            SELECT ?heatmap WHERE {{
                ?heatmap a {heatmap_entry} .
            }}
            """
        return [row['heatmap']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    def query_all_component_set_instances(self, verbose: bool = True) -> List[str]:
        """
        Queries all component set instances stored in the knowledge graph.

        :param verbose: if true, logging is activated
        :return: all component sets stored in the knowledge graph
        """
        if verbose:
            print("####################################")
            print("QUERY: all component set instances")
            print("####################################")
        component_set_entry = self.complete_ontology_entry('ComponentSet')
        set_name_entry = self.complete_ontology_entry('set_name')
        s = f"""
            SELECT ?set_name WHERE {{
                ?comp_set a {component_set_entry} .
                ?comp_set {set_name_entry} ?set_name .
            }}
            """
        return [row['set_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s, verbose)]

    @staticmethod
    def print_res(res: list) -> None:
        """
        Prints the specified query results.

        :param res: list of query results
        """
        for row in res:
            print("--> ", row)


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool()
    qt.print_res(qt.query_all_dtc_instances())
    error_code = "P2563"
    suspect_comp_name = "Ladedruck-Regelventil"
    vehicle_subsystem_name = "SubsystemA"
    fault_category_desc = "{powertrain (engine, transmission, and associated accessories)," \
                          " ---, vehicle speed control, idle control systems, and auxiliary inputs, ---}"
    fault_cond_desc = "Ladedrucksteller-Positionssensor / Signal unplausibel"
    symptom_desc = "Glühkontrollleuchte leuchtet"
    dummy_vin = "1234567890ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    dummy_model = "Mazda 3"
    qt.print_res(qt.query_fault_causes_by_dtc(error_code))
    qt.print_res(qt.query_fault_condition_by_dtc(error_code))
    qt.print_res(qt.query_symptoms_by_dtc(error_code))
    qt.print_res(qt.query_fault_cat_by_dtc(error_code))
    qt.print_res(qt.query_suspect_components_by_dtc(error_code))
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
    qt.print_res(qt.query_priority_id_by_dtc_and_sus_comp(error_code, suspect_comp_name))
    qt.print_res(qt.query_diag_association_by_dtc_and_sus_comp(error_code, suspect_comp_name))
    qt.print_res(qt.query_generated_heatmaps_by_dtc_and_sus_comp(error_code, suspect_comp_name))
    qt.print_res(qt.query_vehicle_instance_by_vin(dummy_vin))
    qt.print_res(qt.query_dtcs_by_vin(dummy_vin))
    qt.print_res(qt.query_dtcs_by_model(dummy_model))
    qt.print_res(qt.query_oscilloscope_usage_by_suspect_component(suspect_comp_name))
    qt.print_res(qt.query_affected_by_relations_by_suspect_component(suspect_comp_name))
    qt.print_res(qt.query_code_type_by_dtc(error_code))
    qt.print_res(qt.query_all_component_set_instances(False))
    qt.print_res(qt.query_all_heatmap_instances(False))
