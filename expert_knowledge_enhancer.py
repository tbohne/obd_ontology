#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from config import ONTOLOGY_PREFIX
from connection_controller import ConnectionController
from expert_knowledge_parser import ExpertKnowledgeParser


class ExpertKnowledgeEnhancer:

    def __init__(self, knowledge_file):
        self.knowledge_parser = ExpertKnowledgeParser(knowledge_file)
        # establish connection to Apache Jena Fuseki server
        self.fuseki_connection = ConnectionController(namespace=ONTOLOGY_PREFIX)

    def extend_knowledge_graph(self):
        self.knowledge_parser.parse_knowledge()
        print(self.knowledge_parser)

    def enhance_expert_knowledge(self):
        self.add_dtc()
        self.add_fault_condition()
        self.add_fault_causes()
        self.add_fault_symptoms()
        self.add_suspect_components()
        self.add_fault_category()
        self.add_measuring_positions()
        self.add_corrective_actions()

    def add_dtc(self):
        self.dtc_obj = self.onto.DTC()
        self.dtc_obj.code.append(self.dtc)
        # TODO: retrieve from DB
        dtc_occurring_with = ["PXXXX", "PYYYY"]
        for other_dtc in dtc_occurring_with:
            self.dtc_obj.occurs_with_DTC.append(other_dtc)

    def add_fault_condition(self):
        # TODO: retrieve from DB
        fault_condition = "Dummy fault condition.."
        fc = self.onto.FaultCondition()
        fc.condition_description.append(fault_condition)
        self.dtc_obj.represents.append(fc)

    def add_fault_causes(self):
        # TODO: retrieve from DB
        fault_causes = ["causeOne", "causeTwo", "causeThree"]
        for fault in fault_causes:
            cause = self.onto.FaultCause()
            cause.cause_description.append(fault)
            fault_condition = list(self.dtc_obj.represents)[0]
            fault_condition.hasCause.append(cause)

    def add_fault_symptoms(self):
        # TODO: retrieve from DB
        symptoms = ["sympOne", "sympTwo", "sympThree"]
        for symptom in symptoms:
            s = self.onto.Symptom()
            s.symptom_description.append(symptom)
            fault_condition = list(self.dtc_obj.represents)[0]
            fault_condition.manifestedBy.append(s)

    def add_suspect_components(self):
        # TODO: retrieve from DB
        sus_components = ["susOne", "susTwo", "susThree"]
        for sus in sus_components:
            comp = self.onto.SuspectComponent()
            comp.component_name.append(sus)
            self.dtc_obj.pointsTo.append(comp)

    def add_fault_category(self):
        # TODO: retrieve from DB
        fault_cat = "category_A"
        cat = self.onto.FaultCategory()
        cat.category_name.append(fault_cat)
        self.dtc_obj.hasCategory.append(cat)

    def add_measuring_positions(self):
        # TODO: retrieve from DB
        measuring_pos = ["pos_A", "pos_B", "pos_C"]
        for pos in measuring_pos:
            measuring_position = self.onto.MeasuringPos()
            measuring_position.position_description.append(pos)
            self.dtc_obj.implies.append(measuring_position)

    def add_corrective_actions(self):
        # TODO: retrieve from DB
        corrective_actions = ["perform_test_A", "check_sensor_B", "apply_C"]
        fault_condition = list(self.dtc_obj.represents)[0]
        for act in corrective_actions:
            action = self.onto.CorrectiveAction()
            action.action_description.append(act)
            action.deletes.append(self.dtc_obj)
            action.resolves.append(fault_condition)
            self.onto.CorrectiveAction(action)


if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer("templates/expert_knowledge_template.txt")
    expert_knowledge_enhancer.extend_knowledge_graph()
