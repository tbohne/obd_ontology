#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import Tuple


class Fact:
    """
    Representation of a semantic fact to be entered into a triple store (knowledge graph).
    """

    def __init__(self, triple: Tuple, property_fact: bool = False) -> None:
        """
        Initializes the semantic fact.

        :param triple: triple comprising the semantic fact <subject, predicate, object>
        :param property_fact: whether it's a property fact
        """
        self.triple = triple
        self.property_fact = property_fact

    def __str__(self) -> str:
        """
        Returns a string representation of the semantic fact.

        :return: string representation of semantic fact
        """
        return "triple: " + str(self.triple)
