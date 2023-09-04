#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import Union

from obd_ontology.component_knowledge import ComponentKnowledge
from obd_ontology.component_set_knowledge import ComponentSetKnowledge
from obd_ontology.dtc_knowledge import DTCKnowledge


def parse_dtc_expert_template(lines: list) -> DTCKnowledge:
    """
    Parses the DTC expert template.

    :param lines: lines of the knowledge template
    :return: parsed DTC knowledge
    """
    dtc = fault_condition = ""
    occurs_with = []
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


def parse_subsystem_expert_template(lines: list) -> ComponentSetKnowledge:
    """
    Parses the vehicle component set expert template.

    :param lines: lines of the knowledge template
    :return: parsed component set knowledge
    """
    component_set = ""
    includes = verified_by = []

    title_cnt = 0
    for line in lines:
        if "###" in line:
            title_cnt += 1  # next category
            continue
        line = line[2:].strip()

        if title_cnt == 1:  # subsystem name
            component_set = line
        elif title_cnt == 4:  # 'contains' entries
            includes.append(line)
        elif title_cnt == 6:  # 'verified_by' entry
            verified_by = [line]

    return ComponentSetKnowledge(component_set, includes, verified_by)


def parse_knowledge(knowledge_file: str) -> Union[DTCKnowledge, list, ComponentKnowledge, None]:
    """
    Parses OBD-related expert knowledge from template file (cf. `templates/dtc_expert_template.txt`,
    `templates/component_expert_template`, `templates/subsystem_expert_template.txt`).

    :param knowledge_file: expert knowledge file to be parsed
    """
    with open(knowledge_file) as f:
        lines = f.readlines()

    # only keep the actual data + headlines (categories)
    lines = [line for line in lines if line.count("#") in [0, 3] and line != "\n"]

    if "dtc" in knowledge_file:
        return parse_dtc_expert_template(lines)
    elif "component" in knowledge_file:
        return parse_component_expert_template(lines)
    elif "subsystem" in knowledge_file:
        return parse_subsystem_expert_template(lines)


if __name__ == '__main__':
    print(parse_knowledge("templates/dtc_expert_template.txt"))
    print("----------------------------------------------------------------------------")
    for sus in parse_knowledge("templates/component_expert_template.txt"):
        print(sus)
    print("----------------------------------------------------------------------------")
    print(parse_knowledge("templates/subsystem_expert_template.txt"))
