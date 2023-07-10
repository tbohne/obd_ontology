import argparse
import pandas
import numpy as np

from expert_knowledge_enhancer import ExpertKnowledgeEnhancer

expert_knowledge_enhancer = ExpertKnowledgeEnhancer()


def create_dtc_dictionary(path: str) -> dict:
    """
    Reads the MSI excel file and extracts the relevant information concerning DTCs and components.

    :param path: path to the excel file
    :return: dictionary with DTCs as keys and a list containing fault condition and tuples of position and
    component as values, e.g. [fault_cond, [1, comp1], [2, comp2]]
    """
    dtc_dict = {}

    data = pandas.read_excel(path, sheet_name="DTC - Element ID - Baum")

    for i in range(len(data)):

        dtc = str(data["DTC"][i])
        pos = data["Ursachenposition"][i]
        comp = str(data["Element ID"][i])
        fault_cond = str(data["Fehlercodes"][i])
        alternative_fault_cond = str(data["Alternative Klartexte der P0 Codes"][i])
        british_fault_cond = str(data["British Standard ISO 15031-6 (2005)"][i])

        if dtc != "nan":
            if dtc not in dtc_dict:
                if fault_cond != "nan":
                    dtc_dict[dtc] = [fault_cond]
                elif alternative_fault_cond != "nan":
                    dtc_dict[dtc] = [alternative_fault_cond]
                elif british_fault_cond != "nan":
                    dtc_dict[dtc] = [british_fault_cond]
                else:
                    dtc_dict[dtc] = [None]

            if comp != "nan":
                dtc_dict[dtc].append([pos, comp])

    return dtc_dict


def remove_invalid_characters(item: str) -> str:
    """
    Removes certain special characters that can cause errors.

    :param item: string which should be cleared of the certain special characters
    :return: string with certain special characters removed
    """
    invalid_characters = ["\n", "\""]
    for invalid_character in invalid_characters:
        item = item.replace(invalid_character, "")
    return item


def add_components_to_knowledge_graph(dtc_dict: dict) -> None:
    """
    Extracts all components from the DTC dictionary and adds them to the knowledge graph.

    :param dtc_dict: dictionary with DTCs as keys and a list containing fault condition and tuples of position and
    component as values, e.g. [fault_cond, [1, comp1], [2, comp2]]
    """
    counter = 0
    all_comps = []

    for dtc_data in dtc_dict.values():
        if len(dtc_data) > 1:
            for comp_tuple in dtc_data[1:]:
                all_comps.append(comp_tuple[1])
    all_comps = set(all_comps)

    for comp in all_comps:
        comp = remove_invalid_characters(comp)
        expert_knowledge_enhancer.add_component_to_knowledge_graph(comp, [], False)
        counter += 1

    print("Added {} components to the knowledge graph.".format(counter))


def add_dtcs_to_knowledge_graph(dtc_dict: dict) -> None:
    """
    Adds DTCs from the DTC dictionary to the knowledge graph.

    Only DTCs with a fault condition and at least one linked component are added.

    :param dtc_dict: dictionary with DTCs as keys and a list containing fault condition and tuples of position and
    component as values, e.g. [fault_cond, [1, comp1], [2, comp2]]
    """
    dtcs_without_components = []
    dtcs_without_fault_cond = []
    counter = 0

    for dtc in dtc_dict:
        dtc_data = dtc_dict[dtc]
        # check that we only add DTCs that have a fault condition and at least one component
        if dtc_data[0] is not None:
            if len(dtc_data) > 1:
                fault_cond = dtc_data[0]
                components = dtc_data[1:]
                order_of_components = np.argsort([sublist[0] for sublist in components])
                ordered_components = np.array(components)[order_of_components, 1].tolist()
                print(ordered_components)

                dtc = remove_invalid_characters(dtc)
                fault_cond = remove_invalid_characters(fault_cond)
                ordered_components = [remove_invalid_characters(comp) for comp in ordered_components]
                expert_knowledge_enhancer.add_dtc_to_knowledge_graph(dtc, [], fault_cond, [], ordered_components)
                counter += 1
            else:
                dtcs_without_components.append(dtc)
        else:
            dtcs_without_fault_cond.append(dtc)

    print("Added {} DTCs to the knowledge graph.".format(counter))
    print("DTCs that do not have a fault condition - please remember to add fault conditions in the future: ",
          dtcs_without_fault_cond)
    print("DTCs that do not have components assigned to them - please remember to add fault conditions in the future: ",
          dtcs_without_components)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--file_path', type=str, help='path to the excel file',
                        required=True)
    args = parser.parse_args()

    dtc_dict = create_dtc_dictionary(args.file_path)
    add_components_to_knowledge_graph(dtc_dict)
    add_dtcs_to_knowledge_graph(dtc_dict)
