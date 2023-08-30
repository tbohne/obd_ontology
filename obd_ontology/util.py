#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List, Tuple


def make_tuple_list(some_list: List) -> List[Tuple]:
    """
    Takes a list of single elements and returns a list where each element appears in a tuple with itself.
    This format is needed as input for 'SelectMultipleField'. Can also be used for 'SelectField'.

    :param some_list: list with single elements
    :return: list of tuples
    """
    return [(e, e) for e in some_list]
