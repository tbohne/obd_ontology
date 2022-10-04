#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from dtc_knowledge import DTCKnowledge
from component_knowledge import ComponentKnowledge


class ExpertKnowledgeParser:
    """
    Parses OBD-related expert knowledge from template file (cf. `templates/dtc_expert_template.txt`,
    `templates/component_expert_template`, `templates/subsystem_expert_template.txt`).
    """

    def __init__(self, ) -> None:
        pass

    @staticmethod
    def parse_dtc_expert_template(lines: list) -> DTCKnowledge:
        """
        Parses the DTC expert template.

        :param lines: lines of the knowledge template
        :return: parsed DTC knowledge
        """
        dtc = ""
        occurs_with = []
        fault_condition = ""
        symptoms = []
        suspect_components = []

        cat_cnt = 0
        for line in lines:
            if "###" in line:
                cat_cnt += 1  # next category
                continue

            # should be data entry
            assert line[0] == "-"
            line = line[2:].strip()

            if cat_cnt == 1:
                dtc = line
            elif cat_cnt == 2:
                occurs_with.append(line)
            elif cat_cnt == 3:
                fault_condition = line
            elif cat_cnt == 4:
                symptoms.append(line)
            elif cat_cnt == 5:
                suspect_components.append(line)

        return DTCKnowledge(dtc, occurs_with, fault_condition, symptoms, suspect_components)

    @staticmethod
    def parse_component_expert_template(lines: list) -> list:
        """
        Parses the suspect component expert template.

        :param lines: lines of the knowledge template
        :return: parsed component knowledge
        """
        suspect_components = []
        # skip description etc.
        lines = [line for line in lines if line[0] != "\n" and line[0] != "#"]

        for line in lines:
            # should be data entry
            assert "-" in line[0:5]
            if line[0] == "-":  # new component
                suspect_component, oscilloscope = line[2:].strip().split(" ")
                oscilloscope = True if "ja" in oscilloscope.lower() else False
            else:  # complete entry
                affected_by = [other_comp.strip() for other_comp in line[6:].split(",")]
                suspect_components.append(ComponentKnowledge(suspect_component.strip(), oscilloscope, affected_by))
        return suspect_components

    def parse_subsystem_expert_template(self, lines: list) -> None:
        pass

    def parse_knowledge(self, knowledge_file: str) -> None:
        """
        Parses the OBD-related expert knowledge.

        :param knowledge_file: expert knowledge file to be parsed
        """
        with open(knowledge_file) as f:
            lines = f.readlines()

        # only keep the actual data + headlines (categories)
        lines = [line for line in lines if line.count("#") in [0, 3] and line != "\n"]

        if "dtc" in knowledge_file:
            return self.parse_dtc_expert_template(lines)
        elif "component" in knowledge_file:
            return self.parse_component_expert_template(lines)
        elif "subsystem" in knowledge_file:
            return self.parse_subsystem_expert_template(lines)


if __name__ == '__main__':
    knowledge_parser = ExpertKnowledgeParser()
    #print(knowledge_parser.parse_knowledge("templates/dtc_expert_template.txt"))
    for sus in knowledge_parser.parse_knowledge("templates/component_expert_template.txt"):
        print(sus)
    #print(knowledge_parser.parse_knowledge("templates/subsystem_expert_template.txt"))
