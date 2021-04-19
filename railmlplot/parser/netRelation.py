class NetRelation:

    def __init__ (self, ident, nav, posA, posB, elemA, elemB):
        self.navigability = nav
        self.positionOnA = posA
        self.positionOnB = posB
        self.elementA = elemA
        self.elementB = elemB
        self.id = ident
        # self.isValid = []
        # self.name = ''
