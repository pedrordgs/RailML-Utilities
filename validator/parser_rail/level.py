class Level:

    def __init__(self, ident, desc, line, nresources):
        self.id = ident
        self.line = line
        self.description = desc
        self.networkResources = nresources

    def append_netRes(self, nr):
      self.networkResources.add(nr)

