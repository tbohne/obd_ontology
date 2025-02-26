#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer

AFFECTED_BY_MAPPING = {
    "C1": ["C7", "C2", "C6"], "C2": ["C8", "C3"], "C8": ["C12"], "C3": ["C4", "C9"], "C4": ["C11", "C10", "C5"],
    "C11": ["C13"], "C14": ["C15"], "C15": ["C16", "C17", "C18"], "C18": ["C19"], "C19": ["C20", "C21"],
    "C22": ["C23", "C24"], "C24": ["C25", "C26"], "C25": ["C27"], "C26": ["C28"], "C27": ["C29"], "C28": ["C29"],
    "C30": ["C31"], "C31": ["C32", "C33"], "C32": ["C34"], "C33": ["C34"], "C34": ["C35", "C36"]
}
DTC_MAPPING = {
    "P0125": "C1", "P0126": "C14", "P0127": "C22", "P0128": "C30",
}
NUM_OF_COMP = 37

if __name__ == '__main__':
    """
    Generates the KG required for the smach unit tests.
    """
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()
    # initially, add all components to the KG without affected_by relations (satisfy requirements)
    # [odd ones: use_oscilloscope := True; even ones: use_oscilloscope := False] - to also include manual inspections
    for i in range(1, NUM_OF_COMP):
        comp = "C" + str(i)
        expert_knowledge_enhancer.add_component_to_knowledge_graph(comp, [], i % 2 != 0, [], [])

    for i in range(1, NUM_OF_COMP):
        comp = "C" + str(i)
        channels = [  # we have one recorded channel in total -- univariate
            "signal_" + comp
        ]
        for chan in channels:
            expert_knowledge_enhancer.add_channel_to_knowledge_graph(chan)
        # add components (in this case, we assume that the associated channels and the COI are equal)
        affected_by_relations = [] if comp not in AFFECTED_BY_MAPPING else AFFECTED_BY_MAPPING[comp]
        expert_knowledge_enhancer.add_component_to_knowledge_graph(
            comp, affected_by_relations, i % 2 != 0, channels, channels
        )
        comp_model = {
            'exp_normalization_method': 'z_norm',
            'measuring_instruction': '',
            'architecture': 'XCM',
            'model_id': comp + '_XCM_v1_fRLed6zx6AGCEvszx2bT6F',
            'input_length': 500,
            'assesses': comp,
            'hasRequirement': [(i, chan) for i, chan in enumerate(channels)]
        }
        expert_knowledge_enhancer.add_model_to_knowledge_graph(
            comp_model['input_length'], comp_model['exp_normalization_method'], comp_model['measuring_instruction'],
            comp_model['model_id'], comp_model['assesses'], comp_model['hasRequirement'], comp_model['architecture']
        )
    # add DTCs (components must exist before linking to them)
    for dtc, comp in DTC_MAPPING.items():
        expert_knowledge_enhancer.add_dtc_to_knowledge_graph(dtc, [], "FC " + dtc, [], [comp])
