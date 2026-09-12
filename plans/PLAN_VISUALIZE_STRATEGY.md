Goals:
- Refactor src/pizza_ontology.py to have two separate implementations for visualzation
- Introduct sub package called visualization
- Within sub package visualization
    - Introduce an abstract class called base.py as a common interface for visualization strategy
    - Migrate networkx specific implementation to contract subclass called networkx.py
    - Move networkx specific visualization to visualization_networkx.py
- Update tests/ to include this reorganization
