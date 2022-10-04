#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

class ExpertKnowledgeParser:
    """
    Parses OBD-related expert knowledge from template file (cf. `templates/dtc_expert_template.txt`,
    `templates/component_expert_template`, `templates/subsystem_expert_template.txt`).
    """

    def __init__(self, knowledge_file: str) -> None:
        self.knowledge_file = knowledge_file
        self.dtc = ""
        self.fault_condition = ""
        self.symptoms = []
        self.suspect_components = []
        self.occurs_with = []

    def parse_dtc_expert_template(self, lines: list) -> None:
        pass

    def parse_component_expert_template(self, lines: list) -> None:
        pass

    def parse_subsystem_expert_template(self, lines: list) -> None:
        pass

    def parse_knowledge(self) -> None:
        """
        Parses the OBD-related expert knowledge.
        """
        with open(self.knowledge_file) as f:
            lines = f.readlines()

        if "dtc" in self.knowledge_file:
            self.parse_dtc_expert_template(lines)
        elif "component" in self.knowledge_file:
            self.parse_component_expert_template(lines)
        elif "subsystem" in self.knowledge_file:
            self.parse_subsystem_expert_template(lines)

        # only keep the actual data + headlines (categories)
        lines = [line for line in lines if line.count("#") in [0, 3] and line != "\n"]

        cat_cnt = 0
        for line in lines:
            if "###" in line:
                cat_cnt += 1  # next category
                continue

            # should be data entry
            assert line[0] == "-"
            line = line[2:].strip()

            if cat_cnt == 1:
                self.dtc = line
            elif cat_cnt == 2:
                self.occurs_with.append(line)
            elif cat_cnt == 3:
                self.fault_condition = line
            elif cat_cnt == 4:
                self.symptoms.append(line)
            elif cat_cnt == 5:
                self.suspect_components.append(line)

    def __str__(self) -> str:
        # TODO: print all fields that are present (have values)
        return "DTC: " + self.dtc + "\nFault Condition: " + self.fault_condition + "\nSymptoms: " \
               + str(self.symptoms) + "\nSuspect Components: " + str(self.suspect_components) + "\nOccurs With: " \
               + str(self.occurs_with)


if __name__ == '__main__':
    knowledge_parser = ExpertKnowledgeParser("templates/dtc_expert_template.txt")
    knowledge_parser.parse_knowledge()
    print(knowledge_parser)
