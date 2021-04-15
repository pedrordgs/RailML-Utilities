import xml.etree.ElementTree as ET
from netElement import NetElement
from netRelation import NetRelation


def parseNetElement(node):
    r = []
    for elem in node:
        ident = 'ne_' + elem.get('label').split('$')[1]
        r.append(NetElement(ident))
    return r


def parseNetRelation(node):
    r = []
    for rel in node:
        ident = 'nr_' + rel.get('label').split('$')[1]
        r.append(NetRelation(ident))
    return r


def parseRelations(node):
    r = []
    for gchild in node:
        if gchild.tag == 'tuple':
            ne = int(gchild[0].get('label').split('$')[1])
            nr = int(gchild[1].get('label').split('$')[1])
            r.append((ne, nr))
    return r


def parseNavigability(node):
    r = []
    for gchild in node:
        if gchild.tag == 'tuple':
            nr = int(gchild[0].get('label').split('$')[1])
            nav = gchild[1].get('label').split('$')[0]
            r.append((nr, nav))
    return r


def parsePositions(node):
    r = []
    for gchild in node:
        if gchild.tag == 'tuple':
            nr = int(gchild[0].get('label').split('$')[1])
            # pos = gchild[1].get('label').split('$')[0]
            # if pos == 'Zero':
            #     r.append((nr, 0))
            # else:
            #     r.append((nr, 1))
            pos = int(gchild[1].get('label').split('$')[1])
            r.append((nr, pos))
    return r


def parseElements(node):
    r = []
    for gchild in node:
        if gchild.tag == 'tuple':
            nr = int(gchild[0].get('label').split('$')[1])
            ne = int(gchild[1].get('label').split('$')[1])
            r.append((nr, ne))
    return r


def organizeInfo(nelems, nrels, rels, navs, posA, posB, elemsA, elemsB):
    for (ne, nr) in rels:
        nelems[ne].addRelation(nrels[nr])

    for (nr, nav) in navs:
        nrels[nr].setNavigability(nav)

    for (nr, pos) in posA:
        nrels[nr].setPositionOnA(pos)

    for (nr, pos) in posB:
        nrels[nr].setPositionOnB(pos)

    for (nr, ne) in elemsA:
        nrels[nr].setElementA(nelems[ne])

    for (nr, ne) in elemsB:
        nrels[nr].setElementB(nelems[ne])

    return (nelems, nrels)



def parseXML (filename):
    nelems = []
    nresl = []
    rels = []
    navs = []
    posA = []
    posB = []
    elemsA = []
    elemsB = []

    tree = ET.parse(filename)
    instance = tree.getroot()[0]

    for child in instance:
        label = child.get('label')
        if label == 'this/NetElement':
            nelems = parseNetElement(child)
        if label == 'this/NetRelation':
            nrels = parseNetRelation(child)
        if label == 'relation':
            rels = parseRelations(child)
        if label == 'navigability':
            navs = parseNavigability(child)
        if label == 'positionOnA':
            posA = parsePositions(child)
        if label == 'positionOnB':
            posB = parsePositions(child)
        if label == 'elementA':
            elemsA = parseElements(child)
        if label == 'elementB':
            elemsB = parseElements(child)

    return organizeInfo(nelems, nrels, rels, navs, posA, posB, elemsA, elemsB)


path = '{https://www.railml.org/schemas/3.1}'


(a, b) = parseXML("example.xml")

tree = ET.parse("template.xml")
instance = tree.getroot()


netElements = instance.find(f'.//{path}netElements')
netRelations = instance.find(f'.//{path}netRelations')


count = 0
for nelem in a:
    new = ET.Element('netElement')
    new.set('id', nelem.id)
    new.set('length', str(nelem.length))
    for rel in nelem.relations:
        nrel = ET.Element('relation')
        nrel.set('ref', rel.id)
        new.append(nrel)
    netElements.append(new)
    count = count + 1

for nrel in b:
    new = ET.Element('netRelation')
    new.set('id', nrel.id)
    new.set('positionOnA', str(nrel.positionOnA))
    new.set('positionOnB', str(nrel.positionOnB))
    new.set('navigability', str(nrel.navigability))
    elemA = ET.Element('elementA')
    elemA.set('ref', nrel.elementA.id)
    new.append(elemA)
    elemB = ET.Element('elementB')
    elemB.set('ref', nrel.elementB.id)
    new.append(elemB)
    netRelations.append(new)


# TODO networks

tree.write('converted.xml')
