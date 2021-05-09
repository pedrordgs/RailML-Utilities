class NetElement:

    def __init__ (self, ident, rels, ecu):
        self.relations = rels
        self.length = 0
        self.id = ident
        # self.associatedPositionSystem = []
        # self.elementCollectionOrdered = []
        self.elementCollectionUnordered = ecu
        # self.isValid = []
        # self.name = ''
