class Alloy:

    def __init__ (self):
        self.instances = []

    def add_instance(self, instance):
        self.instances.append(instance)

    def to_string(self):
        s = 'Instances:\n'
        for i in self.instances:
            s += f'\t{i.filename}\n'
            s += '\tSigs:\n'
            for sig in i.sigs:
                s += f'\t\t{sig.label} {sig.id} {sig.parent} {sig.defs}\n'
                s += '\t\tAtoms:\n'
                for atom in sig.atoms:
                    s += f'\t\t\t{atom}\n'
            s += '\tFields:\n'
            for field in i.fields:
                s += f'\t\t{sig.label} {sig.id} {sig.parent} {sig.defs}\n'
                s += '\t\tTuples:\n'
                for t in field.tuples:
                    s += f'\t\t\t{t}\n'
                s += '\t\tTypes:\n'
                for tp in field.types:
                    s += f'\t\t\t{tp}\n'
        return s


