from parserRail.parser import parseToAlloy
import xml.etree.ElementTree as ET

alloy = parseToAlloy('examples/railml.xml')


root = ET.Element('alloy')
root.set('builddate', "2021-02-23T10:54:30.238Z")


for instance in alloy.instances:
    ins = ET.Element('instance')
    ins.set('bitwidth', instance.bitwidth)
    ins.set('maxseq', instance.maxseq)
    ins.set('mintrace', instance.mintrace)
    ins.set('maxtrace', instance.maxtrace)
    ins.set('filename', instance.filename)
    ins.set('tracelength', instance.tracel)
    ins.set('backloop', instance.backl)

    for sig in instance.sigs:
        s = ET.Element('sig')
        s.set('label', sig.label)
        s.set('ID', sig.id)
        if sig.parent != '-1':
            s.set('parentID', sig.parent)
        for op in sig.defs:
            s.set(op, 'yes')
        for atom in sig.atoms:
            a = ET.Element('atom')
            a.set('label', atom)
            s.append(a)
        ins.append(s)

    for field in instance.fields:
        f = ET.Element('field')
        f.set('label', field.label)
        f.set('ID', field.id)
        f.set('parentID', field.parent)
        for op in field.defs:
            f.set(op, 'yes')
        for atms in field.tuples:
            t = ET.Element('tuple')
            for at in atms:
                ate = ET.Element('atom')
                ate.set('label', at)
                t.append(ate)
            f.append(t)
        for types in field.types:
            tp = ET.Element('types')
            for typ in types:
                te = ET.Element('type')
                te.set('ID', typ)
                tp.append(te)
            f.append(tp)
        ins.append(f)

    root.append(ins)

ET.dump(root)
