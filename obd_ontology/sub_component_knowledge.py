#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne


class SubComponentKnowledge:
    """
    Representation of vehicle-subcomponent-related expert knowledge.
    """

    def __init__(self, sub_component: str, associated_suspect_component: str, oscilloscope: bool,
                 associated_chan: str = "", chan_of_interest: str = "") -> None:
        """
        Initializes the subcomponent knowledge.

        Although subcomponents can have multiple COI and associated channels based on the ontology (inherited),
        we restrict it to exactly one channel (hasCOI == hasChannel) for the moment.

        :param sub_component: subcomponent name
        :param associated_suspect_component: component the subcomponent is element of
        :param oscilloscope: whether oscilloscope measurement possible / reasonable
        :param associated_chan: channel associated with the component, i.e., 'hasChannel' relation
        :param chan_of_interest: proposed channel of interest, i.e., 'hasCOI' relation
        """
        self.sub_component = sub_component
        self.associated_suspect_component = associated_suspect_component
        self.oscilloscope = oscilloscope
        self.associated_chan = associated_chan
        self.chan_of_interest = chan_of_interest

    def __str__(self) -> str:
        """
        Returns a string representation of the subcomponent knowledge.

        :return: string representation of subcomponent knowledge
        """
        return (
                "SubComponent: " + self.sub_component
                + "\nAssociated suspect component: " + self.associated_suspect_component
                + "\nUse Oscilloscope: " + str(self.oscilloscope)
                + "\nAssociated Channel: " + self.associated_chan
                + "\nCOI: " + self.chan_of_interest
        )
