#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer

if __name__ == '__main__':
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()

    channels = [  # we have 8 recorded channels in total
        "Masseleitung der Heizung der Lambdasonde",
        "Plusleitung der Heizung der Lambdasonde",
        "Plusleitung der Lambdasonde",
        "Masseleitung der Lambdasonde",
        "Signalleitung (Druck) des Saugrohrdrucksensors",
        "Signalleitung (Temperatur) des Saugrohrdrucksensors",
        "Masseleitung des Saugrohrdrucksensors",
        "Versorgungsspannung des Saugrohrdrucksensors"
    ]

    # add channels
    for chan in channels:
        expert_knowledge_enhancer.add_channel_to_knowledge_graph(chan)

    # add components (in this case, we assume that the associated channels and the COI are equal)
    expert_knowledge_enhancer.add_component_to_knowledge_graph(
        "Saugrohrdrucksensor", [], True,
        channels[4:8], channels[4:8]
    )
    expert_knowledge_enhancer.add_component_to_knowledge_graph(
        "Lambdasonde", ["Saugrohrdrucksensor"], True,
        channels[0:4], channels[0:4]
    )

    # add subcomponents
    # TODO

    # add DTC
    expert_knowledge_enhancer.add_dtc_to_knowledge_graph(
        "P0172", [], "Gemisch zu fett (Bank 1)", [], ["Lambdasonde"]
    )
