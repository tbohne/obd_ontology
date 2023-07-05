#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

import argparse

from termcolor import colored

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
        print(colored(dtc, "yellow", "on_grey", ["bold"]))
        print(colored("\t- occurs with:", "blue", "on_grey", ["bold"]),
              qt.query_co_occurring_trouble_codes(dtc, False))
        print(colored("\t- category:", "blue", "on_grey", ["bold"]), qt.query_fault_cat_by_dtc(dtc, False)[0])
        print(colored("\t- code type:", "blue", "on_grey", ["bold"]), qt.query_code_type_by_dtc(dtc, False)[0])
        print(colored("\t- fault condition:", "blue", "on_grey", ["bold"]),
              qt.query_fault_condition_by_dtc(dtc, False)[0])
        print(colored("\t- vehicle occurrences:", "blue", "on_grey", ["bold"]))
        vehicle_occurrences = qt.query_vehicle_by_dtc(dtc, False)
        for vehicle_occ in vehicle_occurrences:
            print("\t\t-", vehicle_occ)

        print(colored("\t- symptoms:", "blue", "on_grey", ["bold"]), qt.query_symptoms_by_dtc(dtc, False))

        sub_name = qt.query_indicates_by_dtc(dtc, False)
        sub_name = "" if len(sub_name) == 0 else sub_name[0]

        print(colored("\t- indicates subsystem:", "blue", "on_grey", ["bold"]), sub_name)
        print(colored("\t- indicates vehicle part(s):", "blue", "on_grey", ["bold"]),
              qt.query_vehicle_part_by_subsystem(sub_name, False))
        print(colored("\t- ordered suspect components:", "blue", "on_grey", ["bold"]))

        suspect_components = qt.query_suspect_components_by_dtc(dtc, False)
        ordered_sus_comp = {int(qt.query_priority_id_by_dtc_and_sus_comp(dtc, comp, False)[0]): comp for comp
                            in suspect_components}

        for i in range(len(suspect_components)):
            print(colored("\t\t- " + ordered_sus_comp[i], "yellow", "on_grey", ["bold"]))
            print(colored("\t\t\tuse oscilloscope:", "blue", "on_grey", ["bold"]),
                  qt.query_oscilloscope_usage_by_suspect_component(ordered_sus_comp[i], False)[0])
            print(colored("\t\t\taffected by:", "blue", "on_grey", ["bold"]),
                  qt.query_affected_by_relations_by_suspect_component(ordered_sus_comp[i], False))
            print(colored("\t\t\tverifies:", "blue", "on_grey", ["bold"]),
                  qt.query_verifies_relation_by_suspect_component(ordered_sus_comp[i], False))
            print(colored("\t\t\tcontained in subsystem:", "blue", "on_grey", ["bold"]),
                  qt.query_contains_relation_by_suspect_component(ordered_sus_comp[i], False))
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
        print(colored(subsystem, "yellow", "on_grey", ["bold"]))
        print(colored("\t- contains:", "blue", "on_grey", ["bold"]),
              qt.query_contains_relation_by_subsystem(subsystem, False))
        print(colored("\t- vehicle part(s):", "blue", "on_grey", ["bold"]),
              qt.query_vehicle_part_by_subsystem(subsystem, False))
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
        print(colored(comp_set, "yellow", "on_grey", ["bold"]))
        print(colored("\t- verified by:", "blue", "on_grey", ["bold"]),
              qt.query_verifies_relations_by_component_set(comp_set, False))
        print(colored("\t- includes:", "blue", "on_grey", ["bold"]),
              qt.query_includes_relation_by_component_set(comp_set, False))


def knowledge_snapshot_component_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG from a component-centric perspective.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - COMPONENT PERSPECTIVE")
    print("###########################################################################\n")
    component_instances = qt.query_all_component_instances(False)
    for comp in component_instances:
        print(colored(comp, "yellow", "on_grey", ["bold"]))
        print(colored("\t- oscilloscope:", "blue", "on_grey", ["bold"]),
              qt.query_oscilloscope_usage_by_suspect_component(comp, False)[0])
        print(colored("\t- affected by:", "blue", "on_grey", ["bold"]),
              qt.query_affected_by_relations_by_suspect_component(comp, False))
        print(colored("\t- verifies:", "blue", "on_grey", ["bold"]),
              qt.query_verifies_relation_by_suspect_component(comp, False))
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
        print(colored(osci_set_id, "yellow", "on_grey", ["bold"]))
        oscillogram_instances_by_set = qt.query_oscillograms_by_parallel_osci_set(osci_set_id, False)
        for osci in oscillogram_instances_by_set:
            print(colored("\t- oscillogram instance:", "blue", "on_grey", ["bold"]), osci.split("#")[1])


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
        print(colored("osci: " + osci.split("#")[1], "yellow", "on_grey", ["bold"]))
        time_series = qt.query_time_series_by_oscillogram_instance(osci_id, False)[0]
        print(colored("\t- time series excerpt:", "blue", "on_grey", ["bold"]), time_series[:50], "...")


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
        print(colored(osci_classification_id, "yellow", "on_grey", ["bold"]))
        print(colored("\t- model id:", "blue", "on_grey", ["bold"]),
              qt.query_model_id_by_osci_classification_id(osci_classification_id, False)[0])
        print(colored("\t- uncertainty:", "blue", "on_grey", ["bold"]),
              qt.query_uncertainty_by_osci_classification_id(osci_classification_id, False)[0])
        osci_instance = qt.query_oscillogram_by_classification_instance(osci_classification_id, False)
        print(colored("\t- classifies:", "blue", "on_grey", ["bold"]),
              osci_instance[0].split("#")[1] if len(osci_instance) > 0 else "")

        heatmap_instance = qt.query_heatmap_by_classification_instance(osci_classification_id, False)
        heatmap_id = heatmap_instance[0].split("#")[1] if len(heatmap_instance) > 0 else ""
        if len(heatmap_id) > 0:
            print(colored("\t- produces:", "blue", "on_grey", ["bold"]), heatmap_id)
            print(colored("\t\t- generation_method:", "blue", "on_grey", ["bold"]),
                  qt.query_generation_method_by_heatmap(heatmap_id, False)[0])
            print(colored("\t\t- generated heatmap:", "blue", "on_grey", ["bold"]),
                  qt.query_heatmap_string_by_heatmap(heatmap_id, False)[0])

        suspect_comp_instance = qt.query_suspect_component_by_classification(osci_classification_id, False)
        suspect_comp_id = suspect_comp_instance[0].split("#")[1] if len(suspect_comp_instance) > 0 else ""
        print(colored("\t- checks:", "blue", "on_grey", ["bold"]), suspect_comp_id)

        reason_for_instance = qt.query_reason_for_classification(osci_classification_id, False)
        reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        if reason_for_id == "":
            reason_for_instance = qt.query_led_to_for_classification(osci_classification_id, False)
            reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        print(colored("\t- reason for classification:", "blue", "on_grey", ["bold"]), reason_for_id)
        prediction = qt.query_prediction_by_classification(osci_classification_id, False)
        print(colored("\t- prediction:", "blue", "on_grey", ["bold"]), prediction[0] if len(prediction) > 0 else "")


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
        print(colored(manual_inspection_id, "yellow", "on_grey", ["bold"]))
        suspect_comp_instance = qt.query_suspect_component_by_classification(manual_inspection_id, False)
        suspect_comp_id = suspect_comp_instance[0].split("#")[1] if len(suspect_comp_instance) > 0 else ""
        print(colored("\t- checks:", "blue", "on_grey", ["bold"]), suspect_comp_id)
        reason_for_instance = qt.query_reason_for_inspection(manual_inspection_id, False)
        reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        if reason_for_id == "":
            reason_for_instance = qt.query_led_to_for_inspection(manual_inspection_id, False)
            reason_for_id = reason_for_instance[0].split("#")[1] if len(reason_for_instance) > 0 else ""
        print(colored("\t- reason for inspection:", "blue", "on_grey", ["bold"]), reason_for_id)
        prediction = qt.query_prediction_by_classification(manual_inspection_id, False)
        print(colored("\t- prediction:", "blue", "on_grey", ["bold"]), prediction[0] if len(prediction) > 0 else "")


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
        print(colored(diag_log_id, "yellow", "on_grey", ["bold"]))
        print(colored("\t- date:", "blue", "on_grey", ["bold"]), qt.query_date_by_diag_log(diag_log_id, False)[0])
        print(colored("\t- max number of parallel rec:", "blue", "on_grey", ["bold"]),
              qt.query_max_num_of_parallel_rec_by_diag_log(diag_log_id, False)[0])
        print(colored("\t- appearing DTCs:", "blue", "on_grey", ["bold"]))

        appearing_dtcs = qt.query_dtcs_by_diag_log(diag_log_id, False)
        for dtc in appearing_dtcs:
            print("\t\t-", dtc.split("#")[1])

        fault_path_instance = qt.query_fault_path_by_diag_log(diag_log_id, False)
        fault_path_id = fault_path_instance[0].split("#")[1] if len(fault_path_instance) > 0 else ""
        print(colored("\t- entails fault path:", "blue", "on_grey", ["bold"]), fault_path_id)

        vehicle_instance = qt.query_vehicle_by_diag_log(diag_log_id, False)
        vehicle_id = vehicle_instance[0].split("#")[1]
        print(colored("\t- created for vehicle:", "blue", "on_grey", ["bold"]), vehicle_id)

        print(colored("\t- diagnostic steps:", "blue", "on_grey", ["bold"]))
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
        fault_path_desc = qt.query_fault_path_description_by_id(fault_path_id, False)
        print(colored("fault path: " + str(fault_path_desc), "yellow", "on_grey", ["bold"]))
        print(colored("\t- fault conditions that resulted in this fault path:", "blue", "on_grey", ["bold"]))
        fault_conditions = qt.query_resulted_in_by_fault_path(fault_path_id, False)
        for fc in fault_conditions:
            fault_condition_desc = qt.query_fault_condition_description_by_id(fc.split("#")[1], False)[0]
            print("\t\t-", fault_condition_desc)


def knowledge_snapshot_vehicle_perspective():
    """
    Presents a snapshot of the knowledge currently stored in the KG regarding vehicles.
    """
    print("###########################################################################")
    print("KNOWLEDGE SNAPSHOT - VEHICLE PERSPECTIVE")
    print("###########################################################################\n")
    vehicle_instances = qt.query_all_vehicle_instances()
    for vehicle_id, hsn, tsn, vin, model in vehicle_instances:
        vehicle_id = vehicle_id.split("#")[1]
        print(colored(vehicle_id, "yellow", "on_grey", ["bold"]))
        print(colored("\t- HSN: " + hsn, "blue", "on_grey", ["bold"]))
        print(colored("\t- TSN: " + tsn, "blue", "on_grey", ["bold"]))
        print(colored("\t- VIN: " + vin, "blue", "on_grey", ["bold"]))
        print(colored("\t- model: " + model, "blue", "on_grey", ["bold"]))
        print(colored("\t- DTCs recorded in this vehicle:", "blue", "on_grey", ["bold"]))
        dtcs = qt.query_dtcs_recorded_in_vehicle(vehicle_id, False)
        for dtc in dtcs:
            print("\t\t-", dtc)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Knowledge snapshot - shows current content of KG')
    parser.add_argument('--perspective', type=str, help='perspective of snapshot [expert | diag]',
                        required=False, default='expert')
    args = parser.parse_args()
    qt = KnowledgeGraphQueryTool(local_kb=False)

    if args.perspective == 'expert':  # expert knowledge
        knowledge_snapshot_dtc_perspective()
        knowledge_snapshot_subsystem_perspective()
        knowledge_snapshot_component_perspective()
        knowledge_snapshot_component_set_perspective()
    elif args.perspective == 'diag':  # diagnosis
        knowledge_snapshot_parallel_osci_perspective()
        knowledge_snapshot_oscillogram_perspective()
        knowledge_snapshot_oscillogram_classification_perspective()
        knowledge_snapshot_manual_inspection_perspective()
        knowledge_snapshot_diag_log_perspective()
        knowledge_snapshot_fault_path_perspective()
        knowledge_snapshot_vehicle_perspective()
