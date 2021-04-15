class NetElement:

    def __init__ (self, ident):
        self.relations = []
        self.length = 0
        self.id = ident
        # self.associatedPositionSystem = []
        # self.elementCollectionOrdered = []
        # self.elementCollectionUnordered = []
        # self.isValid = []
        # self.name = ''

    def addRelation (self, net_relation):
        self.relations.append(net_relation)
