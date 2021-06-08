class LinearPosition:

  def __init__ (self, ident, units, start, end, valid_from, valid_to):

    self.id = ident
    self.units = units
    self.description = "Linear"
    self.startMeasure = start
    self.endMeasure = end
    self.valid_from = valid_from
    self.valid_to = valid_to
