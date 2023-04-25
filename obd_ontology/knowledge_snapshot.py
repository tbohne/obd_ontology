#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from knowledge_graph_query_tool import KnowledgeGraphQueryTool


def knowledge_snapshot_dtc_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG from a DTC-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - DTC PERSPECTIVE")
    print("###########################################################################\n")
    dtc_instances = qt.query_all_dtc_instances(False)
    for dtc in dtc_instances:
        print(dtc)
        print("\t- occurs with:", qt.query_co_occurring_trouble_codes(dtc, False))
        print("\t- category:", qt.query_fault_cat_by_dtc(dtc, False))
        print("\t- code type:", qt.query_code_type_by_dtc(dtc, False))
        print("\t- fault condition:", qt.query_fault_condition_by_dtc(dtc, False))
        print("\t- vehicle occurrences:", qt.query_vehicle_by_dtc(dtc, False))
        print("\t- symptoms:", qt.query_symptoms_by_dtc(dtc, False))
        sub_name = qt.query_indicates_by_dtc(dtc, False)
        sub_name = "" if len(sub_name) == 0 else sub_name[0]
        print("\t- indicates subsystem:", sub_name)
        print("\t- indicates vehicle part(s):", qt.query_vehicle_part_by_subsystem(sub_name, False))
        print("\t- ordered suspect components:")
        suspect_components = qt.query_suspect_components_by_dtc(dtc, False)
        ordered_sus_comp = {int(qt.query_priority_id_by_dtc_and_sus_comp(dtc, comp, False)[0]): comp for comp
                            in suspect_components}

        for i in range(len(suspect_components)):
            print("\t\t-", ordered_sus_comp[i])
            print("\t\t\tuse oscilloscope:",
                  qt.query_oscilloscope_usage_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\theatmaps for this diag association:",
                  qt.query_generated_heatmaps_by_dtc_and_sus_comp(dtc, ordered_sus_comp[i], False))
            print("\t\t\taffected by:", qt.query_affected_by_relations_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\tverifies:", qt.query_verifies_relation_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\tcontained in subsystem:", qt.query_contains_relation_by_suspect_component(
                ordered_sus_comp[i], False)
            )
        print()
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_subsystem_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG from a vehicle-subsystem-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - SUBSYSTEM PERSPECTIVE")
    print("###########################################################################\n")
    subsystem_instances = qt.query_all_vehicle_subsystem_instances(False)
    for subsystem in subsystem_instances:
        print(subsystem)
        print("\t- contains:", qt.query_contains_relation_by_subsystem(subsystem, False))
        print("\t- vehicle part(s):", qt.query_vehicle_part_by_subsystem(subsystem, False))
    print("\n----------------------------------------------------------------------\n")


def knowledge_snapshot_component_set_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG from a component-set-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - COMPONENT SET PERSPECTIVE")
    print("###########################################################################\n")
    component_set_instances = qt.query_all_component_set_instances(False)
    for comp_set in component_set_instances:
        print(comp_set)
        print("\t- verified by:", qt.query_verifies_relations_by_component_set(comp_set, False))
        print("\t- includes:", qt.query_includes_relation_by_component_set(comp_set, False))


def knowledge_snapshot_component_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG from a component-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - COMPONENT PERSPECTIVE")
    print("###########################################################################\n")
    component_instances = qt.query_all_component_instances(False)
    for comp in component_instances:
        print(comp)
        print("\t- oscilloscope:", qt.query_oscilloscope_usage_by_suspect_component(comp, False))
        print("\t- affected by:", qt.query_affected_by_relations_by_suspect_component(comp, False))
        print("\t- verifies:", qt.query_verifies_relation_by_suspect_component(comp, False))
    print("\n----------------------------------------------------------------------\n")


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool(local_kb=False)
    knowledge_snapshot_dtc_perspective()
    knowledge_snapshot_subsystem_perspective()
    knowledge_snapshot_component_perspective()
    knowledge_snapshot_component_set_perspective()
