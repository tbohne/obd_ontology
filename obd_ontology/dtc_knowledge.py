#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List


class DTCKnowledge:
    """
    Representation of DTC-related expert knowledge that is not automatically generated based on the DTC parser.
    """

    def __init__(self, dtc: str, occurs_with: List[str], fault_condition: str, symptoms: List[str],
                 suspect_components: List[str]) -> None:
        """
        Initializes the DTC knowledge.

        :param dtc: diagnostic trouble code to be considered
        :param occurs_with: other DTCs frequently occurring with the considered one
        :param fault_condition: fault condition associated with the considered DTC
        :param symptoms: symptoms associated with the considered DTC
        :param suspect_components: components that should be checked when this DTC occurs
                                   (order defines suggestion priority)
        """
        self.dtc = dtc
        self.occurs_with = occurs_with
        self.fault_condition = fault_condition
        self.symptoms = symptoms
        self.suspect_components = suspect_components

    def __str__(self) -> str:
        """
        Returns a string representation of the DTC knowledge.

        :return: string representation of DTC knowledge
        """
        return "DTC: " + self.dtc + "\nFault Condition: " + self.fault_condition + "\nSymptoms: " \
            + str(self.symptoms) + "\nSuspect Components: " + str(self.suspect_components) + "\nOccurs With: " \
            + str(self.occurs_with)
