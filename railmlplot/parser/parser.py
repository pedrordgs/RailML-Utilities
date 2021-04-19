import xml.etree.ElementTree as ET
from netElement import NetElement
from netRelation import NetRelation
from network import Network
from level import Level
from railway import Railway


def parseNetElements(rail, nelems, path='{https://www.railml.org/schemas/3.1}'):
    for elem in nelems:
        ident = elem.get('id')
        length = elem.get('length')
        relations = elem.findall(f'./{path}relation')
        r = []
        for rel in relations:
            r.append(rel.get('ref'))
        ecus = elem.findall(f'./{path}elementCollectionUnordered/{path}elementPart')
        ecol= []
        for e in ecus:
            ecol.append(e.get('ref'))
        rail.addNetElement(NetElement(ident, length, r, ecol))


def parseNetRelations(rail, nrels, path='{https://www.railml.org/schemas/3.1}'):
    for nrel in nrels:
        ident = nrel.get('id')
        posA = nrel.get('positionOnA')
        posB = nrel.get('positionOnB')
        nav = nrel.get('navigability')
        elemA = nrel.find(f'./{path}elementA').get('ref')
        elemB = nrel.find(f'./{path}elementB').get('ref')
        rail.addNetRelation(NetRelation(ident, nav, posA, posB, elemA, elemB))

### TODO: parseNetworks

def parseRailML(filename, path='{https://www.railml.org/schemas/3.1}'):
    rail = Railway()

    tree = ET.parse('railML.xml')
    root = tree.getroot()

    nelems = root.find(f'.//{path}netElements')
    nrels = root.find(f'.//{path}netRelations')

    parseNetElements(rail, nelems)
    parseNetRelations(rail, nrels)

    for elem in rail.netElements:
        print(f'{elem.id} {elem.length} {elem.relations} {elem.elementCollectionUnordered}')

    print('\n')

    for rel in rail.netRelations:
        print(f'{rel.id} {rel.navigability} {rel.positionOnA} {rel.positionOnB} {rel.elementA} {rel.elementB}')

    return rail
