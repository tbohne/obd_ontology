# OBDOntology

Ontology for capturing knowledge about [on-board diagnostics](https://en.wikipedia.org/wiki/On-board_diagnostics) (OBD), particularly [diagnostic trouble codes](https://en.wikipedia.org/wiki/OBD-II_PIDs) (DTCs). Additionally, the `OntologyQueryTool` provides a library of predefined queries for accessing instance information.

![](img/obd_ontology_v10.svg)

## Three Levels of Abstraction

- **raw ontology definition**: no data, just concepts and relations (`raw_obd_ontology.owl`)
- **static ontology**: static OBD knowledge, no specific vehicle info (`static_obd_ontology.owl`)
- **dynamic ontology instance**: instance for one specific vehicle (to be generated automatically based on read OBD data, cf. [
vehicle_diag_smach ](https://github.com/tbohne/vehicle_diag_smach))

## Sample Instance

![](img/sample_instance.png)

## Dependencies

- [**rdflib**](https://rdflib.readthedocs.io/en/stable/): pure Python package for working with RDF

## Interpretation of non-obvious aspects modeled in the ontology

- `use_oscilloscope`: `true` means that it is generally possible to diagnose faults on this component using an oscilloscope
- `priority_id`: important because we suggest the components to be checked in a certain order, starting with the lowest ID, then ascending
- it's also essential to note that `Symptom`s associated with a `FaultCondition` are always optional - they do not have to be present, it is only possible for them to be present
