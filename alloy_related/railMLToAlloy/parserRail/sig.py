class Sig:

    def __init__ (self, label, iden, parent, others):
        self.label = label
        self.id = iden
        self.parent = parent
        self.defs = others
        self.atoms = []


    def add_atom(self, atom):
        self.atoms.append(atom)
