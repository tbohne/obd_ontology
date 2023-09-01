#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List


class ComponentSetKnowledge:
    """
    Representation of vehicle-component-set-related expert knowledge.
    """

    def __init__(self, component_set: str, includes: List[str], verified_by: List[str]) -> None:
        """
        Initializes the component set knowledge.

        :param component_set: vehicle component set to be represented
        :param includes: suspect components assigned to this component set
        :param verified_by: component set can be verified by checking these suspect components
        """
        self.component_set = component_set
        self.includes = includes
        self.verified_by = verified_by

    def __str__(self) -> str:
        """
        Returns a string representation of the component set knowledge.

        :return: string representation of component set knowledge
        """
        return "Vehicle Component Set: " + self.component_set + "\nIncludes: " + str(self.includes) \
            + "\nVerified by: " + str(self.verified_by)
