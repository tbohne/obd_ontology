#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from knowledge_graph_query_tool import KnowledgeGraphQueryTool


def static_knowledge_check_dtc_perspective():
    """
    Presents the static knowledge that is currently stored in the KG from a DTC-centric perspective.
    """
    dtc_instances = qt.query_all_dtc_instances(False)
    for dtc in dtc_instances:
        print(dtc)
        print("\t- occurs with:", qt.query_co_occurring_trouble_codes(dtc, False))
        print("\t- category:", qt.query_fault_cat_by_dtc(dtc, False))
        print("\t- code type:", qt.query_code_type_by_dtc(dtc, False))
        print("\t- condition:", qt.query_fault_condition_by_dtc(dtc, False))
        print("\t- symptoms:", qt.query_symptoms_by_dtc(dtc, False))
        print("\t- ordered suspect components:")
        suspect_components = qt.query_suspect_components_by_dtc(dtc, False)
        ordered_sus_comp = {int(qt.query_diagnostic_association_by_dtc_and_sus_comp(dtc, comp, False)[0]): comp for comp
                            in suspect_components}

        for i in range(len(suspect_components)):
            print("\t\t-", ordered_sus_comp[i])
            print("\t\t\tuse oscilloscope:",
                  qt.query_oscilloscope_usage_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\taffected by:", qt.query_affected_by_relations_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\tverifies:", qt.query_verifies_relation_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\tpart of:", qt.query_contains_relation_by_suspect_component(ordered_sus_comp[i], False))
        print()
    print("\n----------------------------------------------------------------------\n")


def static_knowledge_check_subsystem_perspective():
    """
    Presents the static knowledge that is currently stored in the KG from a vehicle-subsystem-centric perspective.
    """
    subsystem_instances = qt.query_all_vehicle_subsystem_instances(False)
    for subsystem in subsystem_instances:
        print(subsystem)
        print("\t- contains:", qt.query_contains_relation_by_subsystem(subsystem, False))
        print("\t- verified by:", qt.query_verifies_relations_by_vehicle_subsystem(subsystem, False))
    print("\n----------------------------------------------------------------------\n")


def static_knowledge_check_component_perspective():
    """
    Presents the static knowledge that is currently stored in the KG from a component-centric perspective.
    """
    component_instances = qt.query_all_component_instances(False)
    for comp in component_instances:
        print(comp)
        print("\t- oscilloscope:", qt.query_oscilloscope_usage_by_suspect_component(comp, False))
        print("\t- affected by:", qt.query_affected_by_relations_by_suspect_component(comp, False))
    print("\n----------------------------------------------------------------------\n")


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool(local_kb=False)
    static_knowledge_check_dtc_perspective()
    static_knowledge_check_subsystem_perspective()
    static_knowledge_check_component_perspective()
