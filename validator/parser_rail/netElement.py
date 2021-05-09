class NetElement:

    def __init__ (self, ident, l, rels, ecu):
        self.relations = rels
        self.length = l
        self.id = ident
        # self.associatedPositionSystem = []
        # self.elementCollectionOrdered = []
        self.elementCollectionUnordered = ecu
        # self.isValid = []
        # self.name = ''
