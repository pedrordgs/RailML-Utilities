class NetElement:

    def __init__ (self):
        self.relations = []
        # self.length = -1
        # self.id = ''
        # self.associatedPositionSystem = []
        # self.elementCollectionOrdered = []
        # self.elementCollectionUnordered = []
        # self.isValid = []
        # self.name = ''

    def addRelation (self, net_relation):
        self.relations.append(net_relation)
