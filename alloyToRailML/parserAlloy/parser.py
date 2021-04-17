import xml.etree.ElementTree as ET
from parserAlloy.netElement import NetElement
from parserAlloy.netRelation import NetRelation
from parserAlloy.network import Network
from parserAlloy.level import Level
from parserAlloy.railway import Railway


def strToPos(pos):
    if pos == 'Zero':
        return 0
    else:
        return 1


def parseNetElement(rail, nelems, rels):
    for elem in nelems:
        nelem = elem.get('label').split('$')[1]
        ident = 'ne_' + nelem
        assoc_rels = rels.findall(f'.//atom[@label="NetElement${nelem}"]/..')
        r = []
        for rel in assoc_rels:
            netr = 'nr_' + rel[1].get('label').split('$')[1]
            print(f'{ident} {netr}')
            r.append(netr)
        rail.addNetElement(NetElement(ident, r))



def parseNetRelation(rail, nrels, navs, possA, possB, elemsA, elemsB):
    for rel in nrels:
        nrel = rel.get('label').split('$')[1]
        ident = 'nr_' + nrel
        nav = navs.find(f'.//atom[@label="NetRelation${nrel}"]/..')[1].get('label').split('$')[0]
        posA = strToPos(possA.find(f'.//atom[@label="NetRelation${nrel}"]/..')[1].get('label').split('$')[0])
        posB = strToPos(possB.find(f'.//atom[@label="NetRelation${nrel}"]/..')[1].get('label').split('$')[0])
        elemA = 'ne_' + elemsA.find(f'.//atom[@label="NetRelation${nrel}"]/..')[1].get('label').split('$')[1]
        elemB = 'ne_' + elemsB.find(f'.//atom[@label="NetRelation${nrel}"]/..')[1].get('label').split('$')[1]
        print(f'{ident} {nav} {posA} {posB} {elemA} {elemB}')
        rail.netRelations.append(NetRelation(ident, nav, posA, posB, elemA, elemB))


def parseNetworks(rail, nets, lvls, desc_lvl, net_res):
    for n in nets:
        net = n.get('label').split('$')[1]
        ident = 'net_' + net
        levels = lvls.findall(f'.//atom[@label="Network${net}"]/..')
        lvls = []
        for l in levels:
            lvl = l[1].get('label')
            lvl_id = 'lvl_' + lvl.split('$')[1]
            desc = desc_lvl.find(f'.//atom[@label="{lvl}"]/..')[1].get('label').split('$')[0]
            netr_node = net_res.findall(f'.//atom[@label="{lvl}"]/..')
            net_resources = []
            for netr in netr_node:
                s = netr[1].get('label').split('$')
                if s[0] == 'NetElement':
                    net_resources.append('ne_' + s[1])
                else:
                    net_resources.append('nr_' + s[1])
            print(f'{ident} {lvl_id} {desc} {net_resources}')
            lvls.append(Level(lvl_id, desc, net_resources))
        rail.networks.append(Network(ident, lvls))



def parseAlloyXML(filename):
    rail = Railway()

    tree = ET.parse(filename)
    instance = tree.getroot()[0]

    nelems = tree.find(f'.//sig[@label="this/NetElement"]')
    rels = tree.find(f'.//field[@label="relation"]')

    parseNetElement(rail, nelems, rels)

    nrels = tree.find(f'.//sig[@label="this/NetRelation"]')
    navs = tree.find(f'.//field[@label="navigability"]')
    possA = tree.find(f'.//field[@label="positionOnA"]')
    possB = tree.find(f'.//field[@label="positionOnB"]')
    elemsA = tree.find(f'.//field[@label="elementA"]')
    elemsB = tree.find(f'.//field[@label="elementB"]')

    parseNetRelation(rail, nrels, navs, possA, possB, elemsA, elemsB)

    nets = tree.find(f'.//sig[@label="this/Network"]')
    lvls = tree.find(f'.//field[@label="level"]')
    desc_lvl = tree.find(f'.//field[@label="descriptionLevel"]')
    net_res = tree.find(f'.//field[@label="networkResource"]')

    parseNetworks(rail, nets, lvls, desc_lvl, net_res)

    return rail

