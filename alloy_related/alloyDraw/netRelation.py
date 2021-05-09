class NetRelation:

    def __init__ (self):
        self.navigability = ''
        self.positionOnA = -1
        self.positionOnB = -1
        self.elementA = None
        self.elementB = None
        # self.id = ''
        # self.isValid = []
        # self.name = ''

    def setNavigability (self, nav):
        self.navigability = nav

    def setPositionOnA (self, pos):
        self.positionOnA = pos

    def setPositionOnB (self, pos):
        self.positionOnB = pos

    def setElementA (self, elem):
        self.elementA = elem

    def setElementB (self, elem):
        self.elementB = elem

