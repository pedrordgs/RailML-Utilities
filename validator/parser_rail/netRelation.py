class NetRelation:

    def __init__ (self, ident, nav, line, posA, posB, elemA, elemB):

        self.id = ident
        self.navigability = nav
        self.line = line
        self.positionOnA = posA
        self.positionOnB = posB
        self.elementA = elemA
        self.elementB = elemB
        self.networks = set()
        self.associated = set()

    def append_network(self, netw):
      self.networks.add(netw)

    def append_relation(self, rel):
      self.associated.add(rel)

