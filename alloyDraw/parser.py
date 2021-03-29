import xml.etree.ElementTree as ET
from netElement import NetElement
from netRelation import NetRelation


def parseNetElement(node):
    r = []
    for _ in range(len(node)):
        r.append(NetElement())
    return r


def parseNetRelation(node):
    r = []
    for _ in range(len(node)):
        r.append(NetRelation())
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
        nrels[nr].setElementA(ne)

    for (nr, ne) in elemsB:
        nrels[nr].setElementB(ne)

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

    tree = ET.parse('example.xml')
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
