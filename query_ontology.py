import rdflib

ONTOLOGY_FILE = "obd_ontology.owl"
ONTOLOGY_PREFIX = "<http://www.semanticweb.org/tbohne-p15s/ontologies/2022/6/diag_ontology#>"


def complete_ontology_entry(entry):
    return ONTOLOGY_PREFIX.replace('#', '#' + entry)


def print_res(res):
    for row in res:
        print("--> ", str(row).split(ONTOLOGY_PREFIX.replace("<", "").replace(">", ""))[1].replace("'),)", ""))


def query_fault_causes_by_dtc(dtc, g):
    print("####################################")
    print("QUERY: fault causes for", dtc)
    print("####################################")
    dtc_entry = complete_ontology_entry(dtc)
    represents_entry = complete_ontology_entry('represents')
    fault_cause_entry = complete_ontology_entry('FaultCause')
    has_cause_entry = complete_ontology_entry('hasCause')
    s = f"""
        SELECT ?cause WHERE {{
            {dtc_entry} {represents_entry} ?condition .
            ?cause a {fault_cause_entry} .
            ?condition {has_cause_entry} ?cause .
        }}
        """
    print_res(g.query(s))


def query_fault_condition_by_dtc(dtc, g):
    print("####################################")
    print("QUERY: fault condition for", dtc)
    print("####################################")
    dtc_entry = complete_ontology_entry(dtc)
    represents_entry = complete_ontology_entry('represents')
    s = f"""
        SELECT ?condition WHERE {{
            {dtc_entry} {represents_entry} ?condition .
        }}
        """
    print_res(g.query(s))


def query_symptoms_by_dtc(dtc, g):
    print("####################################")
    print("QUERY: symptoms for", dtc)
    print("####################################")
    dtc_entry = complete_ontology_entry(dtc)
    represents_entry = complete_ontology_entry('represents')
    symptom_entry = complete_ontology_entry('Symptom')
    manifested_by_entry = complete_ontology_entry('manifestedBy')
    s = f"""
        SELECT ?symptom WHERE {{
            {dtc_entry} {represents_entry} ?condition .
            ?symptom a {symptom_entry} .
            ?condition {manifested_by_entry} ?symptom .
        }}
        """
    print_res(g.query(s))


def query_corrective_actions_by_dtc(dtc, g):
    print("####################################")
    print("QUERY: corrective actions for", dtc)
    print("####################################")
    dtc_entry = complete_ontology_entry(dtc)
    represents_entry = complete_ontology_entry('represents')
    deletes_entry = complete_ontology_entry('deletes')
    resolves_entry = complete_ontology_entry('resolves')
    condition_entry = complete_ontology_entry('FaultCondition')
    action_entry = complete_ontology_entry('CorrectiveAction')
    s = f"""
       SELECT ?action WHERE {{
           {dtc_entry} {represents_entry} ?condition .
           ?action {deletes_entry} {dtc_entry} .
           ?action {resolves_entry} ?condition .
           ?condition a {condition_entry} .
           ?action a {action_entry} .
       }}
       """
    print_res(g.query(s))


if __name__ == '__main__':
    graph = rdflib.Graph()
    DTC = "P0138"
    graph = graph.parse(ONTOLOGY_FILE, format='xml')
    query_fault_causes_by_dtc(DTC, graph)
    query_fault_condition_by_dtc(DTC, graph)
    query_symptoms_by_dtc(DTC, graph)
    query_corrective_actions_by_dtc(DTC, graph)
