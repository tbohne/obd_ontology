#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

class Fact:

    def __init__(self, triple, property_fact=False):
        self.triple = triple
        self.property_fact = property_fact

    def __str__(self):
        return "triple: " + str(self.triple)
