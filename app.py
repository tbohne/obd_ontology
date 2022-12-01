import logging
from flask import Flask, render_template, redirect, flash, url_for, session
from wtforms import StringField, SubmitField, SelectField
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect

from OBDOntology.expert_knowledge_enhancer import ExpertKnowledgeEnhancer
from OBDOntology.subsystem_knowledge import SubsystemKnowledge
from OBDOntology.component_knowledge import ComponentKnowledge
from OBDOntology.dtc_knowledge import DTCKnowledge
from OBDOntology.knowledge_graph_query_tool import KnowledgeGraphQueryTool

app = Flask(__name__, template_folder="flask_templates")
app.debug = True
app.config['SECRET_KEY'] = "3847850"
app.app_context()

csrf = CSRFProtect(app)
csrf.init_app(app)

logging.basicConfig(level=logging.DEBUG)


def get_components() -> list:
    """
    returns a list of all instances of components that are in the knowledge graph.
    """
    kg_query_tool = KnowledgeGraphQueryTool()
    return kg_query_tool.query_all_component_instances()


def get_dtcs() -> list:
    """
    returns a list of all instances of DTC that are in the knowledge graph.
    """
    kg_query_tool = KnowledgeGraphQueryTool()
    return kg_query_tool.query_all_dtc_instances()


def get_symptoms() -> list:
    """
    returns a list of all instances of symptoms that are in the knowledge graph.
    """
    kg_query_tool = KnowledgeGraphQueryTool()
    return kg_query_tool.query_all_symptom_instances()


def get_vehicle_subsystems() -> list:
    """
    returns a list of all instances of vehicle subsystems that are in the knowledge graph.
    """
    kg_query_tool = KnowledgeGraphQueryTool()
    return kg_query_tool.query_all_vehicle_subsystem_instances()


def make_tuple_list(some_list) -> list:
    """
    takes a list of single elements and returns a list where each element appears in a tuple with itself.

    This format is needed as input for the SelectMultipleField. Can also be used for the SelectField.
    """
    new_list = []
    for element in some_list:
        new_list.append((element, element))
    return new_list


def get_session_variable_list(name: str) -> list:
    """
    returns the session variable for a given name, or, if not existent, an empty list.

    It is expected to be only used on session variables that should either contain lists or contain None, but no other data type.

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
    dtc_name = StringField("Please enter the DTC:")

    occurs_with = SelectField("Select DTCs that occur with this DTC", choices=make_tuple_list(get_dtcs()))

    occurs_with_submit = SubmitField("Add DTC")

    clear_occurs_with = SubmitField("Clear list")

    fault_condition = StringField("Fault condition")

    symptoms_list = make_tuple_list(get_symptoms())

    symptoms = SelectField("Select symptom", choices=symptoms_list)

    symptoms_submit = SubmitField("Add symptom")

    clear_symptoms = SubmitField("clear list")

    new_symptom = StringField("New symptom")

    new_symptom_submit = SubmitField("Add new symptom")

    suspect_components = SelectField("Select component", choices=get_components())

    add_component_submit = SubmitField("Add component")

    clear_components = SubmitField("Clear list")

    final_submit = SubmitField("Submit")


class SubsystemForm(FlaskForm):
    """
    Form for the subsystem page.
    """
    subsystem_name = StringField("Name of the subsystem")

    components = SelectField("Suspect components", choices=make_tuple_list(get_components()))

    add_component_submit = SubmitField("Add to list")

    clear_components = SubmitField("Clear list")

    verified_by = SelectField("component", choices=get_components())

    final_submit = SubmitField("Submit")


class SuspectComponentsForm(FlaskForm):
    """
    Form for the component page.
    """
    component_name = StringField('Component name:')

    boolean_choices = [("false", "No",), ("true", "Yes")]

    final_submit = SubmitField('Submit component')

    affecting_component_submit = SubmitField('Add to list')

    clear_affecting_components = SubmitField("Clear list")

    measurements_possible = SelectField(choices=boolean_choices)

    affecting_components = SelectField("Add further component", choices=make_tuple_list(get_components()))


def add_component_to_knowledge_graph(name, affected_by, oscilloscope_useful):
    """
    Adds a component instance with the given properties to the knowledge graph.
    """

    new_component_knowledge = ComponentKnowledge(name, oscilloscope_useful, affected_by)
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer(None)
    fact_list = expert_knowledge_enhancer.generate_suspect_component_facts([new_component_knowledge])
    expert_knowledge_enhancer.fuseki_connection.extend_knowledge_graph(fact_list)


def add_dtc_to_knowledge_graph(dtc_name, occurs_with, faultcondition, symptoms, suspect_components):
    """
    Adds a DTC instance with the given properties to the knowledge graph.
    """
    new_dtc_knowledge = DTCKnowledge(dtc_name, occurs_with, faultcondition, symptoms, suspect_components)
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer(None)
    fact_list = expert_knowledge_enhancer.generate_dtc_form_related_facts(new_dtc_knowledge)
    expert_knowledge_enhancer.fuseki_connection.extend_knowledge_graph(fact_list)


def add_subsystem_to_knowledge_graph(subsystem_name, components, verified_by):
    """
    Adds a subsystem instance to the knowledge graph.
    """
    new_subsystem_knowledge = SubsystemKnowledge(subsystem_name, components, verified_by)
    expert_knowledge_enhancer = ExpertKnowledgeEnhancer(None)
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
                if form.component_name.data in get_components() and form.component_name.data != session.get(
                        "component_name"):
                    flash(
                        "WARNING: This component already exists! If you are sure that you want to overwrite it, "
                        "please click the submit button one more time.")
                    session["component_name"] = form.component_name.data
                else:
                    add_component_to_knowledge_graph(name=form.component_name.data,
                                                     affected_by=get_session_variable_list("affecting_components"),
                                                     oscilloscope_useful=form.measurements_possible.data)
                    get_session_variable_list("affecting_components").clear()
                    form.affecting_components.choices = get_components()
                    if form.component_name.data == session.get("component_name"):
                        flash(f"The component {form.component_name.data} has successfully been overwritten.")
                    else:
                        flash(f"The component {form.component_name.data} has successfully been added.")
                    return redirect(url_for('component_form'))
            else:
                flash("Please enter component name")

        elif form.affecting_component_submit.data:
            get_session_variable_list("affecting_components").append(form.affecting_components.data)

        elif form.clear_affecting_components.data:
            get_session_variable_list("affecting_components").clear()

    if form.component_name.data != session.get("component_name"):
        session["component_name"] = None

    form.affecting_components.choices = get_components()

    return render_template('component_form.html', form=form,
                           affecting_components_variable_list=get_session_variable_list("affecting_components"))


@app.route('/dtc_form', methods=['GET', 'POST'])
def dtc_form():
    """
    Renders the DTC page and processes the form data.
    """
    form = DTCForm()

    form.suspect_components.choices = get_components()

    if form.validate_on_submit():
        if form.final_submit.data:
            if form.dtc_name.data:
                if form.fault_condition.data:
                    if form.dtc_name.data in get_dtcs() and form.dtc_name.data != session.get("dtc_name"):
                        flash(
                            "WARNING: This DTC already exists! If you are sure that you want to overwrite it, please "
                            "click the submit button one more time.")
                        session["dtc_name"] = form.dtc_name.data
                    else:
                        add_dtc_to_knowledge_graph(dtc_name=form.dtc_name.data,
                                                   occurs_with=get_session_variable_list("occurs_with_list"),
                                                   faultcondition=form.fault_condition.data,
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
                    flash("Please enter a fault condition description!")
            else:
                flash("Please enter a DTC code!")

        elif form.add_component_submit.data:
            get_session_variable_list("component_list").append(form.suspect_components.data)

        elif form.symptoms_submit.data:
            get_session_variable_list("symptom_list").append(form.symptoms.data)

        elif form.new_symptom_submit.data:

            if form.new_symptom.data:
                # ToDo: check if symptom is already in the list
                get_session_variable_list("symptom_list").append(form.new_symptom.data)

            else:
                flash("Please add the new symptom before submitting the symptom!")

        elif form.occurs_with_submit.data:
            get_session_variable_list("occurs_with_list").append(form.occurs_with.data)

        elif form.clear_occurs_with.data:
            get_session_variable_list("occurs_with_list").clear()

        elif form.clear_components.data:
            session.get("component_list").clear()

        elif form.clear_symptoms.data:
            session.get("symptom_list").clear()

    if form.dtc_name.data != session.get("dtc_name"):
        session["dtc_name"] = None

    form.symptoms.choices = get_symptoms()
    form.suspect_components.choices = get_components()
    form.occurs_with.choices = get_dtcs()

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
                if form.subsystem_name.data in get_vehicle_subsystems() and form.subsystem_name.data != session.get(
                        "subsystem_name"):
                    flash(
                        "WARNING: This vehicle subsystem already exists! If you are sure that you want to overwrite it,"
                        " please click the submit button one more time.")
                    session["subsystem_name"] = form.subsystem_name.data
                else:
                    add_subsystem_to_knowledge_graph(subsystem_name=form.subsystem_name.data,
                                                     components=get_session_variable_list("subsystem_components"),
                                                     verified_by=form.verified_by.data)
                    get_session_variable_list("subsystem_components").clear()
                    if form.subsystem_name.data == session.get("subsystem_name"):
                        flash(f"The vehicle subsystem called {form.subsystem_name.data} "
                              f"has successfully been overwritten.")
                    else:
                        flash(f"The vehicle subsystem called {form.subsystem_name.data} has successfully been added.")
                    return redirect(url_for('subsystem_form'))

            else:
                flash("Please enter a name for the subsystem!")

        elif form.add_component_submit.data:
            get_session_variable_list("subsystem_components").append(form.components.data)

        elif form.clear_components.data:
            get_session_variable_list("subsystem_components").clear()

    if form.subsystem_name.data != session.get("subsystem_name"):
        session["subsystem_name"] = None

    form.components.choices = get_components()

    return render_template('subsystem_form.html', form=form,
                           components_variable_list=get_session_variable_list("subsystem_components"))


if __name__ == '__main__':
    app.run(debug=True)
