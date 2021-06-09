class GeometricPosition:

  def __init__ (self, ident, line, valid_from, valid_to):
    self.id = ident
    self.line = line
    self.description = "Geometric"
    self.valid_from = valid_from
    self.valid_to = valid_to

    self.elements  = set()
    self.relations = set()

  def append_element(self, e):
    self.elements.add(e)

  def append_relation(self, r):
    self.relations.add(r)
