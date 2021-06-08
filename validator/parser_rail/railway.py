class Railway:

    def __init__(self):
        self.netElements = []
        self.netRelations = []
        self.networks = []
        self.positions = []

    def addNetElement(self, nelem):
        self.netElements.append(nelem)

    def addNetRelation(self, nrel):
        self.netRelations.append(nrel)

    def addNetwork(self, net):
        self.networks.append(net)

    def addPosition(self, pos):
        self.positions.append(pos)
