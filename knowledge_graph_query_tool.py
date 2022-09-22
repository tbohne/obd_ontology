#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import pathlib

import rdflib

from config import ONTOLOGY_PREFIX, KNOWLEDGE_GRAPH_FILE
from connection_controller import ConnectionController


class KnowledgeGraphQueryTool:

    def __init__(self, local_kb=False):
        self.ontology_prefix = ONTOLOGY_PREFIX
        self.graph = rdflib.Graph()
        self.local_kb = local_kb
        if local_kb:
            self.init_local_knowledge_base()
        else:
            self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)

    def init_local_knowledge_base(self):
        self.graph = self.graph.parse(str(pathlib.Path(__file__).parent.resolve()) + "/" + KNOWLEDGE_GRAPH_FILE,
                                      format='xml')

    def complete_ontology_entry(self, entry):
        return self.ontology_prefix.replace('#', '#' + entry)

    def process_res(self, res):
        return [str(row).split(self.ontology_prefix.replace("<", "").replace(">", ""))[1].replace("'),)", "") for row in
                res]

    def query_fault_causes_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: fault causes for", dtc)
        print("####################################")
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
        return [row['cause_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_fault_condition_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: fault condition for", dtc)
        print("####################################")
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
        return [row['condition_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_symptoms_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: symptoms for", dtc)
        print("####################################")
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
        return [row['symptom_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_corrective_actions_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: corrective actions for", dtc)
        print("####################################")
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
        return [row['action_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_fault_cat_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: fault category for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        has_cat_entry = self.complete_ontology_entry('hasCategory')
        fault_cat = self.complete_ontology_entry('FaultCategory')
        cat_name_entry = self.complete_ontology_entry('category_name')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?cat_name WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {has_cat_entry} ?cat .
                ?dtc {code_entry} ?dtc_code .
                ?cat a {fault_cat} .
                ?cat {cat_name_entry} ?cat_name .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.cat_name for row in self.graph.query(s)]
        return [row['cat_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_measuring_pos_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: measuring pos for", dtc)
        print("####################################")
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
        return [row['measuring_pos_desc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_suspect_component_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: suspect components for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry('DTC')
        points_to_entry = self.complete_ontology_entry('pointsTo')
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        component_name_entry = self.complete_ontology_entry('component_name')
        code_entry = self.complete_ontology_entry('code')
        s = f"""
            SELECT ?comp_name WHERE {{
                ?dtc a {dtc_entry} .
                ?dtc {points_to_entry} ?comp .
                ?dtc {code_entry} ?dtc_code .
                ?comp a {suspect_comp_entry} .
                ?comp {component_name_entry} ?comp_name .
                FILTER(STR(?dtc_code) = "{dtc}")
            }}
            """
        if self.local_kb:
            return [row.comp_name for row in self.graph.query(s)]
        return [row['comp_name']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_dtc_occurring_with_the_specified_dtc(self, dtc):
        print("####################################")
        print("QUERY: DTCs occurring with", dtc)
        print("####################################")
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
        return [row['other']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    def query_vehicle_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: vehicle associated with DTC ", dtc)
        print("####################################")
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
                self.fuseki_connection.query_knowledge_graph(s)]

    def query_all_dtc_instances(self):
        print("####################################")
        print("QUERY: all DTC instances")
        print("####################################")
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
        return [row['dtc']['value'] for row in self.fuseki_connection.query_knowledge_graph(s)]

    @staticmethod
    def print_res(res):
        for row in res:
            print("--> ", row)


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool(local_kb=False)
    qt.print_res(qt.query_all_dtc_instances())
    dtc = "P2563"
    qt.print_res(qt.query_fault_causes_by_dtc(dtc))
    qt.print_res(qt.query_fault_condition_by_dtc(dtc))
    qt.print_res(qt.query_symptoms_by_dtc(dtc))
    qt.print_res(qt.query_corrective_actions_by_dtc(dtc))
    qt.print_res(qt.query_fault_cat_by_dtc(dtc))
    qt.print_res(qt.query_measuring_pos_by_dtc(dtc))
    qt.print_res(qt.query_suspect_component_by_dtc(dtc))
    qt.print_res(qt.query_dtc_occurring_with_the_specified_dtc(dtc))
    qt.print_res(qt.query_vehicle_by_dtc(dtc))
