#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

class SubsystemKnowledge:
    """
    Representation of vehicle-subsystem-related expert knowledge.
    """

    def __init__(self, vehicle_subsystem: str, contains: list, verified_by: list) -> None:
        """
        Initializes the subsystem knowledge.

        :param vehicle_subsystem: vehicle subsystem to be represented
        :param contains: suspect components assigned to this subsystem
        :param verified_by: subsystem can be verified by checking this suspect component
        """
        self.vehicle_subsystem = vehicle_subsystem
        self.contains = contains
        self.verified_by = verified_by

    def __str__(self):
        return "Vehicle Subsystem: " + self.vehicle_subsystem + "\nContains: " + str(self.contains) \
            + "\nVerified by: " + str(self.verified_by)
