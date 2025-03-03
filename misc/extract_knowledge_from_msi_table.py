#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Patricia Windler, Tim Bohne

import argparse
import re
from typing import List, Dict

import numpy as np
import pandas

from obd_ontology.config import VALID_SPECIAL_CHARACTERS, DTC_REGEX
from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer

EXPERT_KNOWLEDGE_ENHANCER = ExpertKnowledgeEnhancer()


def remove_dtc_from_fault_cond(fault_cond: str, dtc: str) -> str:
    """
    Deletes DTCs that appear at the beginning of the fault condition string, as well as spaces and dashes.

    It first tries to delete anything at the beginning of the fault condition that matches the DTC pattern. This is done
    because there are cases in which the DTC in fault_cond is not the same as the DTC that the fault condition belongs
    to. As there can be DTCs that do not match the DTC pattern, it also tries to delete the DTC itself from the
    beginning of fault_cond.

    :param fault_cond: string containing the fault condition description
    :param dtc: the DTC as string
    :return: fault condition string with DTC in the beginning removed
    """
    pattern = re.compile(DTC_REGEX)
    if pattern.match(fault_cond[:5]):
        fault_cond = fault_cond[5:]
    else:  # some DTCs might not match the pattern; try to remove them by removing that specific DTC
        fault_cond = fault_cond.removeprefix(dtc)
    return fault_cond.lstrip(" -")


def create_dtc_dictionary(path: str) -> Dict[str, List]:
    """
    Reads the MSI Excel file and extracts the relevant information concerning DTCs and components.

    :param path: path to the Excel file
    :return: dictionary with DTCs as keys and a list containing fault condition and tuples of position (priority of the
     component) and component as values, e.g., [fault_cond, (1, comp1), (2, comp2)]
    """
    dtc_dict = {}
    data = pandas.read_excel(path, sheet_name="DTC - Element ID - Baum")

    def get_existing_fault_conditions() -> List[str]:
        """
        Returns a list of all fault conditions that are stored in the dtc_dict at that moment.

        :return: list of all fault conditions in the dtc_dict
        """
        return [dtc_data[0] for dtc_data in dtc_dict.values()]

    for i in range(len(data)):
        dtc = remove_invalid_characters(str(data["DTC"][i]))
        pos = data["Ursachenposition"][i]
        comp = remove_invalid_characters(str(data["Element ID"][i]))
        fault_cond = str(data["Fehlercodes"][i])
        alternative_fault_cond = str(data["Alternative Klartexte der P0 Codes"][i])
        klavkarr_fault_cond = str(data["klavkarr Fehlercodes"][i])
        british_fault_cond = str(data["British Standard ISO 15031-6 (2005)"][i])

        if dtc != "nan":
            if dtc not in dtc_dict:
                if fault_cond != "nan":
                    available_fault_cond = fault_cond
                elif alternative_fault_cond != "nan":
                    available_fault_cond = alternative_fault_cond
                elif klavkarr_fault_cond != "nan":
                    available_fault_cond = klavkarr_fault_cond
                elif british_fault_cond != "nan":
                    available_fault_cond = british_fault_cond
                else:
                    available_fault_cond = "Bitte Fehlerzustandsbeschreibung für {} eingeben".format(dtc)
                available_fault_cond = remove_invalid_characters(available_fault_cond)
                cleaned_fault_cond = remove_dtc_from_fault_cond(available_fault_cond, dtc)
                existing_fault_conds = get_existing_fault_conditions()
                if cleaned_fault_cond not in existing_fault_conds:
                    dtc_dict[dtc] = [cleaned_fault_cond]
                elif available_fault_cond not in existing_fault_conds:
                    dtc_dict[dtc] = [available_fault_cond]
                else:
                    new_fault_cond = dtc + " - " + available_fault_cond
                    assert new_fault_cond not in existing_fault_conds
                    dtc_dict[dtc] = [new_fault_cond]
            if comp != "nan":
                dtc_dict[dtc].append((pos, comp))
    return dtc_dict


def remove_invalid_characters(item: str) -> str:
    """
    Removes certain special characters that can cause errors.

    :param item: string which should be cleared of the certain special characters
    :return: string with certain special characters removed
    """
    item = item.replace("\n", "")
    temp_item = item
    for character in item:
        if not character.isalnum() and character not in VALID_SPECIAL_CHARACTERS:
            temp_item = temp_item.replace(character, "")
    return temp_item


def add_components_to_knowledge_graph(dtc_dict: Dict[str, List]) -> None:
    """
    Extracts all components from the DTC dictionary and adds them to the knowledge graph.

    :param dtc_dict: dictionary with DTCs as keys and a list containing fault condition and tuples of position
    (priority of the component) and component as values, e.g., [fault_cond, (1, comp1), (2, comp2)]
    """
    counter = 0
    all_comps = []
    for dtc_data in dtc_dict.values():
        if len(dtc_data) > 1:
            for comp_tuple in dtc_data[1:]:
                all_comps.append(comp_tuple[1])
    all_comps = set(all_comps)
    for comp in all_comps:
        EXPERT_KNOWLEDGE_ENHANCER.add_component_to_knowledge_graph(comp, [], False)
        counter += 1
    print("Added {} components to the knowledge graph.".format(counter))


def remove_duplicates_from_list(some_list: List[str]) -> List[str]:
    """
    Removes duplicates from a list while preserving the order.

    :param some_list: list that may contain duplicates
    :return: list without duplicates
    """
    list_without_duplicates = []
    for item in some_list:
        if item not in list_without_duplicates:
            list_without_duplicates.append(item)
    return list_without_duplicates


def add_dtcs_to_knowledge_graph(dtc_dict: Dict[str, List]) -> None:
    """
    Adds DTCs from the DTC dictionary to the knowledge graph.

    Only DTCs with a fault condition and at least one linked component are added.

    :param dtc_dict: dictionary with DTCs as keys and a list containing fault condition and tuples of position
    (priority of the component) and component as values, e.g., [fault_cond, (1, comp1), (2, comp2)]
    """
    counter = 0
    for dtc in dtc_dict:
        dtc_data = dtc_dict[dtc]
        fault_cond = dtc_data[0]
        if len(dtc_data) > 1:
            components = dtc_data[1:]
            order_of_components = np.argsort([sublist[0] for sublist in components])
            ordered_components = np.array(components)[order_of_components, 1].tolist()
            ordered_components = remove_duplicates_from_list(ordered_components)
        else:
            ordered_components = []
        EXPERT_KNOWLEDGE_ENHANCER.add_dtc_to_knowledge_graph(dtc, [], fault_cond, [], ordered_components)
        counter += 1
    print("Added {} DTCs to the knowledge graph.".format(counter))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', type=str, help='path to the excel file', required=True)
    args = parser.parse_args()
    dtc_dict = create_dtc_dictionary(args.file_path)
    add_components_to_knowledge_graph(dtc_dict)
    add_dtcs_to_knowledge_graph(dtc_dict)
