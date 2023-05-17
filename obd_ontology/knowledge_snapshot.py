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


def knowledge_snapshot_parallel_osci_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding parallel oscillogram sets.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - PARALLEL OSCILLOGRAM SET PERSPECTIVE")
    print("###########################################################################\n")
    osci_set_instances = qt.query_all_parallel_rec_oscillogram_set_instances(False)
    for osci_set_id in osci_set_instances:
        osci_set_id = osci_set_id.split("#")[1]
        print(osci_set_id)
        oscillogram_instances_by_set = qt.query_oscillograms_by_parallel_osci_set(osci_set_id, False)
        for osci in oscillogram_instances_by_set:
            print("\t- oscillogram instance:", osci.split("#")[1])


def knowledge_snapshot_oscillogram_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding oscillograms.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - OSCILLOGRAM PERSPECTIVE")
    print("###########################################################################\n")
    osci_instances = qt.query_all_recorded_oscillograms(False)
    for osci in osci_instances:
        osci_id = osci.split("#")[1]
        print("osci:", osci)
        time_series = qt.query_time_series_by_oscillogram_instance(osci_id, False)[0]
        print("\t- time series excerpt:", time_series[:50], "...")


def knowledge_snapshot_oscillogram_classification_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding oscillogram classifications.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - OSCILLOGRAM CLASSIFICATION PERSPECTIVE")
    print("###########################################################################\n")
    osci_classification_instances = qt.query_all_oscillogram_classifications(False)
    for osci_classification in osci_classification_instances:
        osci_classification_id = osci_classification.split("#")[1]
        print(osci_classification_id)
        print("\t- model id:", qt.query_model_id_by_osci_classification_id(osci_classification_id, False)[0])
        print("\t- uncertainty:", qt.query_uncertainty_by_osci_classification_id(osci_classification_id, False)[0])
        osci_instance = qt.query_oscillogram_by_classification_instance(osci_classification_id, False)
        print("\t- classifies:", osci_instance[0].split("#")[1] if len(osci_instance) > 0 else "")
        heatmap_instance = qt.query_heatmap_by_classification_instance(osci_classification_id, False)
        heatmap_id = heatmap_instance[0].split("#")[1] if len(heatmap_instance) > 0 else ""
        if len(heatmap_id) > 0:
            print("\t- produces:", heatmap_id)
            print("\t\t- generation_method:", qt.query_generation_method_by_heatmap(heatmap_id, False)[0])
            print("\t\t- generated heatmap:", qt.query_heatmap_string_by_heatmap(heatmap_id, False)[0])
        suspect_comp_instance = qt.query_suspect_component_by_osci_classification(osci_classification_id, False)
        suspect_comp_id = suspect_comp_instance[0].split("#")[1] if len(suspect_comp_instance) > 0 else ""
        print("\t- checks:", suspect_comp_id)
        reason_for_instance = qt.query_reason_for_classification(osci_classification_id, False)
        reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        if reason_for_id == "":
            reason_for_instance = qt.query_led_to_for_classification(osci_classification_id, False)
            reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        print("\t- reason for classification:", reason_for_id)
        prediction = qt.query_prediction_by_classification(osci_classification_id, False)
        print("\t- prediction:", prediction[0] if len(prediction) > 0 else "")


def knowledge_snapshot_manual_inspection_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding manual inspections.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - MANUAL INSPECTION PERSPECTIVE")
    print("###########################################################################\n")
    manual_inspection_instances = qt.query_all_manual_inspection_instances(False)
    for manual_inspection in manual_inspection_instances:
        manual_inspection_id = manual_inspection.split("#")[1]
        print(manual_inspection_id)
        suspect_comp_instance = qt.query_suspect_component_by_manual_inspection_id(manual_inspection_id, False)
        suspect_comp_id = suspect_comp_instance[0].split("#")[1] if len(suspect_comp_instance) > 0 else ""
        print("\t- checks:", suspect_comp_id)
        reason_for_instance = qt.query_reason_for_inspection(manual_inspection_id, False)
        reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        if reason_for_id == "":
            reason_for_instance = qt.query_led_to_for_inspection(manual_inspection_id, False)
            reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        print("\t- reason for inspection:", reason_for_id)
        prediction = qt.query_prediction_by_inspection(manual_inspection_id, False)
        print("\t- prediction:", prediction[0] if len(prediction) > 0 else "")


def knowledge_snapshot_diag_log_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding diagnosis logs.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - DIAGNOSIS LOG PERSPECTIVE")
    print("###########################################################################\n")
    diag_log_instances = qt.query_all_diag_log_instances(False)
    for diag_log in diag_log_instances:
        diag_log_id = diag_log.split("#")[1]
        print(diag_log_id)
        print("\t- date:", qt.query_date_by_diag_log(diag_log_id, False)[0])
        print("\t- max number of parallel rec:", qt.query_max_num_of_parallel_rec_by_diag_log(diag_log_id, False)[0])
        print("\t- appearing DTCs:")
        appearing_dtcs = qt.query_dtcs_by_diag_log(diag_log_id, False)
        for dtc in appearing_dtcs:
            print("\t\t-", dtc.split("#")[1])
        fault_path_instance = qt.query_fault_path_by_diag_log(diag_log_id, False)
        fault_path_id = fault_path_instance[0].split("#")[1] if len(fault_path_instance) > 0 else ""
        print("\t- entails fault path:", fault_path_id)
        vehicle_instance = qt.query_vehicle_by_diag_log(diag_log_id, False)
        vehicle_id = vehicle_instance[0].split("#")[1]
        print("\t- created for vehicle:", vehicle_id)
        print("\t- diagnostic steps:")
        diag_steps = qt.query_diag_steps_by_diag_log(diag_log_id, False)
        for diag_step in diag_steps:
            print("\t\t-", diag_step.split("#")[1])


def knowledge_snapshot_fault_path_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding fault paths.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - FAULT PATH PERSPECTIVE")
    print("###########################################################################\n")
    fault_path_instances = qt.query_all_fault_path_instances(False)
    for fault_path in fault_path_instances:
        fault_path_id = fault_path.split("#")[1]
        print(fault_path_id)
        print("\t- fault conditions that resulted in this fault path:")
        fault_conditions = qt.query_resulted_in_by_fault_path(fault_path_id, False)
        for fc in fault_conditions:
            print("\t\t-", fc.split("#")[1])


if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool(local_kb=False)
    knowledge_snapshot_dtc_perspective()
    knowledge_snapshot_subsystem_perspective()
    knowledge_snapshot_component_perspective()
    knowledge_snapshot_component_set_perspective()
    knowledge_snapshot_parallel_osci_perspective()
    knowledge_snapshot_oscillogram_perspective()
    knowledge_snapshot_oscillogram_classification_perspective()
    knowledge_snapshot_manual_inspection_perspective()
    knowledge_snapshot_diag_log_perspective()
    knowledge_snapshot_fault_path_perspective()
