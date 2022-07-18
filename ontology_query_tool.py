#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import rdflib
import pathlib

ONTOLOGY_FILE = "obd_ontology.owl"
ONTOLOGY_PREFIX = "<http://www.semanticweb.org/diag_ontology#>"


class OntologyQueryTool:

    def __init__(self):
        self.ontology_prefix = ONTOLOGY_PREFIX
        self.graph = rdflib.Graph()
        self.graph = self.graph.parse(str(pathlib.Path(__file__).parent.resolve()) + "/" + ONTOLOGY_FILE, format='xml')

    def complete_ontology_entry(self, entry):
        return self.ontology_prefix.replace('#', '#' + entry)

    def process_res(self, res):
        return [str(row).split(self.ontology_prefix.replace("<", "").replace(">", ""))[1].replace("'),)", "") for row in res]

    def query_fault_causes_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: fault causes for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        represents_entry = self.complete_ontology_entry('represents')
        fault_cause_entry = self.complete_ontology_entry('FaultCause')
        has_cause_entry = self.complete_ontology_entry('hasCause')
        s = f"""
            SELECT ?cause WHERE {{
                {dtc_entry} {represents_entry} ?condition .
                ?cause a {fault_cause_entry} .
                ?condition {has_cause_entry} ?cause .
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_fault_condition_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: fault condition for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        represents_entry = self.complete_ontology_entry('represents')
        s = f"""
            SELECT ?condition WHERE {{
                {dtc_entry} {represents_entry} ?condition .
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_symptoms_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: symptoms for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        represents_entry = self.complete_ontology_entry('represents')
        symptom_entry = self.complete_ontology_entry('Symptom')
        manifested_by_entry = self.complete_ontology_entry('manifestedBy')
        s = f"""
            SELECT ?symptom WHERE {{
                {dtc_entry} {represents_entry} ?condition .
                ?symptom a {symptom_entry} .
                ?condition {manifested_by_entry} ?symptom .
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_corrective_actions_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: corrective actions for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        represents_entry = self.complete_ontology_entry('represents')
        deletes_entry = self.complete_ontology_entry('deletes')
        resolves_entry = self.complete_ontology_entry('resolves')
        condition_entry = self.complete_ontology_entry('FaultCondition')
        action_entry = self.complete_ontology_entry('CorrectiveAction')
        s = f"""
            SELECT ?action WHERE {{
                {dtc_entry} {represents_entry} ?condition .
                ?action {deletes_entry} {dtc_entry} .
                ?action {resolves_entry} ?condition .
                ?condition a {condition_entry} .
                ?action a {action_entry} .
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_fault_description_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: fault description for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        has_description_entry = self.complete_ontology_entry('hasDescription')
        fault_description = self.complete_ontology_entry('FaultDescription')
        dtc_class = self.complete_ontology_entry('DTC')
        s = f"""
            SELECT ?description WHERE {{
                {dtc_entry} {has_description_entry} ?description .
                ?description a {fault_description} .
                {dtc_entry} a {dtc_class}
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_fault_cat_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: fault category for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        has_cat_entry = self.complete_ontology_entry('hasCategory')
        fault_cat = self.complete_ontology_entry('FaultCategory')
        dtc_class = self.complete_ontology_entry('DTC')
        s = f"""
            SELECT ?cat WHERE {{
                {dtc_entry} {has_cat_entry} ?cat .
                ?cat a {fault_cat} .
                {dtc_entry} a {dtc_class}
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_measuring_pos_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: measuring pos for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        implies_entry = self.complete_ontology_entry('implies')
        measuring_pos = self.complete_ontology_entry('MeasuringPos')
        dtc_class = self.complete_ontology_entry('DTC')
        s = f"""
            SELECT ?measuring_pos WHERE {{
                {dtc_entry} {implies_entry} ?measuring_pos .
                ?measuring_pos a {measuring_pos} .
                {dtc_entry} a {dtc_class}
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_suspect_component_by_dtc(self, dtc):
        print("####################################")
        print("QUERY: suspect components for", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        points_to_entry = self.complete_ontology_entry('pointsTo')
        suspect_comp_entry = self.complete_ontology_entry('SuspectComponent')
        dtc_class = self.complete_ontology_entry('DTC')
        s = f"""
            SELECT ?comp WHERE {{
                {dtc_entry} {points_to_entry} ?comp .
                ?comp a {suspect_comp_entry} .
                {dtc_entry} a {dtc_class}
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_dtc_occurring_with_the_specified_dtc(self, dtc):
        print("####################################")
        print("QUERY: DTCs occurring with", dtc)
        print("####################################")
        dtc_entry = self.complete_ontology_entry(dtc)
        occurs_with_entry = self.complete_ontology_entry('occursWith')
        dtc_class = self.complete_ontology_entry('DTC')
        s = f"""
            SELECT ?dtc WHERE {{
                {dtc_entry} {occurs_with_entry} ?dtc .
                ?dtc a {dtc_class} .
                {dtc_entry} a {dtc_class}
            }}
            """
        return self.process_res(self.graph.query(s))

    def query_all_dtc_instances(self):
        print("####################################")
        print("QUERY: all DTC instances")
        print("####################################")
        instance_entry = self.complete_ontology_entry('DTC')
        s = f"""
            SELECT ?instance WHERE {{
                ?instance a {instance_entry} .
            }}
            """
        return self.process_res(self.graph.query(s))

    @staticmethod
    def print_res(res):
        for row in res:
            print("--> ", row)


if __name__ == '__main__':
    oqt = OntologyQueryTool()
    oqt.print_res(oqt.query_all_dtc_instances())
    dtc = "P0138"
    oqt.print_res(oqt.query_fault_causes_by_dtc(dtc))
    oqt.print_res(oqt.query_fault_condition_by_dtc(dtc))
    oqt.print_res(oqt.query_symptoms_by_dtc(dtc))
    oqt.print_res(oqt.query_corrective_actions_by_dtc(dtc))
    oqt.print_res(oqt.query_fault_description_by_dtc(dtc))
    oqt.print_res(oqt.query_fault_cat_by_dtc(dtc))
    oqt.print_res(oqt.query_measuring_pos_by_dtc(dtc))
    oqt.print_res(oqt.query_suspect_component_by_dtc(dtc))
    oqt.print_res(oqt.query_dtc_occurring_with_the_specified_dtc(dtc))
