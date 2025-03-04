#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from typing import List, Tuple


class ModelKnowledge:
    """
    Representation of model-related expert knowledge.
    """

    def __init__(
            self, input_len: int, exp_norm_method: str, measuring_instruction: str, model_id: str, classified_comp: str,
            input_chan_req: List[Tuple[int, str]], architecture: str
    ) -> None:
        """
        Initializes the model knowledge.

        :param input_len: expected input length
        :param exp_norm_method: expected normalization method for input signals
        :param measuring_instruction: instructions to be followed during sensor signal recording
        :param model_id: ID of the model
        :param classified_comp: component the model is suited to evaluate
        :param input_chan_req: input channel requirements
        :param architecture: neural network architecture type
        """
        self.input_len = input_len
        self.exp_norm_method = exp_norm_method
        self.measuring_instruction = measuring_instruction
        self.model_id = model_id
        self.classified_comp = classified_comp
        self.input_chan_req = input_chan_req
        self.architecture = architecture

    def __str__(self) -> str:
        """
        Returns a string representation of the model knowledge.

        :return: string representation of model knowledge
        """
        return "model ID: " + self.model_id + "\ninput len: " + str(self.input_len) + "\nexp norm. method: " \
            + self.exp_norm_method + "\nmeasuring instruction: " + self.measuring_instruction \
            + "\nclassified comp: " + self.classified_comp + "\ninput chan req: " + str(self.input_chan_req) \
            + "\nneural network architecture: " + self.architecture
