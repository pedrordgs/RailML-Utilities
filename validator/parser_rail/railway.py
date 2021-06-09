class Railway:

    def __init__(self):
        self.netElements = []
        self.netRelations = []
        self.networks = []
        self.linear = []
        self.geometric = []

    def addNetElement(self, nelem):
        self.netElements.append(nelem)

    def addNetRelation(self, nrel):
        self.netRelations.append(nrel)

    def addNetwork(self, net):
        self.networks.append(net)

    def addLinear(self, pos):
        self.linear.append(pos)

    def addGeometric(self, pos):
        self.geometric.append(pos)
