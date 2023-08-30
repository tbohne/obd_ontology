#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Patricia Windler, Tim Bohne

import logging
import os
import re
from typing import List, Union

from flask import Flask, render_template, redirect, flash, url_for, session, jsonify, wrappers
from flask_wtf.csrf import CSRFProtect

from obd_ontology.app_classes import SuspectComponentsForm, DTCForm, ComponentSetForm
from obd_ontology.config import VALID_SPECIAL_CHARACTERS, DTC_REGEX
from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from obd_ontology.util import make_tuple_list

app = Flask(
    __name__,
    template_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates')),
    static_folder=os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))
)

CERT_FILE = os.getenv('CERT_FILE')
KEY_FILE = os.getenv('KEY_FILE')
CONTEXT = (CERT_FILE, KEY_FILE) if CERT_FILE and KEY_FILE else 'adhoc'

app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'for dev')
# transmit cookies via HTTPS
app.config['SESSION_COOKIE_SECURE'] = True
# cookies are only sent in requests that originate from the same site (top-level)
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.app_context()

csrf = CSRFProtect(app)
csrf.init_app(app)

logging.basicConfig(level=logging.ERROR)

KG_QUERY_TOOL = KnowledgeGraphQueryTool()
EXPERT_KNOWLEDGE_ENHANCER = ExpertKnowledgeEnhancer("")


@app.route('/session_values')
def get_session_values() -> wrappers.Response:
    """
    This page shows the current state of session variable lists. It is used to synchronize the lists in other tabs.
    """
    return jsonify({
        "synchronized_comp_set_components": get_session_variable_list("comp_set_components"),
        "synchronized_verifying_components": get_session_variable_list("verifying_components"),
        "synchronized_affecting_components": get_session_variable_list("affecting_components"),
        "synchronized_occurs_with_list": get_session_variable_list("occurs_with_list"),
        "synchronized_symptom_list": get_session_variable_list("symptom_list"),
        "synchronized_component_list": get_session_variable_list("component_list"),
    })


def get_session_variable_list(name: str) -> List:
    """
    Returns the session variable for a given name, or, if not existent, an empty list. It is expected to be only used
    on session variables that should either contain lists or 'None', but no other data type.

    :param name: name of the session variable
    :return: list stored in the session variable, or empty list
    """
    if session.get(name) is None:
        session[name] = []
    assert isinstance(session.get(name), list)
    return session.get(name)


def invalid_characters(input_string: str) -> bool:
    """
    Checks whether a string contains invalid special characters, returns true if an invalid character is found.

    :param input_string: string that should be checked
    :return: boolean indicating whether an invalid special character is found
    """
    return any(not c.isalnum() and c not in VALID_SPECIAL_CHARACTERS for c in input_string)


@app.route('/', methods=['POST', 'GET'])
def main() -> str:
    """
    Renders the start page.

    :return: HTML string for the page
    """
    return render_template('index.html')


def check_suspect_components_form(form: SuspectComponentsForm) -> bool:
    """
    Checks if all user inputs to the component form are complete and correct.
    If a problem is found, a corresponding message is flashed.

    :param form: the suspect components form that should be checked
    :return: true if the form has been filled out completely and correctly, else false
    """
    if not form.component_name.data:
        # component name StringField is empty
        flash("Bitte geben Sie den Namen der Komponente ein!")
        return False
    if invalid_characters(form.component_name.data):
        # found an invalid special character in component name StringField
        flash("Ungültiges Sonderzeichen im Namen der Komponente!")
        return False
    if form.component_name.data in get_session_variable_list("affecting_components"):
        # the component itself is in the list of affecting components
        flash("Sie haben angegeben, dass die Komponente von sich selbst beeinflusst wird. Das ist nicht zulässig.")
        return False
    return True


def remove_deprecated_component_facts() -> None:
    """
    Removes deprecated component facts.
    """
    component_name = session.get("component_name")
    # construct all the facts that should be removed
    facts_to_be_removed = []
    add_use_oscilloscope_removal_fact(component_name, facts_to_be_removed)
    add_affected_by_removal_fact(component_name, facts_to_be_removed)
    # remove all the facts that are newly added now (replacement)
    EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.remove_outdated_facts_from_knowledge_graph(facts_to_be_removed)


def add_component_to_kg(form: SuspectComponentsForm, entered_affecting_comps: List) -> None:
    """
    Adds a new component to the knowledge graph.

    :param form: suspect components form with user input
    :param entered_affecting_comps: affecting components entered by the user
    """
    assert form.measurements_possible.data == "Ja" or form.measurements_possible.data == "Nein"
    oscilloscope_useful = True if form.measurements_possible.data == "Ja" else False
    EXPERT_KNOWLEDGE_ENHANCER.add_component_to_knowledge_graph(
        suspect_component=form.component_name.data,
        affected_by=entered_affecting_comps,
        oscilloscope=oscilloscope_useful
    )
    # update SelectField
    form.affecting_components.choices = sorted(KG_QUERY_TOOL.query_all_component_instances())
    # reset variables related to the newly added component
    get_session_variable_list("affecting_components").clear()
    session.modified = True
    session["affecting_components_empty_warning_received"] = None


def show_component_success_msg(form: SuspectComponentsForm) -> None:
    """
    Shows the success message for entered components.

    :param form: suspect components form with user input
    """
    if form.component_name.data == session.get("component_name"):
        flash(f"Die Komponente {form.component_name.data} wurde erfolgreich überschrieben.")
    else:
        flash(f"Die Komponente {form.component_name.data} wurde erfolgreich hinzugefügt.")


def show_component_exists_warning_msg(form: SuspectComponentsForm) -> None:
    """
    Shows the 'component already exists' warning message for entered components.

    :param form: suspect components form with user input
    """
    flash("WARNUNG: Diese Komponente existiert bereits! Wenn Sie sicher sind, dass Sie sie "
          "überschreiben möchten, klicken Sie bitte erneut auf den \"Absenden\"-Button.")
    session["component_name"] = form.component_name.data


def show_no_affecting_component_warning_msg() -> None:
    """
    Shows the 'no affecting components' warning message for entered components.
    """
    flash("WARNUNG: Sie haben keine Komponenten angegeben, die die aktuelle Komponente beeinflussen! "
          "Bitte fügen Sie alle Komponenten hinzu, von denen Sie wissen, dass sie die aktuelle "
          "Komponente beeinflussen. Wenn Sie sicher sind, dass Sie keine beeinflussenden Komponenten "
          "hinzufügen wollen, klicken Sie bitte den  \"Absenden\"-Button erneut.")
    session["affecting_components_empty_warning_received"] = True


def display_component_info(form: SuspectComponentsForm) -> None:
    """
    Displays available component information requested by the user.

    :param form: suspect components form with user input
    """
    existing_component_name = form.existing_components.data
    if existing_component_name is None:
        flash("Keine Daten verfügbar")
    else:
        existing_affecting_components = KG_QUERY_TOOL.query_affected_by_relations_by_suspect_component(
            existing_component_name)
        session["affecting_components"] = existing_affecting_components
        form.component_name.data = existing_component_name
        oscilloscope_useful = KG_QUERY_TOOL.query_oscilloscope_usage_by_suspect_component(existing_component_name)[0]
        form.measurements_possible.data = "Ja" if oscilloscope_useful else "Nein"


def clear_component_info(form: SuspectComponentsForm) -> None:
    """
    Clears the displayed component info.

    :param form: suspect components form with user input
    """
    get_session_variable_list("affecting_components").clear()
    session.modified = True
    form.component_name.data = ""


def add_affecting_components(form: SuspectComponentsForm) -> None:
    """
    Adds the specified affecting components to the list.

    :param form: suspect components form with user input
    """
    if form.affecting_components.data not in get_session_variable_list("affecting_components"):
        get_session_variable_list("affecting_components").append(form.affecting_components.data)
        session.modified = True


def clear_affecting_components() -> None:
    """
    Clears the affecting components list.
    """
    get_session_variable_list("affecting_components").clear()
    session.modified = True


@app.route('/component_form', methods=['GET', 'POST'])
def component_form() -> Union[str, wrappers.Response]:
    """
    Renders the components page and processes the form data.

    :return: HTML string for the page
    """
    form = SuspectComponentsForm()
    if form.validate_on_submit():
        if form.final_submit.data:
            if check_suspect_components_form(form):
                comp_part_of_kg = form.component_name.data in KG_QUERY_TOOL.query_all_component_instances()
                warning_already_shown = form.component_name.data == session.get("component_name")
                entered_affecting_comps = get_session_variable_list("affecting_components")
                # the component will only be added if:
                #   - the name of the component does not exist in the KG yet, or a warning has already been flashed
                #   - there is at least one affecting component specified, or a related warning has already been flashed
                if (not comp_part_of_kg or warning_already_shown) and (
                        entered_affecting_comps or session.get("affecting_components_empty_warning_received")):
                    if warning_already_shown:  # replacement confirmation given
                        remove_deprecated_component_facts()
                    add_component_to_kg(form, entered_affecting_comps)
                    show_component_success_msg(form)
                    return redirect(url_for('component_form'))
                elif comp_part_of_kg and not warning_already_shown:
                    show_component_exists_warning_msg(form)
                elif not entered_affecting_comps and not session.get("affecting_components_empty_warning_received"):
                    show_no_affecting_component_warning_msg()
        elif form.affecting_component_submit.data:  # button that adds affecting components to list has been clicked
            add_affecting_components(form)
        elif form.clear_affecting_components.data:  # button that clears the affecting component list has been clicked
            clear_affecting_components()
        elif form.existing_components_submit.data:  # user wants to see data for an existing component
            display_component_info(form)
        elif form.clear_everything.data:  # button that clears all lists and text fields has been clicked
            clear_component_info(form)
    else:  # no submit button has been pressed - reset variable that specifies whether warning has been shown
        session["affecting_components_empty_warning_received"] = None
    # reset variable that specifies whether warning has been shown
    if form.component_name.data != session.get("component_name"):
        session["component_name"] = None
    # update SelectField choices
    form.affecting_components.choices = make_tuple_list(sorted(KG_QUERY_TOOL.query_all_component_instances()))
    form.existing_components.choices = make_tuple_list(sorted(KG_QUERY_TOOL.query_all_component_instances()))

    return render_template('component_form.html', form=form,
                           affecting_components_variable_list=get_session_variable_list("affecting_components"))


def dtc_sanity_check(dtc: str) -> bool:
    """
    Checks whether the specified DTC satisfies the expected pattern.

    :param dtc: DTC to check pattern for
    :return whether the specified DTC matches the pattern
    """
    pattern = re.compile(DTC_REGEX)
    print("match:", pattern.match(dtc))
    return pattern.match(dtc) and len(dtc) == 5


def add_fault_condition_removal_fact(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    If necessary, adds the fault condition removal fact to the list of facts to be removed.

    :param dtc_name: DTC to check fault condition removal for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    fault_condition = KG_QUERY_TOOL.query_fault_condition_by_dtc(dtc_name, False)[0]
    # check whether fault condition to be added is already part of the KG
    fc = KG_QUERY_TOOL.query_fault_condition_by_description(fault_condition)
    if len(fc) > 0:
        fault_cond_uuid = fc[0].split("#")[1]
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_condition_description_fact(
            fault_cond_uuid, fault_condition, True
        ))


def add_co_occurring_dtc_removal_facts(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the co-occurring DTC facts to be removed.

    :param dtc_name: DTC to remove co-occurring DTCs for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    co_occurring_dtcs = KG_QUERY_TOOL.query_co_occurring_trouble_codes(dtc_name, False)
    dtc_instance = KG_QUERY_TOOL.query_dtc_instance_by_code(dtc_name)
    dtc_uuid = dtc_instance[0].split("#")[1]

    for code in co_occurring_dtcs:
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_co_occurring_dtc_fact(
            dtc_uuid, code, True
        ))


def add_symptom_removal_facts(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the symptom facts to be removed.

    :param dtc_name: DTC to remove symptom associations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    symptoms = KG_QUERY_TOOL.query_symptoms_by_dtc(dtc_name)
    fault_condition = KG_QUERY_TOOL.query_fault_condition_by_dtc(dtc_name, False)[0]
    fault_cond_uuid = KG_QUERY_TOOL.query_fault_condition_by_description(fault_condition)[0].split("#")[1]

    for symptom in symptoms:
        symptom_uuid = KG_QUERY_TOOL.query_symptoms_by_desc(symptom)[0].split("#")[1]
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_symptom_fact(
            fault_cond_uuid, symptom_uuid, False
        ))


def add_diagnostic_association_removal_facts(dtc_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the diagnostic association facts to be removed.

    :param dtc_name: DTC to consider diagnostic associations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    dtc_uuid = KG_QUERY_TOOL.query_dtc_instance_by_code(dtc_name)[0].split("#")[1]

    for comp in KG_QUERY_TOOL.query_suspect_components_by_dtc(dtc_name, False):
        comp_uuid = KG_QUERY_TOOL.query_suspect_component_by_name(comp)[0].split("#")[1]
        diag_association_uuid = KG_QUERY_TOOL.query_diag_association_instance_by_dtc_and_sus_comp(dtc_name, comp, False)
        diag_association_uuid = diag_association_uuid[0].split("#")[1]

        # remove the 'has' connection between DTC and diagnostic association
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_has_association_fact(
            dtc_uuid, diag_association_uuid, False
        ))
        # remove the 'pointsTo' connection between diagnostic association and suspect component
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_points_to_fact(
            diag_association_uuid, comp_uuid, False
        ))
        # remove diagnostic association for the considered DTC
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_diagnostic_association_fact(
            diag_association_uuid, False
        ))

        subsystem_name = KG_QUERY_TOOL.query_indicates_by_dtc(dtc_name, False)[0]
        # remove `contains` relation if there is no other DTC that still causes it
        # -> find DTCs that also have associations with this comp and the particular subsystem
        dtcs_associated_with_comp = KG_QUERY_TOOL.query_dtcs_by_suspect_comp_and_vehicle_subsystem(
            comp, subsystem_name, False
        )
        if len(dtcs_associated_with_comp) > 1:
            print("there is at least one other DTC causing the `contains` relation, not removing it..")
        else:
            print("there is no other DTC causing the `contains` relation, removing it..")
            subsystem_uuid = KG_QUERY_TOOL.query_vehicle_subsystem_by_name(subsystem_name)[0].split("#")[1]
            facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_contains_fact(
                subsystem_uuid, comp_uuid, False
            ))


def add_included_component_removal_facts(comp_set_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `includes` facts to be removed.

    :param comp_set_name: component set to remove `includes` relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    comp_set_uuid = KG_QUERY_TOOL.query_component_set_by_name(comp_set_name)[0].split("#")[1]
    for comp in KG_QUERY_TOOL.query_includes_relation_by_component_set(comp_set_name, False):
        comp_uuid = KG_QUERY_TOOL.query_suspect_component_by_name(comp)[0].split("#")[1]
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_includes_fact(
            comp_set_uuid, comp_uuid, False
        ))


def add_verifying_component_removal_facts(component_set_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `verifies` facts to be removed.

    :param component_set_name: component set to remove `verifies` relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    component_set_uuid = KG_QUERY_TOOL.query_component_set_by_name(component_set_name)[0].split("#")[1]
    for comp in KG_QUERY_TOOL.query_verifies_relations_by_component_set(component_set_name, False):
        comp_uuid = KG_QUERY_TOOL.query_suspect_component_by_name(comp)[0].split("#")[1]
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_verifies_fact(
            comp_uuid, component_set_uuid, False
        ))


def add_use_oscilloscope_removal_fact(component_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `use_oscilloscope` facts to be removed.

    :param component_name: vehicle component to remove oscilloscope usage for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    component_uuid = KG_QUERY_TOOL.query_suspect_component_by_name(component_name)[0].split("#")[1]
    usage = KG_QUERY_TOOL.query_oscilloscope_usage_by_suspect_component(component_name, False)[0]
    facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_use_oscilloscope_fact(
        component_uuid, f"\"{str(usage).lower()}\"^^<http://www.w3.org/2001/XMLSchema#boolean>", True
    ))


def add_affected_by_removal_fact(component_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `affected_by` facts to be removed.

    :param component_name: vehicle component to remove `affected_by` relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    component_uuid = KG_QUERY_TOOL.query_suspect_component_by_name(component_name)[0].split("#")[1]
    for comp in KG_QUERY_TOOL.query_affected_by_relations_by_suspect_component(component_name, False):
        facts_to_be_removed.append(EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.generate_affected_by_fact(
            component_uuid, comp, True
        ))


def check_dtc_form(form: DTCForm) -> bool:
    """
    Checks if all user inputs to the DTC form are complete and correct.

    If a problem has been found, a corresponding message is flashed.

    :param form: the DTCForm that should be checked
    :return: True if the form has been filled out completely and correctly, else False
    """
    if not form.dtc_name.data:
        # the StringField for the DTC is empty
        flash("Bitte geben Sie den DTC ein!")
        return False
    if invalid_characters(form.dtc_name.data):
        # found an invalid special character in DTC
        flash("Ungültiges Sonderzeichen im DTC-Eingabefeld!")
        return False
    if not dtc_sanity_check(form.dtc_name.data):
        # invalid DTC pattern
        flash("Ungültiger DTC (entspricht nicht dem erwarteten Muster): " + form.dtc_name.data)
        return False
    if form.dtc_name.data in get_session_variable_list("occurs_with_list"):
        # DTC occurs with itself
        flash("Sie haben eingegeben, dass der DTC häufig mit sich selbst zusammen auftritt. "
              "Das ist nicht zulässig.")
        return False
    if not form.fault_condition.data:
        # the StringField for the fault condition is empty
        flash("Bitte geben Sie eine Beschreibung des Fehlerzustands ein!")
        return False
    if invalid_characters(form.fault_condition.data):
        # found an invalid special character in the fault condition
        flash("Ungültiges Sonderzeichen im Fehlerzustand-Eingabefeld!")
        return False
    if not (form.fault_condition.data not in KG_QUERY_TOOL.query_all_fault_condition_instances() or
            form.fault_condition.data in KG_QUERY_TOOL.query_fault_condition_by_dtc(form.dtc_name.data)):
        # fault condition already exists
        flash("Der Fehlerzustand existiert bereits für einen anderen DTC. Für jeden DTC muss ein "
              "individueller Fehlerzustand eingegeben werden.")
        return False
    if not get_session_variable_list("component_list"):
        # the list of suspect components is empty
        flash("Bitte nennen Sie mindestens eine Komponente, die überprüft werden sollte!")
        return False
    return True


@app.route('/dtc_form', methods=['GET', 'POST'])
def dtc_form():
    """
    Renders the DTC page and processes the form data.
    """
    form = DTCForm()
    form.suspect_components.choices = sorted(KG_QUERY_TOOL.query_all_component_instances())

    if form.validate_on_submit():
        if form.final_submit.data:
            if check_dtc_form(form):

                warning_already_shown = form.dtc_name.data == session.get("dtc_name")
                # if the DTC already exists and there has not been a warning yet, flash a warning first
                if form.dtc_name.data in KG_QUERY_TOOL.query_all_dtc_instances(False) \
                        and not warning_already_shown:
                    flash(
                        "WARNUNG: Dieser DTC existiert bereits! Wenn Sie sicher sind, dass Sie ihn "
                        "überschreiben möchten, klicken Sie bitte noch einmal auf den \"Absenden\"-Button")
                    session["dtc_name"] = form.dtc_name.data
                else:  # either the DTC does not exist yet, or the warning has already been flashed

                    if warning_already_shown:  # replacement confirmation given
                        dtc_name = session.get("dtc_name")
                        # construct all the facts that should be removed
                        facts_to_be_removed = []
                        try:  # if a DTC has no fault condition, this will be skipped
                            add_fault_condition_removal_fact(dtc_name, facts_to_be_removed)
                            add_symptom_removal_facts(dtc_name, facts_to_be_removed)
                        except IndexError:
                            pass
                        add_co_occurring_dtc_removal_facts(dtc_name, facts_to_be_removed)
                        add_diagnostic_association_removal_facts(dtc_name, facts_to_be_removed)
                        # remove all the facts that are newly added now (replacement)
                        EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                            facts_to_be_removed)

                    # add the DTC to the knowledge graph
                    EXPERT_KNOWLEDGE_ENHANCER.add_dtc_to_knowledge_graph(
                        dtc=form.dtc_name.data,
                        occurs_with=get_session_variable_list("occurs_with_list"),
                        fault_condition=form.fault_condition.data,
                        symptoms=get_session_variable_list("symptom_list"),
                        suspect_components=get_session_variable_list("component_list"))

                    # reset lists
                    get_session_variable_list("component_list").clear()
                    get_session_variable_list("symptom_list").clear()
                    get_session_variable_list("occurs_with_list").clear()
                    session.modified = True

                    # show success message
                    if form.dtc_name.data == session.get("dtc_name"):
                        flash(f"Der DTC {form.dtc_name.data} wurde erfolgreich überschrieben.")
                    else:
                        flash(f"The DTC {form.dtc_name.data} wurde erfolgreich hinzugefügt.")
                    return redirect(url_for('dtc_form'))

        # a button that is not the final submit button has been clicked
        elif form.add_component_submit.data:  # button that adds components to the component list has been clicked
            if form.suspect_components.data not in get_session_variable_list("component_list"):
                get_session_variable_list("component_list").append(form.suspect_components.data)
                session.modified = True

        # button that adds symptoms from the SelectField to the symptom list has been clicked
        elif form.symptoms_submit.data:
            if form.symptoms.data not in get_session_variable_list("symptom_list"):
                get_session_variable_list("symptom_list").append(form.symptoms.data)
                session.modified = True

        # button that adds symptoms from the StringField to the symptom list has been clicked
        elif form.new_symptom_submit.data:
            if form.new_symptom.data:
                if not invalid_characters(form.new_symptom.data):
                    if form.new_symptom.data not in get_session_variable_list("symptom_list"):
                        get_session_variable_list("symptom_list").append(form.new_symptom.data)
                        session.modified = True
                else:  # found an invalid special character
                    flash("Ungültiges Sonderzeichen im Symptom-Eingabefeld gefunden!")
            else:  # no input text in the symptom StringField
                flash("Bitte schreiben Sie das neue Symptom in das Textfeld, bevor Sie versuchen, es hinzuzufügen!")

        elif form.occurs_with_submit.data:  # button that adds other DTC to the occurs_with list has been clicked
            if form.occurs_with.data not in get_session_variable_list("occurs_with_list"):
                get_session_variable_list("occurs_with_list").append(form.occurs_with.data)
                session.modified = True

        elif form.clear_occurs_with.data:  # button that clears the occurs_with list has been clicked
            get_session_variable_list("occurs_with_list").clear()
            session.modified = True

        elif form.clear_components.data:  # button that clears the component list has been clicked
            get_session_variable_list("component_list").clear()
            session.modified = True

        elif form.clear_symptoms.data:  # button that clears the symptom list has been clicked
            get_session_variable_list("symptom_list").clear()
            session.modified = True

        elif form.clear_everything.data:  # button that clears all lists and text fields has been clicked
            get_session_variable_list("occurs_with_list").clear()
            get_session_variable_list("component_list").clear()
            get_session_variable_list("symptom_list").clear()
            session.modified = True
            form.dtc_name.data = ""
            form.fault_condition.data = ""

        elif form.existing_dtc_submit.data:  # user wants to see data for existing DTCs
            existing_dtc = form.existing_dtcs.data
            if existing_dtc is None:
                flash("Keine Daten verfügbar")
            else:
                session["occurs_with_list"] = KG_QUERY_TOOL.query_co_occurring_trouble_codes(existing_dtc)
                suspect_components = KG_QUERY_TOOL.query_suspect_components_by_dtc(existing_dtc, False)
                ordered_sus_comp = {
                    int(KG_QUERY_TOOL.query_priority_id_by_dtc_and_sus_comp(existing_dtc, comp, False)[0]):
                        comp for comp in suspect_components
                }
                session["component_list"] = [ordered_sus_comp[i] for i in range(len(suspect_components))]
                session["symptom_list"] = KG_QUERY_TOOL.query_symptoms_by_dtc(existing_dtc)
                form.dtc_name.data = existing_dtc
                try:
                    form.fault_condition.data = KG_QUERY_TOOL.query_fault_condition_by_dtc(existing_dtc)[0]
                except IndexError:
                    form.fault_condition.data = ""

    # reset variable that specifies whether warning has been shown
    if form.dtc_name.data != session.get("dtc_name"):
        session["dtc_name"] = None

    # update choices of the SelectFields
    form.symptoms.choices = sorted(KG_QUERY_TOOL.query_all_symptom_instances())
    form.suspect_components.choices = sorted(KG_QUERY_TOOL.query_all_component_instances())
    form.occurs_with.choices = sorted(KG_QUERY_TOOL.query_all_dtc_instances(False))
    form.existing_dtcs.choices = sorted(KG_QUERY_TOOL.query_all_dtc_instances())

    return render_template('DTC_form.html', form=form,
                           suspect_components_variable_list=get_session_variable_list("component_list"),
                           symptoms_variable_list=get_session_variable_list("symptom_list"),
                           occurs_with_DTCs_variable_list=get_session_variable_list("occurs_with_list"))


def check_component_set_form(form: ComponentSetForm) -> bool:
    """
    Checks if all user inputs to the component set form are complete and correct.

    If a problem has been found, a corresponding message is flashed.

    :param form: the ComponentSetForm that should be checked
    :return: True if the form has been filled out completely and correctly, else False
    """
    if not form.set_name.data:
        # the StringField for the component set name is empty
        flash("Bitte geben Sie einen Namen für das Komponenten-Set ein!")
        return False
    if invalid_characters(form.set_name.data):
        # found an invalid special character in the set name
        flash("Ungültiges Sonderzeichen im Namen des Komponenten-Sets gefunden!")
        form.set_name.data = ""
        return False
    if not get_session_variable_list("comp_set_components"):
        # the list of components belonging to the component set is empty
        flash("Bitte nennen Sie die Komponenten, aus denen dieses Komponenten-Set besteht!")
        return False
    if not get_session_variable_list("verifying_components"):
        # the list of verifying components is empty
        flash("Nennen Sie bitte mindestens eine Komponente, durch die verifiziert werden kann, ob "
              "dieses Komponenten-Set korrekt funktioniert!")
        return False
    return True


@app.route('/component_set_form', methods=['GET', 'POST'])
def component_set_form():
    """
    Renders the component set page and processes the form data.
    """
    form = ComponentSetForm()

    if form.validate_on_submit():
        if form.final_submit.data:
            if check_component_set_form(form):

                warning_already_shown = form.set_name.data == session.get("comp_set_name")
                # if the comp set already exists and there has not been a warning yet, flash a warning first
                if form.set_name.data in KG_QUERY_TOOL.query_all_component_set_instances() \
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
                        EXPERT_KNOWLEDGE_ENHANCER.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                            facts_to_be_removed
                        )
                    # add the component set to the knowledge graph
                    EXPERT_KNOWLEDGE_ENHANCER.add_component_set_to_knowledge_graph(
                        component_set=form.set_name.data,
                        includes=get_session_variable_list("comp_set_components"),
                        verified_by=get_session_variable_list("verifying_components")
                    )
                    # reset lists
                    get_session_variable_list("comp_set_components").clear()
                    get_session_variable_list("verifying_components").clear()
                    session.modified = True
                    # show a success message
                    if form.set_name.data == session.get("comp_set_name"):
                        flash(f"Das Fahrzeugkomponenten-Set mit dem Namen {form.set_name.data} "
                              f"wurde erfolgreich überschrieben.")
                    else:
                        flash(f"Das Fahrzeugkomponenten-Set mit dem Namen {form.set_name.data} "
                              f"wurde erfolgreich hinzugefügt.")
                    return redirect(url_for('component_set_form'))

        # a button that is not the final submit button has been clicked
        elif form.add_component_submit.data:  # button that adds components to the component list has been clicked
            if form.components.data not in get_session_variable_list("comp_set_components"):
                get_session_variable_list("comp_set_components").append(form.components.data)
                session.modified = True

        # button that adds components to the verified_by list has been clicked
        elif form.verifying_components_submit.data:
            if form.verifying_components.data not in get_session_variable_list("verifying_components"):
                get_session_variable_list("verifying_components").append(form.verifying_components.data)
                session.modified = True

        elif form.clear_components.data:  # button that clears the component list has been clicked
            get_session_variable_list("comp_set_components").clear()
            session.modified = True

        elif form.clear_verifying_components.data:  # button that clears the verified_by list has been clicked
            get_session_variable_list("verifying_components").clear()
            session.modified = True

        elif form.clear_everything.data:  # button that clears all lists and text fields has been clicked
            get_session_variable_list("comp_set_components").clear()
            get_session_variable_list("verifying_components").clear()
            session.modified = True
            form.set_name.data = ""

        elif form.existing_component_set_submit.data:  # user wants to see data for existing component sets
            component_set_name = form.existing_component_sets.data
            if component_set_name is None:
                flash("Keine Daten verfügbar")
            else:
                session["comp_set_components"] = KG_QUERY_TOOL.query_includes_relation_by_component_set(
                    component_set_name)
                session["verifying_components"] = KG_QUERY_TOOL.query_verifies_relations_by_component_set(
                    component_set_name)
                form.set_name.data = component_set_name

    # reset variable that specifies whether warning has been shown
    if form.set_name.data != session.get("comp_set_name"):
        session["comp_set_name"] = None

    # update choices for the SelectFields
    form.components.choices = sorted(KG_QUERY_TOOL.query_all_component_instances())
    form.verifying_components.choices = sorted(KG_QUERY_TOOL.query_all_component_instances())
    form.existing_component_sets.choices = sorted(KG_QUERY_TOOL.query_all_component_set_instances())

    return render_template('component_set_form.html', form=form,
                           components_variable_list=get_session_variable_list("comp_set_components"),
                           verifying_components_list=get_session_variable_list("verifying_components"))


if __name__ == '__main__':
    app.run(debug=True, ssl_context=CONTEXT)
