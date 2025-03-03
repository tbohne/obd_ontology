#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool


def clear_heatmap_facts(exp_enhancer: ExpertKnowledgeEnhancer, kg_query_tool: KnowledgeGraphQueryTool) -> None:
    """
    Clears the heatmap facts (generated heatmaps) currently stored in the KG.

    :param exp_enhancer: instance of the expert knowledge enhancer
    :param kg_query_tool: instance of the KG query tool
    """
    facts_to_be_removed = []
    gen_heatmaps = kg_query_tool.query_all_heatmap_instances(False)
    for heatmap in gen_heatmaps:
        heatmap_uuid = heatmap.split("#")[1]
        heatmap_str = kg_query_tool.query_heatmap_string_by_heatmap(heatmap_uuid, False)[0]
        facts_to_be_removed.append(exp_enhancer.generate_generated_heatmap_fact(heatmap_uuid, heatmap_str, True))
        gen_method = kg_query_tool.query_generation_method_by_heatmap(heatmap_uuid, False)[0]
        facts_to_be_removed.append(exp_enhancer.generate_heatmap_generation_method_fact(heatmap_uuid, gen_method, True))
        osci_classification = kg_query_tool.query_oscillogram_classification_by_heatmap(heatmap_uuid, False)[0]
        classification_uuid = osci_classification.split("#")[1]
        facts_to_be_removed.append(exp_enhancer.generate_produces_fact(classification_uuid, heatmap_uuid, False))
        facts_to_be_removed.append(exp_enhancer.generate_heatmap_fact(heatmap_uuid, False))
    exp_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(facts_to_be_removed)


def clear_oscillogram_facts(exp_enhancer: ExpertKnowledgeEnhancer, kg_query_tool: KnowledgeGraphQueryTool) -> None:
    """
    Clears the oscillogram facts (recorded oscillograms) currently stored in the KG.

    :param exp_enhancer: instance of the expert knowledge enhancer
    :param kg_query_tool: instance of the KG query tool
    """
    facts_to_be_removed = []
    osci_classifications = kg_query_tool.query_all_oscillogram_classifications(False)
    for classification in osci_classifications:
        classification_uuid = classification.split("#")[1]
        osci = kg_query_tool.query_oscillogram_by_classification_instance(classification_uuid, False)[0]
        osci_uuid = osci.split("#")[1]
        time_series = kg_query_tool.query_time_series_by_oscillogram_instance(osci_uuid, False)[0]
        facts_to_be_removed.append(exp_enhancer.generate_time_series_fact(osci_uuid, time_series, True))
        facts_to_be_removed.append(exp_enhancer.generate_classifies_fact(classification_uuid, osci_uuid, False))
        facts_to_be_removed.append(exp_enhancer.generate_oscillogram_fact(osci_uuid, False))
    exp_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(facts_to_be_removed)


if __name__ == '__main__':
    """
    This script is used to reduce the size of the currently hosted KG by removing the largest aspects of the diagnostic
    knowledge, i.e., the generated heatmaps and oscillogram recordings.
    Although it makes sense to store these facts in general, it also makes sense to be able to obtain a reduced version
    of the KG without these gigantic arrays (e.g., for testing purposes).
    """
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()
    knowledge_graph_query_tool = KnowledgeGraphQueryTool()
    clear_heatmap_facts(expert_knowledge_enhancer, knowledge_graph_query_tool)
    clear_oscillogram_facts(expert_knowledge_enhancer, knowledge_graph_query_tool)
