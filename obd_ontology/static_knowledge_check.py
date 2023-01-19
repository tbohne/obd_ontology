#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from knowledge_graph_query_tool import KnowledgeGraphQueryTool

if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool(local_kb=False)

    dtc_instances = qt.query_all_dtc_instances(False)
    for dtc in dtc_instances:
        print(dtc)
        print("\t- occurs with:", qt.query_co_occurring_trouble_codes(dtc, False))
        print("\t- category:", qt.query_fault_cat_by_dtc(dtc, False))
        print("\t- condition:", qt.query_fault_condition_by_dtc(dtc, False))
        print("\t- symptoms:", qt.query_symptoms_by_dtc(dtc, False))
        print("\t- ordered suspect components:")
        suspect_components = qt.query_suspect_components_by_dtc(dtc, False)
        ordered_sus_comp = {int(qt.query_diagnostic_association_by_dtc_and_sus_comp(dtc, comp, False)[0]): comp for comp
                            in suspect_components}

        for i in range(len(suspect_components)):
            print("\t\t-", ordered_sus_comp[i])
            print("\t\t\tuse oscilloscope:", qt.query_oscilloscope_usage_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\taffected by:", qt.query_affected_by_relations_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\tverifies:", qt.query_verifies_relation_by_suspect_component(ordered_sus_comp[i], False))
            print("\t\t\tpart of:", qt.query_contains_relation_by_suspect_component(ordered_sus_comp[i], False))
        print()
