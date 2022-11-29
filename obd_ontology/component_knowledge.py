#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

class ComponentKnowledge:
    """
    Representation of vehicle-component-related expert knowledge.
    """

    def __init__(self, suspect_component: str, oscilloscope: bool, affected_by: list) -> None:
        """
        Initializes the component knowledge.

        :param suspect_component: component to be checked
        :param oscilloscope: whether oscilloscope measurement possible / reasonable
        :param affected_by: list of components whose misbehavior could affect the correct functioning of the component
                            under consideration
        """
        self.suspect_component = suspect_component
        self.oscilloscope = oscilloscope
        self.affected_by = affected_by

    def __str__(self):
        return "Suspect Component: " + self.suspect_component + "\nUse Oscilloscope: " + str(self.oscilloscope) \
               + "\nAffected By: " + str(self.affected_by)
