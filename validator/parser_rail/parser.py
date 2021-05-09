import xml.etree.ElementTree as ET
from parser_rail.netElement import NetElement
from parser_rail.netRelation import NetRelation
from parser_rail.network import Network
from parser_rail.level import Level
from parser_rail.railway import Railway


def parseNetElements(rail, nelems, path='{https://www.railml.org/schemas/3.1}'):
    for elem in nelems:
        ident = elem.get('id')
        length = elem.get('length')
        relations = elem.findall(f'./{path}relation')
        r = []
        for rel in relations:
            r.append(rel.get('ref'))
        ecus = elem.findall(f'./{path}elementCollectionUnordered/{path}elementPart')
        ecus = ecus + elem.findall(f'./{path}elementCollectionOrdered/{path}elementPart')
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

def parseNetworks(rail, nets, path='{https://www.railml.org/schemas/3.1}'):
    for n in nets:
        net = n.get('id')
        # ident = 'net_' + net
        levels = n.findall(f'./{path}level')
        lvls_associated = []
        for l in levels:
          id_l  = l.attrib['id']
          descLevel = l.attrib['descriptionLevel']
          net_resources = [e.attrib['ref'] for e in l]

          lvls_associated.append(Level(id_l, descLevel, net_resources))
        rail.addNetwork(Network(net, lvls_associated))


def parseRailML(filename, path='{https://www.railml.org/schemas/3.1}'):
    rail = Railway()

    tree = ET.parse(filename)
    root = tree.getroot()

    nelems   = root.find(f'.//{path}netElements')
    nrels    = root.find(f'.//{path}netRelations')
    networks = root.find(f'.//{path}networks')

    parseNetElements(rail, nelems)
    parseNetRelations(rail, nrels)
    parseNetworks(rail, networks)

    return rail
