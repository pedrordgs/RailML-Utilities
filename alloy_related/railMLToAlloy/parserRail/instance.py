class Instance:

    def __init__ (self, alloyfp):
        self.bitwidth = '4'
        self.maxseq = '4'
        self.mintrace = '-1'
        self.maxtrace = '-1'
        self.filename = alloyfp
        self.tracel = '1'
        self.backl = '0'
        self.sigs = []
        self.fields = []

    def add_sig(self, sig):
        self.sigs.append(sig)

    def add_field(self, field):
        self.fields.append(field)





