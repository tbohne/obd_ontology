#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer

if __name__ == '__main__':
    """
    Generates the KG for the final multivariate demonstrator scenario in the project.
    """

    expert_knowledge_enhancer = ExpertKnowledgeEnhancer()

    channels = [  # we have 8 recorded channels in total
        "Masseleitung der Heizung der Lambdasonde",
        "Plusleitung der Heizung der Lambdasonde",
        "Plusleitung der Lambdasonde",
        "Masseleitung der Lambdasonde",
        "Versorgungsspannung des Saugrohrdrucksensors",
        "Signalleitung (Temperatur) des Saugrohrdrucksensors",
        "Masseleitung des Saugrohrdrucksensors",
        "Signalleitung (Druck) des Saugrohrdrucksensors"
    ]

    for chan in channels:  # add channels
        expert_knowledge_enhancer.add_channel_to_knowledge_graph(chan)

    # add components (in this case, we assume that the associated channels and the COI are equal)
    expert_knowledge_enhancer.add_component_to_knowledge_graph(
        "Saugrohrdrucksensor", [], True, channels[4:8], channels[4:8]
    )
    expert_knowledge_enhancer.add_component_to_knowledge_graph(
        "Lambdasonde", ["Saugrohrdrucksensor"], True, channels[0:4], channels[0:4]
    )

    # add subcomponents
    # in this case, we have one subcomponent for each channel, this is not necessarily always the case
    for chan in channels[0:4]:
        expert_knowledge_enhancer.add_sub_component_to_knowledge_graph(chan, "Lambdasonde", True)
    for chan in channels[4:]:
        expert_knowledge_enhancer.add_sub_component_to_knowledge_graph(chan, "Saugrohrdrucksensor", True)

    # add DTC
    expert_knowledge_enhancer.add_dtc_to_knowledge_graph(
        "P0172", [], "Gemisch zu fett (Bank 1)", [], ["Lambdasonde"]
    )

    # add the trained model knowledge
    #   - one for each channel in isolation + "Lambdasonde" + "Saugrohrdrucksensor"

    # add the two multichannel ANNs
    lambda_model = {
        'exp_normalization_method': 'z_norm',
        'measuring_instruction': 'Explainable Convolutional Neural Network (XCM) zur binären Klassifizierung von'
                                 ' Lambdasonden-Anomalien in multivariaten Zeitreihen',
        'architecture': 'XCM',
        'model_id': 'Lambdasonde_XCM_v1_fRLed6zx6AGCEvszx2bT6F',
        'input_length': 500,
        'assesses': 'Lambdasonde',
        'hasRequirement': [(i, chan) for i, chan in enumerate(channels[0:4])],
        # the following three are not (yet) part of the ontology
        'format': 'pth',
        'test_acc': 0.9565,
        'output': 'bool'
    }
    expert_knowledge_enhancer.add_model_to_knowledge_graph(
        lambda_model['input_length'], lambda_model['exp_normalization_method'], lambda_model['measuring_instruction'],
        lambda_model['model_id'], lambda_model['assesses'], lambda_model['hasRequirement'], lambda_model['architecture']
    )
    pressure_model = {
        'exp_normalization_method': 'z_norm',
        'measuring_instruction': 'Explainable Convolutional Neural Network (XCM) zur binären Klassifizierung von'
                                 ' Saugrohrdrucksensor-Anomalien in multivariaten Zeitreihen',
        'architecture': 'XCM',
        'model_id': 'Saugrohrdrucksensor_XCM_v1_H5bqdN5pjTmTs6RGaCPEqL',
        'input_length': 500,
        'assesses': 'Saugrohrdrucksensor',
        'hasRequirement': [(i, chan) for i, chan in enumerate(channels[4:])],
        # the following three are not (yet) part of the ontology
        'format': 'pth',
        'test_acc': 1.0,
        'output': 'bool'
    }
    expert_knowledge_enhancer.add_model_to_knowledge_graph(
        pressure_model['input_length'], pressure_model['exp_normalization_method'],
        pressure_model['measuring_instruction'], pressure_model['model_id'], pressure_model['assesses'],
        pressure_model['hasRequirement'], pressure_model['architecture']
    )

    # add the rule-based models for channel evaluation
    rule_based_lambda_model = {
        'exp_normalization_method': '',  # raw data expected
        'measuring_instruction': 'rule-based model -- hand-crafted classification rules for channels',
        'architecture': 'rule-based',
        'model_id': 'lambda_rule_based_univariate_ts_classification_model_001',
        'input_length': 500,
        'assesses': 'Lambdasonde',
        'hasRequirement': [(i, chan) for i, chan in enumerate(channels[0:4])]
    }
    expert_knowledge_enhancer.add_model_to_knowledge_graph(
        rule_based_lambda_model['input_length'], rule_based_lambda_model['exp_normalization_method'],
        rule_based_lambda_model['measuring_instruction'], rule_based_lambda_model['model_id'],
        rule_based_lambda_model['assesses'], rule_based_lambda_model['hasRequirement'],
        rule_based_lambda_model['architecture']
    )
    rule_based_pressure_model = {
        'exp_normalization_method': '',  # raw data expected
        'measuring_instruction': 'rule-based model -- hand-crafted classification rules for channels',
        'architecture': 'rule-based',
        'model_id': 'pressure_rule_based_univariate_ts_classification_model_001',
        'input_length': 500,
        'assesses': 'Saugrohrdrucksensor',
        'hasRequirement': [(i, chan) for i, chan in enumerate(channels[4:])]
    }
    expert_knowledge_enhancer.add_model_to_knowledge_graph(
        rule_based_pressure_model['input_length'], rule_based_pressure_model['exp_normalization_method'],
        rule_based_pressure_model['measuring_instruction'], rule_based_pressure_model['model_id'],
        rule_based_pressure_model['assesses'], rule_based_pressure_model['hasRequirement'],
        rule_based_pressure_model['architecture']
    )
