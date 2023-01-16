#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from knowledge_graph_query_tool import KnowledgeGraphQueryTool

if __name__ == '__main__':
    qt = KnowledgeGraphQueryTool(local_kb=False)

    dtc_instances = qt.query_all_dtc_instances(False)
    for dtc in dtc_instances:
        print(dtc)
        print("\toccurs with:", qt.query_co_occurring_trouble_codes(dtc, False))
        print("\tcategory:", qt.query_fault_cat_by_dtc(dtc, False))
        print("\tcondition:", qt.query_fault_condition_by_dtc(dtc, False))
        print("\tsymptoms:", qt.query_symptoms_by_dtc(dtc, False))
        print("\tordered suspect components:")
        suspect_components = qt.query_suspect_component_by_dtc(dtc, False)
        ordered_sus_comp = {int(qt.query_diagnostic_association_by_dtc_and_sus_comp(dtc, comp, False)[0]): comp for comp
                            in suspect_components}
        for i in range(len(suspect_components)):
            print("\t\t-", ordered_sus_comp[i])

        print()
