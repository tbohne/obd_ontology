#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import Tuple


class Fact:
    """
    Representation of a general fact to be entered into a triple store (knowledge graph).
    """

    def __init__(self, triple: Tuple, property_fact=False) -> None:
        self.triple = triple
        self.property_fact = property_fact

    def __str__(self) -> str:
        return "triple: " + str(self.triple)
