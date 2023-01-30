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
from obd_ontology.dtc_knowledge import DTCKnowledge
from obd_ontology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer
from obd_ontology.knowledge_graph_query_tool import KnowledgeGraphQueryTool
from obd_ontology.subsystem_knowledge import SubsystemKnowledge

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
    dtc_name = StringField("DTC:")
    occurs_with = SelectField("Other DTCs that frequently occur together with the specified DTC:",
                              choices=make_tuple_list(kg_query_tool.query_all_dtc_instances(False)), validate_choice=False)
    occurs_with_submit = SubmitField("Add DTC")
    clear_occurs_with = SubmitField("Clear list")
    fault_condition = StringField("Fault condition")
    symptoms_list = make_tuple_list(kg_query_tool.query_all_symptom_instances())
    symptoms = SelectField("Symptoms potentially occurring with the fault condition:", choices=symptoms_list, validate_choice=False)
    symptoms_submit = SubmitField("Add symptom")
    clear_symptoms = SubmitField("Clear list")
    new_symptom = StringField("If a symptom is not included in the list, please add it in the text box:")
    new_symptom_submit = SubmitField("Add new symptom")
    suspect_components = SelectField(
        "List of suspect components (those that are first in the list should also be checked first):",
        choices=make_tuple_list(kg_query_tool.query_all_component_instances()), validate_choice=False)
    add_component_submit = SubmitField("Add component")
    clear_components = SubmitField("Clear list")
    final_submit = SubmitField("Submit")
    clear_everything = SubmitField("Clear")


class SubsystemForm(FlaskForm):
    """
    Form for the subsystem page.
    """
    subsystem_name = StringField("Subsystem:")
    components = SelectField("Suspect components",
                             choices=make_tuple_list(kg_query_tool.query_all_component_instances()), validate_choice=False)
    add_component_submit = SubmitField("Add to list")
    clear_components = SubmitField("Clear list")
    verifying_components = SelectField("component", choices=make_tuple_list(kg_query_tool.query_all_component_instances()), validate_choice=False)
    verifying_components_submit = SubmitField("Add to list")
    clear_verifying_components = SubmitField("Clear list")
    final_submit = SubmitField("Submit")
    clear_everything = SubmitField("Clear")


class SuspectComponentsForm(FlaskForm):
    """
    Form for the component page.
    """
    component_name = StringField('Component:')
    boolean_choices = [("No", "No",), ("Yes", "Yes")]
    final_submit = SubmitField('Submit component')
    affecting_component_submit = SubmitField('Add to list')
    clear_affecting_components = SubmitField("Clear list")
    measurements_possible = SelectField(choices=boolean_choices)
    affecting_components = SelectField("Add further component",
                                       choices=make_tuple_list(kg_query_tool.query_all_component_instances()), validate_choice=False)


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


def add_subsystem_to_knowledge_graph(vehicle_subsystem: str, contains: list, verified_by: list) -> None:
    """
    Adds a subsystem instance to the knowledge graph using the ExpertKnowledgeEnhancer.

    :param vehicle_subsystem: vehicle subsystem to be represented
    :param contains: suspect components assigned to this subsystem
    :param verified_by: subsystem can be verified by checking this suspect component
    """
    assert isinstance(vehicle_subsystem, str)
    assert isinstance(contains, list)
    assert isinstance(verified_by, list)

    new_subsystem_knowledge = SubsystemKnowledge(vehicle_subsystem=vehicle_subsystem, contains=contains,
                                                 verified_by=verified_by)
    fact_list = expert_knowledge_enhancer.generate_subsystem_facts(new_subsystem_knowledge)
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
                if get_session_variable_list("affecting_components"):
                    if form.component_name.data in kg_query_tool.query_all_component_instances() and \
                            form.component_name.data != session.get("component_name"):
                        flash(
                            "WARNING: This component already exists! If you are sure that you want to overwrite it, "
                            "please click the submit button one more time.")
                        session["component_name"] = form.component_name.data
                    else:
                        # TODO: check whether this is the correct way to check replacement confirmation
                        if form.component_name.data == session.get("component_name"):
                            component_name = session.get("component_name")

                            # TODO: construct all the facts that should be removed
                            facts_to_be_removed = []
                            add_use_oscilloscope_removal_fact(component_name, facts_to_be_removed)
                            add_affected_by_removal_fact(component_name, facts_to_be_removed)

                            # TODO: remove all the facts that are newly added now (replacement)
                            expert_knowledge_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                                facts_to_be_removed
                            )

                        assert form.measurements_possible.data == "Yes" or form.measurements_possible.data == "No"
                        oscilloscope_useful = True if form.measurements_possible.data == "Yes" else False
                        add_component_to_knowledge_graph(suspect_component=form.component_name.data,
                                                         affected_by=get_session_variable_list("affecting_components"),
                                                         oscilloscope=oscilloscope_useful)
                        get_session_variable_list("affecting_components").clear()
                        form.affecting_components.choices = kg_query_tool.query_all_component_instances()
                        if form.component_name.data == session.get("component_name"):
                            flash(f"The component {form.component_name.data} has successfully been overwritten.")
                        else:
                            flash(f"The component {form.component_name.data} has successfully been added.")
                        return redirect(url_for('component_form'))
                else:
                    flash("Please add at least one component that affects the current component!")
            else:
                flash("Please enter component name")

        elif form.affecting_component_submit.data:
            if form.affecting_components.data not in get_session_variable_list("affecting_components"):
                get_session_variable_list("affecting_components").append(form.affecting_components.data)

        elif form.clear_affecting_components.data:
            get_session_variable_list("affecting_components").clear()

    if form.component_name.data != session.get("component_name"):
        session["component_name"] = None

    form.affecting_components.choices = make_tuple_list(kg_query_tool.query_all_component_instances())

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
        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_has_fact(
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


def add_contained_component_removal_facts(subsystem_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `contains` facts to be removed.

    :param subsystem_name: subsystem to remove contains relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    subsystem_uuid = kg_query_tool.query_vehicle_subsystem_by_name(subsystem_name)[0].split("#")[1]

    for comp in kg_query_tool.query_contains_relation_by_subsystem(subsystem_name, False):
        comp_uuid = kg_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]

        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_contains_fact(
            subsystem_uuid, comp_uuid, False
        ))


def add_verifying_component_removal_facts(subsystem_name: str, facts_to_be_removed: list) -> None:
    """
    Adds the `verifies` facts to be removed.

    :param subsystem_name: subsystem to remove verifies relations for
    :param facts_to_be_removed: list of facts to be removed from the KG
    """
    subsystem_uuid = kg_query_tool.query_vehicle_subsystem_by_name(subsystem_name)[0].split("#")[1]

    for comp in kg_query_tool.query_verifies_relations_by_vehicle_subsystem(subsystem_name, False):
        comp_uuid = kg_query_tool.query_suspect_component_by_name(comp)[0].split("#")[1]

        facts_to_be_removed.append(expert_knowledge_enhancer.fuseki_connection.generate_verifies_fact(
            comp_uuid, subsystem_uuid, False
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
                            if form.dtc_name.data in kg_query_tool.query_all_dtc_instances(False) \
                                    and form.dtc_name.data != session.get("dtc_name"):
                                flash(
                                    "WARNING: This DTC already exists! If you are sure that you want"
                                    " to overwrite it, please click the submit button one more time.")
                                session["dtc_name"] = form.dtc_name.data
                            else:
                                if not dtc_sanity_check(form.dtc_name.data):
                                    flash("invalid DTC (not matching expected pattern): " + form.dtc_name.data)
                                else:
                                    # TODO: check whether this is the correct way to check replacement confirmation
                                    if form.dtc_name.data == session.get("dtc_name"):
                                        dtc_name = session.get("dtc_name")

                                        # TODO: construct all the facts that should be removed
                                        facts_to_be_removed = []
                                        add_fault_condition_removal_fact(dtc_name, facts_to_be_removed)
                                        add_co_occurring_dtc_removal_facts(dtc_name, facts_to_be_removed)
                                        add_symptom_removal_facts(dtc_name, facts_to_be_removed)
                                        add_diagnostic_association_removal_facts(dtc_name, facts_to_be_removed)

                                        # TODO: remove all the facts that are newly added now (replacement)
                                        expert_knowledge_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                                            facts_to_be_removed)

                                    add_dtc_to_knowledge_graph(
                                        dtc=form.dtc_name.data,
                                        occurs_with=get_session_variable_list("occurs_with_list"),
                                        fault_condition=form.fault_condition.data,
                                        symptoms=get_session_variable_list("symptom_list"),
                                        suspect_components=get_session_variable_list("component_list"))

                                    get_session_variable_list("component_list").clear()
                                    get_session_variable_list("symptom_list").clear()
                                    get_session_variable_list("occurs_with_list").clear()
                                    if form.dtc_name.data == session.get("dtc_name"):
                                        flash(f"The DTC {form.dtc_name.data} has successfully been overwritten.")
                                    else:
                                        flash(f"The DTC {form.dtc_name.data} has successfully been added.")

                                    return redirect(url_for('dtc_form'))
                        else:
                            flash("Please list at least one component that should be checked!")
                    else:
                        flash("Please add at least one symptom that can occur with the DTC!")
                else:
                    flash("Please enter a fault condition description!")
            else:
                flash("Please enter a DTC code!")

        elif form.add_component_submit.data:
            if form.suspect_components.data not in get_session_variable_list("component_list"):
                get_session_variable_list("component_list").append(form.suspect_components.data)

        elif form.symptoms_submit.data:
            if form.symptoms.data not in get_session_variable_list("symptom_list"):
                get_session_variable_list("symptom_list").append(form.symptoms.data)

        elif form.new_symptom_submit.data:

            if form.new_symptom.data:
                if form.new_symptom.data not in get_session_variable_list("symptom_list"):
                    get_session_variable_list("symptom_list").append(form.new_symptom.data)

            else:
                flash("Please add the new symptom before submitting the symptom!")

        elif form.occurs_with_submit.data:
            if form.occurs_with.data not in get_session_variable_list("occurs_with_list"):
                get_session_variable_list("occurs_with_list").append(form.occurs_with.data)

        elif form.clear_occurs_with.data:
            get_session_variable_list("occurs_with_list").clear()

        elif form.clear_components.data:
            get_session_variable_list("component_list").clear()

        elif form.clear_symptoms.data:
            get_session_variable_list("symptom_list").clear()

        elif form.clear_everything.data:
            get_session_variable_list("occurs_with_list").clear()
            get_session_variable_list("component_list").clear()
            get_session_variable_list("symptom_list").clear()

    if form.dtc_name.data != session.get("dtc_name"):
        session["dtc_name"] = None

    form.symptoms.choices = kg_query_tool.query_all_symptom_instances()
    form.suspect_components.choices = kg_query_tool.query_all_component_instances()
    form.occurs_with.choices = kg_query_tool.query_all_dtc_instances(False)

    return render_template('DTC_form.html', form=form,
                           suspect_components_variable_list=get_session_variable_list("component_list"),
                           symptoms_variable_list=get_session_variable_list("symptom_list"),
                           occurs_with_DTCs_variable_list=get_session_variable_list("occurs_with_list"))


@app.route('/subsystem_form', methods=['GET', 'POST'])
def subsystem_form():
    """
    Renders the subsystem page and processes the form data.
    """
    form = SubsystemForm()

    if form.validate_on_submit():
        if form.final_submit.data:
            if form.subsystem_name.data:
                if get_session_variable_list("subsystem_components"):
                    if get_session_variable_list("verifying_components"):
                        if form.subsystem_name.data in kg_query_tool.query_all_vehicle_subsystem_instances() \
                                and form.subsystem_name.data != session.get("subsystem_name"):
                            flash(
                                "WARNING: This vehicle subsystem already exists! If you are sure that "
                                "you want to overwrite it, please click the submit button one more time.")
                            session["subsystem_name"] = form.subsystem_name.data
                        else:
                            # TODO: check whether this is the correct way to check replacement confirmation
                            if form.subsystem_name.data == session.get("subsystem_name"):
                                subsystem_name = session.get("subsystem_name")

                                # TODO: construct all the facts that should be removed
                                facts_to_be_removed = []
                                add_contained_component_removal_facts(subsystem_name, facts_to_be_removed)
                                add_verifying_component_removal_facts(subsystem_name, facts_to_be_removed)

                                # TODO: remove all the facts that are newly added now (replacement)
                                expert_knowledge_enhancer.fuseki_connection.remove_outdated_facts_from_knowledge_graph(
                                    facts_to_be_removed
                                )

                            add_subsystem_to_knowledge_graph(
                                vehicle_subsystem=form.subsystem_name.data,
                                contains=get_session_variable_list("subsystem_components"),
                                verified_by=get_session_variable_list("verifying_components")
                            )
                            get_session_variable_list("subsystem_components").clear()
                            get_session_variable_list("verifying_components").clear()
                            if form.subsystem_name.data == session.get("subsystem_name"):
                                flash(f"The vehicle subsystem called {form.subsystem_name.data} "
                                      f"has successfully been overwritten.")
                            else:
                                flash(
                                    f"The vehicle subsystem called {form.subsystem_name.data} "
                                    f"has successfully been added.")
                            return redirect(url_for('subsystem_form'))
                    else:
                        flash(
                            "Please name at least one component that can verify whether this "
                            "subsystem works correctly!")
                else:
                    flash("Please list the components that this subsystem comprises!")
            else:
                flash("Please enter a name for the subsystem!")

        elif form.add_component_submit.data:
            if form.components.data not in get_session_variable_list("subsystem_components"):
                get_session_variable_list("subsystem_components").append(form.components.data)

        elif form.verifying_components_submit.data:
            if form.verifying_components.data not in get_session_variable_list("verifying_components"):
                get_session_variable_list("verifying_components").append(form.verifying_components.data)

        elif form.clear_components.data:
            get_session_variable_list("subsystem_components").clear()

        elif form.clear_verifying_components.data:
            get_session_variable_list("verifying_components").clear()

        elif form.clear_everything.data:
            get_session_variable_list("subsystem_components").clear()
            get_session_variable_list("verifying_components").clear()

    if form.subsystem_name.data != session.get("subsystem_name"):
        session["subsystem_name"] = None

    form.components.choices = kg_query_tool.query_all_component_instances()
    form.verifying_components.choices = kg_query_tool.query_all_component_instances()

    return render_template('subsystem_form.html', form=form,
                           components_variable_list=get_session_variable_list("subsystem_components"),
                           verifying_components_list=get_session_variable_list("verifying_components"))


if __name__ == '__main__':
    app.run(debug=True)
