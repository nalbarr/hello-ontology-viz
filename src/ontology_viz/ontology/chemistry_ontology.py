from owlready2 import ObjectProperty, Thing, get_ontology, sync_reasoner


def get_my_ontology():
    onto = get_ontology("http://example.org/chemistry")

    with onto:
        class ChemicalCompound(Thing): pass
        class PFASSubstance(ChemicalCompound): pass
        class ChemicalElement(Thing): pass
        class Fluorine(ChemicalElement): pass
        class ChemicalBond(Thing): pass
        class MolecularComponent(Thing): pass

        # Define properties
        class hasElement(ObjectProperty):
            domain = [ChemicalCompound]
            range = [ChemicalElement]

        class hasBondType(ObjectProperty):
            domain = [ChemicalCompound]
            range = [ChemicalBond]

        class hasComponent(ObjectProperty):
            domain = [PFASSubstance]
            range = [MolecularComponent]

        # An inline constraint that should trigger an inference
        class OrganofluorinePollutant(ChemicalCompound):
            equivalent_to = [ChemicalCompound & hasElement.some(Fluorine)]

        # Assert individual facts (Stated layer)
        pfoa = PFASSubstance("PFOA")
        fluorine_atom = Fluorine("fluorine_atom")
        pfoa.hasElement.append(fluorine_atom)

        carbon_fluorine_bond = ChemicalBond("CarbonFluorineBond")
        pfoa.hasBondType.append(carbon_fluorine_bond)

        fluorinated_tail = MolecularComponent("FluorinatedTail")
        carboxylic_head = MolecularComponent("CarboxylicHead")
        pfoa.hasComponent.append(fluorinated_tail)
        pfoa.hasComponent.append(carboxylic_head)

        return onto


def compute_inferred_rels():
    sync_reasoner()
