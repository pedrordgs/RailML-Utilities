class NetElement:

    def __init__ (self, ident, length, line, linear, geometric):
        self.id = ident
        self.length = length
        self.line = line
        self.linear = linear
        self.geometric = geometric

        self.relations = []
        self.elementCollectionUnordered = []
        self.transitive_ecu = []

    def append_relation(self, rel):
      self.relations.append(rel)

    def append_element(self, elem):
      self.elementCollectionUnordered.append(elem)

    def set_transitive(self, list_):
      self.transitive_ecu = list_
