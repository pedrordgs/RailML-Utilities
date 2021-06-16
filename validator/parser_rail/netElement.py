class NetElement:

    def __init__ (self, ident, length, line):
        self.id = ident
        self.length = length
        self.line = line

        self.linear = {}
        self.geometric = {}

        self.networks = set()
        self.levels = set()
        self.parents = set()

        self.relations = []
        self.elementCollectionUnordered = []
        self.transitive_ecu = []

    def append_relation(self, rel):
      self.relations.append(rel)

    def append_element(self, elem):
      self.elementCollectionUnordered.append(elem)

    def set_transitive(self, list_):
      self.transitive_ecu = list_

    def append_network(self, netw):
      self.networks.add(netw)

    def append_level(self, l):
      self.levels.add(l)

    def append_parent(self, p):
      self.parents.add(p)

    def setLinear(self, l):
      self.linear = l

    def setGeometric(self, g):
      self.geometric = g
