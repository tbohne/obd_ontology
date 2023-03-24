#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Patricia Windler, Tim Bohne

import logging
import os
import re

from flask import Flask, render_template, redirect, flash, url_for, session
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, SubmitField, SelectField

from obd_ontology.component_knowledge import ComponentKnowledge
from obd_ontology.component_set_knowledge import ComponentSetKnowledge
from obd_ontology.dtc_knowledge import DTCKnowledge
from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool

app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
)
app.debug = True
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'for dev')
app.app_context()

csrf = CSRFProtect(app)
csrf.init_app(app)

logging.basicConfig(level=logging.DEBUG)

kg_query_tool = KnowledgeGraphQueryTool()

expert_knowledge_enhancer = ExpertKnowledgeEnhancer("")


def make_tuple_list(some_list) -> list:
    """
    Takes a list of single elements and returns a list where each element appears in a tuple with itself.

    This format is needed as input for the SelectMultipleField. Can also be used for the SelectField.

    :param some_list: list with single elements
    :return: list of tuples
    """
    return [(e, e) for e in some_list]


def get_session_variable_list(name: str) -> list:
    """
    Returns the session variable for a given name, or, if not existent, an empty list.

    It is expected to be only used on session variables that should either contain lists or contain None, but
    no other data type.

    :param name: name of the session variable
    :return: list stored in the session variable, or empty list
    """
    if session.get(name) is None:
        session[name] = []
    assert isinstance(session.get(name), list)
    return session.get(name)


class DTCForm(FlaskForm):
    """
    Form for the DTC page.
    """
    dtc_name = StringField("")
    existing_dtcs = SelectField("", choices=kg_query_tool.query_all_dtc_instances(),
                                validate_choice=False)
    existing_dtc_submit = SubmitField("Daten anzeigen")
    occurs_with = SelectField("",
                              choices=make_tuple_list(kg_query_tool.query_all_dtc_instances(False)),
                              validate_choice=False)
    occurs_with_submit = SubmitField("DTC hinzufügen")
    clear_occurs_with = SubmitField("Liste leeren")
    fault_condition = StringField("")
    symptoms_list = make_tuple_list(kg_query_tool.query_all_symptom_instances())
    symptoms = SelectField("", choices=symptoms_list,
                           validate_choice=False)
    symptoms_submit = SubmitField("Symptom hinzufügen")
    clear_symptoms = SubmitField("Liste leeren")
    new_symptom = StringField("")
    new_symptom_submit = SubmitField("Neues Symptom hinzufügen")
    suspect_components = SelectField(
        "",
        choices=make_tuple_list(kg_query_tool.query_all_component_instances()), validate_choice=False)
    add_component_submit = SubmitField("Komponente hinzufügen")
    clear_components = SubmitField("Liste leeren")
    final_submit = SubmitField("Absenden")
    clear_everything = SubmitField("Alles leeren")


class ComponentSetForm(FlaskForm):
    """
    Form for the component set page.
    """
    set_name = StringField("")
    existing_component_sets = SelectField("", choices=kg_query_tool.query_all_component_set_instances(),
                                          validate_choice=False)
    existing_component_set_submit = SubmitField("Daten anzeigen")
    components = SelectField("",
                             choices=make_tuple_list(kg_query_tool.query_all_component_instances()),
                             validate_choice=False)
    add_component_submit = SubmitField("Komponente hinzufügen")
    clear_components = SubmitField("Liste leeren")
    verifying_components = SelectField("",
                                       choices=make_tuple_list(kg_query_tool.query_all_component_instances()),
                                       validate_choice=False)
    verifying_components_submit = SubmitField("Komponente hinzufügen")
    clear_verifying_components = SubmitField("Liste leeren")
    final_submit = SubmitField("Absenden")
    clear_everything = SubmitField("Alles leeren")


class SuspectComponentsForm(FlaskForm):
    """
    Form for the component page.
    """
    component_name = StringField("")
    existing_components = SelectField("",
                                      choices=make_tuple_list(kg_query_tool.query_all_component_instances()),
                                      validate_choice=False)
    existing_components_submit = SubmitField("Daten anzeigen")
    boolean_choices = [("Nein", "Nein",), ("Ja", "Ja")]
    final_submit = SubmitField('Absenden')
    affecting_component_submit = SubmitField('Komponente hinzufügen')
    clear_affecting_components = SubmitField("Liste leeren")
    measurements_possible = SelectField(choices=boolean_choices)
    affecting_components = SelectField("",
                                       choices=make_tuple_list(kg_query_tool.query_all_component_instances()),
                                       validate_choice=False)
    clear_everything = SubmitField("Alles leeren")


def add_component_to_knowledge_graph(suspect_component: str, affected_by: list, oscilloscope: bool) -> None:
    """
    Adds a component instance with the given properties to the knowledge graph using the ExpertKnowledgeEnhancer.

    :param suspect_component: component to be checked
    :param affected_by: list of components whose misbehavior could affect the correct functioning of the component
                        under consideration
    :param oscilloscope: whether oscilloscope measurement possible / reasonable
    """
    assert isinstance(suspect_component, str)
    assert isinstance(affected_by, list)
    assert isinstance(oscilloscope, bool)

    new_component_knowledge = ComponentKnowledge(suspect_component=suspect_component, oscilloscope=oscilloscope,
                                                 affected_by=affected_by)
    fact_list = expert_knowledge_enhancer.generate_suspect_component_facts([new_component_knowledge])
    expert_knowledge_enhancer.fuseki_connection.extend_knowledge_graph(fact_list)


def add_dtc_to_knowledge_graph(dtc: str, occurs_with: list, fault_condition: str, symptoms: list,
                               suspect_components: list) -> None:
    """
    Adds a DTC instance with the given properties to the knowledge graph using the ExpertKnowledgeEnhancer.

    :param dtc: diagnostic trouble code to be considered
    :param occurs_with: other DTCs frequently occurring with the considered one
    :param fault_condition: fault condition associated with the considered DTC
    :param symptoms: symptoms associated with the considered DTC
    :param suspect_components: components that should be checked when this DTC occurs
                               (order defines suggestion priority)
    """
    assert isinstance(dtc, str)
    assert isinstance(occurs_with, list)
    assert isinstance(fault_condition, str)
    assert isinstance(symptoms, list)
    assert isinstance(suspect_components, list)

    new_dtc_knowledge = DTCKnowledge(dtc=dtc, occurs_with=occurs_with, fault_condition=fault_condition,
                                     symptoms=symptoms, suspect_components=suspect_components)
    fact_list = expert_knowledge_enhancer.generate_dtc_related_facts(new_dtc_knowledge)
    expert_knowledge_enhancer.fuseki_connection.extend_knowledge_graph(fact_list)


def add_component_set_to_knowledge_graph(component_set: str, includes: list, verified_by: list) -> None:
    """
    Adds a component set instance to the knowledge graph using the ExpertKnowledgeEnhancer.

    :param component_set: vehicle component set to be represented
    :param includes: suspect components assigned to this component set
    :param verified_by: component set can be verified by checking this suspect component
    """
    assert isinstance(component_set, str)
    assert isinstance(includes, list)
    assert isinstance(verified_by, list)

    new_comp_set_knowledge = ComponentSetKnowledge(component_set=component_set, includes=includes,
                                                   verified_by=verified_by)
    fact_list = expert_knowledge_enhancer.generate_component_set_facts(new_comp_set_knowledge)
    expert_knowledge_enhancer.fuseki_connection.extend_knowledge_graph(fact_list)


@app.route('/', methods=['POST', 'GET'])
def main():
    """
    Renders the start page.
    """
    return render_template('index.html')


@app.route('/component_form', methods=['GET', 'POST'])
def component_form():
    """
    Renders the components page and processes the form data.
    """
    form = SuspectComponentsForm()

    if form.validate_on_submit():
        if form.final_submit.data:
            if form.component_name.data:

                comp_part_of_kg = form.component_name.data in kg_query_tool.query_all_component_instances()
                warning_already_shown = form.component_name.data == session.get("component_name")
                entered_affecting_comps = get_session_variable_list("affecting_components")

                # the component will only be added if:
                #   - the name of the component does not exist in the KG yet, or a warning has already been flashed
                #   - there is at least one affecting component specified, or a related warning has already been flashed
                if (not comp_part_of_kg or warning_already_shown) and (
                        entered_affecting_comps or session.get("affecting_components_empty_warning_received")):
                    # replacement confirmation given
                    if warning_already_shown:
                        component_name = session.get("component_name")
                        # construct all the facts that should be removed
                        facts_to_be_removed = []
                        add_use_oscilloscope_removal_fact(component_name, facts_to_be_removed)
                        add_affected_by_removal_fact(component_name, facts_to_be_removed)
                        # remove all the facts that are newly added now (replacement)
                        expert_knowledge_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                            facts_to_be_removed
                        )
                    # add component to the knowledge graph
                    assert form.measurements_possible.data == "Ja" or form.measurements_possible.data == "Nein"
                    oscilloscope_useful = True if form.measurements_possible.data == "Ja" else False
                    add_component_to_knowledge_graph(suspect_component=form.component_name.data,
                                                     affected_by=entered_affecting_comps,
                                                     oscilloscope=oscilloscope_useful)
                    # update SelectField
                    form.affecting_components.choices = kg_query_tool.query_all_component_instances()
                    # reset variables related to the newly added component
                    get_session_variable_list("affecting_components").clear()
                    session["affecting_components_empty_warning_received"] = None
                    # show success message
                    if form.component_name.data == session.get("component_name"):
                        flash(f"Die Komponente {form.component_name.data} wurde erfolgreich überschrieben.")
                    else:
                        flash(f"Die Komponente {form.component_name.data} wurde erfolgreich hinzugefügt.")
                    return redirect(url_for('component_form'))

                elif comp_part_of_kg and not warning_already_shown:
                    flash(
                        "WARNUNG: Diese Komponente existiert bereits! Wenn Sie sicher sind, dass Sie sie "
                        "überschreiben möchten, klicken Sie bitte erneut auf den \"Absenden\"-Button.")
                    session["component_name"] = form.component_name.data

                elif not entered_affecting_comps and not session.get("affecting_components_empty_warning_received"):
                    flash("WARNUNG: Sie haben keine Komponenten angegeben, die die aktuelle Komponente beeinflussen! "
                          "Bitte fügen Sie alle Komponenten hinzu, von denen Sie wissen, dass sie die aktuelle "
                          "Komponente beeinflussen. Wenn Sie sicher sind, dass Sie keine beeinflussenden Komponenten "
                          "hinzufügen wollen, klicken Sie bitte den  \"Absenden\"-Button erneut.")
                    session["affecting_components_empty_warning_received"] = True

            else:  # component name StringField is empty
                flash("Bitte geben Sie den Namen der Komponente ein!")
        # a button that is not the final submit button has been clicked
        elif form.affecting_component_submit.data:  # button that adds affecting components to list has been clicked
            if form.affecting_components.data not in get_session_variable_list("affecting_components"):
                get_session_variable_list("affecting_components").append(form.affecting_components.data)

        elif form.clear_affecting_components.data:  # button that clears the affecting component list has been clicked
            get_session_variable_list("affecting_components").clear()

        elif form.existing_components_submit.data:  # user wants to see data for an existing component
            existing_component_name = form.existing_components.data
            if existing_component_name is None:
                flash("Keine Daten verfügbar")
            else:
                existing_affecting_components = kg_query_tool.query_affected_by_relations_by_suspect_component(
                    existing_component_name)
                session["affecting_components"] = existing_affecting_components
                form.component_name.data = existing_component_name
                oscilloscope_useful = \
                kg_query_tool.query_oscilloscope_usage_by_suspect_component(existing_component_name)[0]
                form.measurements_possible.data = "Ja" if oscilloscope_useful else "Nein"

        elif form.clear_everything.data: # button that clears all lists and text fields has been clicked
            get_session_variable_list("affecting_components").clear()
            form.component_name.data = ""

    else:  # no submit button has been pressed - reset variable that specifies whether warning has been shown
        session["affecting_components_empty_warning_received"] = None
    # reset variable that specifies whether warning has been shown
    if form.component_name.data != session.get("component_name"):
        session["component_name"] = None
    # update SelectField choices
    form.affecting_components.choices = make_tuple_list(kg_query_tool.query_all_component_instances())
    form.existing_components.choices = make_tuple_list(kg_query_tool.query_all_component_instances())

    return render_template('component_form.html', form=form,
                           affecting_components_variable_list=get_session_variable_list("affecting_components"))


def dtc_sanity_check(dtc: str) -> bool:
    """
    Checks whether the specified DTC satisfies the expected pattern.

    :param dtc: DTC to check pattern for
    :return whether the specified DTC matches the pattern
    """
    pattern = re.compile("[PCBU][012]\d{3}")
    print("match:", pattern.match(dtc))
    return pattern.match(dtc) and len(dtc) == 5


def add_fault_condition_removal_fact(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    If necessary, adds the fault condition removal fact to the list of facts to be removed.

    :param dtc_name: DTC to check fault condition removal for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    fault_condition = kg_query_tool.query_fault_condition_by_dtc(dtc_name, False)[0]
    # check whether fault condition to be added is already part of the KG
    fc = kg_query_tool.query_fault_condition_by_description(fault_condition)
    if len(fc) > 0:
        fault_cond_uuid = fc[0].split("#")[1]
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_condition_description_fact(
            fault_cond_uuid, fault_condition, True
        ))


def add_co_occurring_dtc_removal_facts(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the co-occurring DTC facts to be removed.

    :param dtc_name: DTC to remove co-occurring DTCs for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    co_occurring_dtcs = kg_query_tool.query_co_occurring_trouble_codes(dtc_name, False)
    dtc_instance = kg_query_tool.query_dtc_instance_by_code(dtc_name)
    dtc_uuid = dtc_instance[0].split("#")[1]

    for code in co_occurring_dtcs:
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_co_occurring_dtc_fact(
            dtc_uuid, code, True
        ))


def add_symptom_removal_facts(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the symptom facts to be removed.

    :param dtc_name: DTC to remove symptom associations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    symptoms = kg_query_tool.query_symptoms_by_dtc(dtc_name)
    fault_condition = kg_query_tool.query_fault_condition_by_dtc(dtc_name, False)[0]
    fault_cond_uuid = kg_query_tool.query_fault_condition_by_description(fault_condition)[0].split("#")[1]

    for symptom in symptoms:
        symptom_uuid = kg_query_tool.query_symptoms_by_desc(symptom)[0].split("#")[1]
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_symptom_fact(
            fault_cond_uuid, symptom_uuid, False
        ))


def add_diagnostic_association_removal_facts(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the diagnostic association facts to be removed.

    :param dtc_name: DTC to consider diagnostic associations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    dtc_uuid = kg_query_tool.query_dtc_instance_by_code(dtc_name)[0].split("#")[1]

    for comp in kg_query_tool.query_suspect_components_by_dtc(dtc_name, False):
        comp_uuid = kg_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]
        diag_association_uuid = kg_query_tool.query_diag_association_instance_by_dtc_and_sus_comp(dtc_name, comp, False)
        diag_association_uuid = diag_association_uuid[0].split("#")[1]

        # remove the 'has' connection between DTC and diagnostic association
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_has_association_fact(
            dtc_uuid, diag_association_uuid, False
        ))
        # remove the 'pointsTo' connection between diagnostic association and suspect component
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_points_to_fact(
            diag_association_uuid, comp_uuid, False
        ))
        # remove diagnostic association for the considered DTC
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_diagnostic_association_fact(
            diag_association_uuid, False
        ))

        subsystem_name = kg_query_tool.query_indicates_by_dtc(dtc_name, False)[0]
        # remove `contains` relation if there is no other DTC that still causes it
        # -> find DTCs that also have associations with this comp and the particular subsystem
        dtcs_associated_with_comp = kg_query_tool.query_dtcs_by_suspect_comp_and_vehicle_subsystem(
            comp, subsystem_name, False
        )
        if len(dtcs_associated_with_comp) > 1:
            print("there is at least one other DTC causing the `contains` relation, not removing it..")
        else:
            print("there is no other DTC causing the `contains` relation, removing it..")
            subsystem_uuid = kg_query_tool.query_vehicle_subsystem_by_name(subsystem_name)[0].split("#")[1]
            facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_contains_fact(
                subsystem_uuid, comp_uuid, False
            ))


def add_included_component_removal_facts(comp_set_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `includes` facts to be removed.

    :param comp_set_name: component set to remove `includes` relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    comp_set_uuid = kg_query_tool.query_component_set_by_name(comp_set_name)[0].split("#")[1]
    for comp in kg_query_tool.query_includes_relation_by_component_set(comp_set_name, False):
        comp_uuid = kg_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_includes_fact(
            comp_set_uuid, comp_uuid, False
        ))


def add_verifying_component_removal_facts(component_set_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `verifies` facts to be removed.

    :param component_set_name: component set to remove `verifies` relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    component_set_uuid = kg_query_tool.query_component_set_by_name(component_set_name)[0].split("#")[1]
    for comp in kg_query_tool.query_verifies_relations_by_component_set(component_set_name, False):
        comp_uuid = kg_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_verifies_fact(
            comp_uuid, component_set_uuid, False
        ))


def add_use_oscilloscope_removal_fact(component_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `use_oscilloscope` facts to be removed.

    :param component_name: vehicle component to remove oscilloscope usage for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    component_uuid = kg_query_tool.query_suspect_component_by_name(component_name)[0].split("#")[1]
    usage = kg_query_tool.query_oscilloscope_usage_by_suspect_component(component_name, False)[0]
    facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_use_oscilloscope_fact(
        component_uuid, f"\"{str(usage).lower()}\"^^<http://www.w3.org/2001/XMLSchema#boolean>", True
    ))


def add_affected_by_removal_fact(component_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `affected_by` facts to be removed.

    :param component_name: vehicle component to remove `affected_by` relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    component_uuid = kg_query_tool.query_suspect_component_by_name(component_name)[0].split("#")[1]
    for comp in kg_query_tool.query_affected_by_relations_by_suspect_component(component_name, False):
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_affected_by_fact(
            component_uuid, comp, True
        ))


@app.route('/dtc_form', methods=['GET', 'POST'])
def dtc_form():
    """
    Renders the DTC page and processes the form data.
    """
    form = DTCForm()
    form.suspect_components.choices = kg_query_tool.query_all_component_instances()

    if form.validate_on_submit():
        if form.final_submit.data:
            if form.dtc_name.data:
                if form.fault_condition.data:
                    if get_session_variable_list("symptom_list"):
                        if get_session_variable_list("component_list"):

                            warning_already_shown = form.dtc_name.data == session.get("dtc_name")
                            # if the DTC already exists and there has not been a warning yet, flash a warning first
                            if form.dtc_name.data in kg_query_tool.query_all_dtc_instances(False) \
                                    and not warning_already_shown:
                                flash(
                                    "WARNUNG: Dieser DTC existiert bereits! Wenn Sie sicher sind, dass Sie ihn "
                                    "überschreiben möchten, klicken Sie bitte noch einmal auf den \"Absenden\"-Button")
                                session["dtc_name"] = form.dtc_name.data
                            else:  # either the DTC does not exist yet, or the warning has already been flashed
                                if not dtc_sanity_check(form.dtc_name.data):
                                    flash(
                                        "Ungültiger DTC (entspricht nicht dem erwarteten Muster): " + form.dtc_name.data)
                                else:
                                    # replacement confirmation given
                                    if warning_already_shown:
                                        dtc_name = session.get("dtc_name")
                                        # construct all the facts that should be removed
                                        facts_to_be_removed = []
                                        add_fault_condition_removal_fact(dtc_name, facts_to_be_removed)
                                        add_co_occurring_dtc_removal_facts(dtc_name, facts_to_be_removed)
                                        add_symptom_removal_facts(dtc_name, facts_to_be_removed)
                                        add_diagnostic_association_removal_facts(dtc_name, facts_to_be_removed)
                                        # remove all the facts that are newly added now (replacement)
                                        expert_knowledge_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                                            facts_to_be_removed)

                                    # add the DTC to the knowledge graph
                                    add_dtc_to_knowledge_graph(
                                        dtc=form.dtc_name.data,
                                        occurs_with=get_session_variable_list("occurs_with_list"),
                                        fault_condition=form.fault_condition.data,
                                        symptoms=get_session_variable_list("symptom_list"),
                                        suspect_components=get_session_variable_list("component_list"))

                                    # reset lists
                                    get_session_variable_list("component_list").clear()
                                    get_session_variable_list("symptom_list").clear()
                                    get_session_variable_list("occurs_with_list").clear()

                                    # show success message
                                    if form.dtc_name.data == session.get("dtc_name"):
                                        flash(f"Der DTC {form.dtc_name.data} wurde erfolgreich überschrieben.")
                                    else:
                                        flash(f"The DTC {form.dtc_name.data} wurde erfolgreich hinzugefügt.")
                                    return redirect(url_for('dtc_form'))
                        else:  # the list of suspect components is empty
                            flash("Bitte nennen Sie mindestens eine Komponente, die überprüft werden sollte!")
                    else:  # the list of symptoms is empty
                        flash(
                            "Bitte fügen Sie mindestens ein Symptom hinzu, das im Zusammenhang mit dem DTC "
                            "auftreten kann!")
                else:  # the StringField for the fault condition is empty
                    flash("Bitte geben Sie eine Beschreibung des Fehlerzustands ein!")
            else:  # the StringField for the DTC is empty
                flash("Bitte geben Sie den DTC ein!")

        # a button that is not the final submit button has been clicked
        elif form.add_component_submit.data:  # button that adds components to the component list has been clicked
            if form.suspect_components.data not in get_session_variable_list("component_list"):
                get_session_variable_list("component_list").append(form.suspect_components.data)

        # button that adds symptoms from the SelectField to the symptom list has been clicked
        elif form.symptoms_submit.data:
            if form.symptoms.data not in get_session_variable_list("symptom_list"):
                get_session_variable_list("symptom_list").append(form.symptoms.data)

        # button that adds symptoms from the StringField to the symptom list has been clicked
        elif form.new_symptom_submit.data:
            if form.new_symptom.data:
                if form.new_symptom.data not in get_session_variable_list("symptom_list"):
                    get_session_variable_list("symptom_list").append(form.new_symptom.data)
            else:
                flash("Bitte schreiben Sie das neue Symptom in das Textfeld, bevor Sie versuchen, es hinzuzufügen!")

        elif form.occurs_with_submit.data:  # button that adds other DTC to the occurs_with list has been clicked
            if form.occurs_with.data not in get_session_variable_list("occurs_with_list"):
                get_session_variable_list("occurs_with_list").append(form.occurs_with.data)

        elif form.clear_occurs_with.data:  # button that clears the occurs_with list has been clicked
            get_session_variable_list("occurs_with_list").clear()

        elif form.clear_components.data:  # button that clears the component list has been clicked
            get_session_variable_list("component_list").clear()

        elif form.clear_symptoms.data:  # button that clears the symptom list has been clicked
            get_session_variable_list("symptom_list").clear()

        elif form.clear_everything.data:  # button that clears all lists and text fields has been clicked
            get_session_variable_list("occurs_with_list").clear()
            get_session_variable_list("component_list").clear()
            get_session_variable_list("symptom_list").clear()
            form.dtc_name.data = ""
            form.fault_condition.data = ""

        elif form.existing_dtc_submit.data:  # user wants to see data for existing DTCs
            existing_dtc = form.existing_dtcs.data
            if existing_dtc is None:
                flash("Keine Daten verfügbar")
            else:
                session["occurs_with_list"] = kg_query_tool.query_co_occurring_trouble_codes(existing_dtc)
                session["component_list"] = kg_query_tool.query_suspect_components_by_dtc(existing_dtc)
                session["symptom_list"] = kg_query_tool.query_symptoms_by_dtc(existing_dtc)
                form.dtc_name.data = existing_dtc
                try:
                    form.fault_condition.data = kg_query_tool.query_fault_condition_by_dtc(existing_dtc)[0]
                except IndexError:
                    form.fault_condition.data = ""

    # reset variable that specifies whether warning has been shown
    if form.dtc_name.data != session.get("dtc_name"):
        session["dtc_name"] = None

    # update choices of the SelectFields
    form.symptoms.choices = kg_query_tool.query_all_symptom_instances()
    form.suspect_components.choices = kg_query_tool.query_all_component_instances()
    form.occurs_with.choices = kg_query_tool.query_all_dtc_instances(False)
    form.existing_dtcs.choices = kg_query_tool.query_all_dtc_instances()

    return render_template('DTC_form.html', form=form,
                           suspect_components_variable_list=get_session_variable_list("component_list"),
                           symptoms_variable_list=get_session_variable_list("symptom_list"),
                           occurs_with_DTCs_variable_list=get_session_variable_list("occurs_with_list"))


@app.route('/component_set_form', methods=['GET', 'POST'])
def component_set_form():
    """
    Renders the component set page and processes the form data.
    """
    form = ComponentSetForm()

    if form.validate_on_submit():
        if form.final_submit.data:
            if form.set_name.data:
                if get_session_variable_list("comp_set_components"):
                    if get_session_variable_list("verifying_components"):

                        warning_already_shown = form.set_name.data == session.get("comp_set_name")
                        # if the comp set already exists and there has not been a warning yet, flash a warning first
                        if form.set_name.data in kg_query_tool.query_all_component_set_instances() \
                                and not warning_already_shown:
                            flash(
                                "WARNUNG: Dieses Fahrzeugkomponenten-Set existiert bereits! Wenn Sie sicher sind, "
                                "dass Sie es überschreiben möchten, klicken Sie bitte noch einmal auf den"
                                " \"Absenden\"-Button.")
                            session["comp_set_name"] = form.set_name.data
                        else:
                            # replacement confirmation given
                            if warning_already_shown:
                                comp_set_name = session.get("comp_set_name")
                                # construct all the facts that should be removed
                                facts_to_be_removed = []
                                add_included_component_removal_facts(comp_set_name, facts_to_be_removed)
                                add_verifying_component_removal_facts(comp_set_name, facts_to_be_removed)
                                # remove all the facts that are newly added now (replacement)
                                expert_knowledge_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                                    facts_to_be_removed
                                )
                            # add the component set to the knowledge graph
                            add_component_set_to_knowledge_graph(
                                component_set=form.set_name.data,
                                includes=get_session_variable_list("comp_set_components"),
                                verified_by=get_session_variable_list("verifying_components")
                            )
                            # reset lists
                            get_session_variable_list("comp_set_components").clear()
                            get_session_variable_list("verifying_components").clear()
                            # show a success message
                            if form.set_name.data == session.get("comp_set_name"):
                                flash(f"Das Fahrzeugkomponenten-Set mit dem Namen {form.set_name.data} "
                                      f"wurde erfolgreich überschrieben.")
                            else:
                                flash(f"Das Fahrzeugkomponenten-Set mit dem Namen {form.set_name.data} "
                                      f"wurde erfolgreich hinzugefügt.")
                            return redirect(url_for('component_set_form'))
                    else:  # the list of verifying components is empty
                        flash("Nennen Sie bitte mindestens eine Komponente, durch die verifiziert werden kann, ob "
                              "dieses Komponenten-Set korrekt funktioniert!")
                else:  # the list of components belonging to the component set is empty
                    flash("Bitte nennen Sie die Komponenten, aus denen dieses Komponenten-Set besteht!")
            else:  # the StringField for the component set name is empty
                flash("Bitte geben Sie einen Namen für das Komponenten-Set ein!")

        # a button that is not the final submit button has been clicked
        elif form.add_component_submit.data:  # button that adds components to the component list has been clicked
            if form.components.data not in get_session_variable_list("comp_set_components"):
                get_session_variable_list("comp_set_components").append(form.components.data)

        # button that adds components to the verified_by list has been clicked
        elif form.verifying_components_submit.data:
            if form.verifying_components.data not in get_session_variable_list("verifying_components"):
                get_session_variable_list("verifying_components").append(form.verifying_components.data)

        elif form.clear_components.data:  # button that clears the component list has been clicked
            get_session_variable_list("comp_set_components").clear()

        elif form.clear_verifying_components.data:  # button that clears the verified_by list has been clicked
            get_session_variable_list("verifying_components").clear()

        elif form.clear_everything.data:  # button that clears all lists and text fields has been clicked
            get_session_variable_list("comp_set_components").clear()
            get_session_variable_list("verifying_components").clear()
            form.set_name.data = ""

        elif form.existing_component_set_submit.data:  # user wants to see data for existing component sets
            component_set_name = form.existing_component_sets.data
            if component_set_name is None:
                flash("Keine Daten verfügbar")
            else:
                session["comp_set_components"] = kg_query_tool.query_includes_relation_by_component_set(
                    component_set_name)
                session["verifying_components"] = kg_query_tool.query_verifies_relations_by_component_set(
                    component_set_name)
                form.set_name.data = component_set_name

    # reset variable that specifies whether warning has been shown
    if form.set_name.data != session.get("comp_set_name"):
        session["comp_set_name"] = None

    # update choices for the SelectFields
    form.components.choices = kg_query_tool.query_all_component_instances()
    form.verifying_components.choices = kg_query_tool.query_all_component_instances()
    form.existing_component_sets.choices = kg_query_tool.query_all_component_set_instances()

    return render_template('component_set_form.html', form=form,
                           components_variable_list=get_session_variable_list("comp_set_components"),
                           verifying_components_list=get_session_variable_list("verifying_components"))


if __name__ == '__main__':
    context = ('static/cert.pem', 'static/key.pem')
    app.run(debug=True, ssl_context=context)
