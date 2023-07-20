#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author Tim Bohne

KNOWLEDGE_GRAPH_FILE = "obd_knowledge_graph.owl"
ONTOLOGY_PREFIX = "http://www.semanticweb.org/diag_ontology#"
FUSEKI_URL = "http://127.0.0.1:3030"
SPARQL_ENDPOINT = "/OBD/sparql"
DATA_ENDPOINT = "/OBD/data"
UPDATE_ENDPOINT = "/OBD/update"
VALID_SPECIAL_CHARACTERS = " ,()-:&/"
DTC_REGEX = "[PCBU][012]\d{3}"
