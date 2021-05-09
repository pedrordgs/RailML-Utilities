class Field:

    def __init__ (self, label, iden, parent, others):
        self.label = label
        self.id = iden
        self.parent = parent
        self.defs = others
        self.tuples = []
        self.types = []

    def add_tuple(self, t):
        self.tuples.append(t)

    def add_type(self, t):
        self.types.append(t)
