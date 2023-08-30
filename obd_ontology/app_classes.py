#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField

from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from obd_ontology.util import make_tuple_list

KG_QUERY_TOOL = KnowledgeGraphQueryTool()


class DTCForm(FlaskForm):
    """
    Form for the DTC page.
    """
    dtc_name = StringField("")
    existing_dtcs = SelectField("", choices=sorted(KG_QUERY_TOOL.query_all_dtc_instances()), validate_choice=False)
    existing_dtc_submit = SubmitField("Daten anzeigen")
    occurs_with = SelectField("", choices=make_tuple_list(sorted(KG_QUERY_TOOL.query_all_dtc_instances(False))),
                              validate_choice=False)
    occurs_with_submit = SubmitField("DTC hinzufügen")
    clear_occurs_with = SubmitField("Liste leeren")
    fault_condition = StringField("")
    symptoms_list = make_tuple_list(sorted(KG_QUERY_TOOL.query_all_symptom_instances()))
    symptoms = SelectField("", choices=symptoms_list, validate_choice=False)
    symptoms_submit = SubmitField("Symptom hinzufügen")
    clear_symptoms = SubmitField("Liste leeren")
    new_symptom = StringField("")
    new_symptom_submit = SubmitField("Neues Symptom hinzufügen")
    suspect_components = SelectField("", choices=make_tuple_list(sorted(KG_QUERY_TOOL.query_all_component_instances())),
                                     validate_choice=False)
    add_component_submit = SubmitField("Komponente hinzufügen")
    clear_components = SubmitField("Liste leeren")
    final_submit = SubmitField("Absenden")
    clear_everything = SubmitField("Eingaben löschen")


class ComponentSetForm(FlaskForm):
    """
    Form for the component set page.
    """
    set_name = StringField("")
    existing_component_sets = SelectField("", choices=sorted(KG_QUERY_TOOL.query_all_component_set_instances()),
                                          validate_choice=False)
    existing_component_set_submit = SubmitField("Daten anzeigen")
    components = SelectField("", choices=make_tuple_list(sorted(KG_QUERY_TOOL.query_all_component_instances())),
                             validate_choice=False)
    add_component_submit = SubmitField("Komponente hinzufügen")
    clear_components = SubmitField("Liste leeren")
    verifying_components = SelectField("",
                                       choices=make_tuple_list(sorted(KG_QUERY_TOOL.query_all_component_instances())),
                                       validate_choice=False)
    verifying_components_submit = SubmitField("Komponente hinzufügen")
    clear_verifying_components = SubmitField("Liste leeren")
    final_submit = SubmitField("Absenden")
    clear_everything = SubmitField("Eingaben löschen")


class SuspectComponentsForm(FlaskForm):
    """
    Form for the component page.
    """
    component_name = StringField("")
    existing_components = SelectField("",
                                      choices=make_tuple_list(sorted(KG_QUERY_TOOL.query_all_component_instances())),
                                      validate_choice=False)
    existing_components_submit = SubmitField("Daten anzeigen")
    boolean_choices = [("Nein", "Nein",), ("Ja", "Ja")]
    final_submit = SubmitField('Absenden')
    affecting_component_submit = SubmitField('Komponente hinzufügen')
    clear_affecting_components = SubmitField("Liste leeren")
    measurements_possible = SelectField(choices=boolean_choices)
    affecting_components = SelectField("",
                                       choices=make_tuple_list(sorted(KG_QUERY_TOOL.query_all_component_instances())),
                                       validate_choice=False)
    clear_everything = SubmitField("Eingaben löschen")
