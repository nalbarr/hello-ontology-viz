from owlready2 import ObjectProperty, Thing, get_ontology, sync_reasoner


def get_my_ontology():
    onto = get_ontology("http://example.org")

    with onto:
        class Pizza(Thing): pass
        class MargheritaPizza(Pizza): pass
        class Topping(Thing): pass
        class CheeseTopping(Topping): pass

        # Define a property
        class hasTopping(ObjectProperty):
            domain = [Pizza]
            range = [Topping]

        # An inline constraint that should trigger an inference
        class CheesyPizza(Pizza):
            equivalent_to = [Pizza & hasTopping.some(CheeseTopping)]

        # Assert individual facts (Stated layer)
        my_pizza = MargheritaPizza("my_pizza")
        mozzarella = CheeseTopping("mozzarella")
        my_pizza.hasTopping.append(mozzarella)

        return onto


def compute_inferred_rels():
    sync_reasoner()
