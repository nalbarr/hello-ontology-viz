Goal:
- Extend the standardized src/tests structure from PLAN_STANDARIZE_PYTHON_DIRS.md
- Load the real models/pizza.ttl ontology file via owlready2 (in addition to the existing inline demo ontology)
- Add pytest tests for the STATED ontology view (get_stated_rels) using the loaded pizza.ttl ontology
- Add pytest tests for the INFERRED ontology view (get_stated_and_inferred_rels + reasoner) using the loaded pizza.ttl ontology
- Add pytest tests for hierarchical tree visualization (hierarchical_layout) against the real pizza.ttl class hierarchy
- Make each new test fail red then pass green
