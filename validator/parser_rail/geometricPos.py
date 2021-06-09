class GeometricPosition:

  def __init__ (self, ident, valid_from, valid_to):
    self.id = ident
    self.description = "Geometric"
    self.valid_from = valid_from
    self.valid_to = valid_to

    self.elements  = set()

  def append_element(self, e):
    self.elements.add(e)
