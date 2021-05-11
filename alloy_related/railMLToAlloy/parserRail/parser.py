import xml.etree.ElementTree as ET
from parserRail.alloy import Alloy
from parserRail.instance import Instance
from parserRail.sig import Sig
from parserRail.field import Field

path = '{https://www.railml.org/schemas/3.1}'

def int2Pos(x):
    if x == '0':
        return 'Zero$0'
    if x == '1':
        return 'One$0'
    else:
        return 'null'

def init_decl(instance):
    instance.add_sig(Sig('seq/Int', '0', '1', ['builtin']))
    instance.add_sig(Sig('Int', '1', '2', ['builtin']))
    instance.add_sig(Sig('String', '3', '2', ['builtin']))
    sig = Sig('this/None', '8', '9', ['one'])
    sig.add_atom('None$0')
    instance.add_sig(sig)
    sig = Sig('this/Both', '10', '9', ['one'])
    sig.add_atom('Both$0')
    instance.add_sig(sig)
    sig = Sig('this/AB', '11', '9', ['one'])
    sig.add_atom('AB$0')
    instance.add_sig(sig)
    sig = Sig('this/BA', '12', '9', ['one'])
    sig.add_atom('BA$0')
    instance.add_sig(sig)
    instance.add_sig(Sig('this/Navigability', '9', '2', ['abstract']))
    sig = Sig('this/Zero', '13', '14', ['one'])
    sig.add_atom('Zero$0')
    instance.add_sig(sig)
    sig = Sig('this/One', '15', '14', ['one'])
    sig.add_atom('One$0')
    instance.add_sig(sig)
    instance.add_sig(Sig('this/Position', '14', '2', ['abstract']))
    sig = Sig('this/Micro', '27', '25', ['one'])
    sig.add_atom('Micro$0')
    instance.add_sig(sig)
    sig = Sig('this/Meso', '28', '25', ['one'])
    sig.add_atom('Meso$0')
    instance.add_sig(sig)
    sig = Sig('this/Macro', '29', '25', ['one'])
    sig.add_atom('Macro$0')
    instance.add_sig(sig)
    instance.add_sig(Sig('this/DescriptionLevel', '25', '2', ['abstract']))
    instance.add_sig(Sig('univ', '2', '-1', ['builtin']))



def parseNetElements(instance, nelems):
    sig = Sig('this/NetElement', '4', '2', ['some'])
    i = 0
    nelem_id = {}
    for elem in nelems:
        sig.add_atom(f'NetElement${i}')
        nelem_id[elem.get('id')] = f'NetElement${i}'
        i += 1
    instance.add_sig(sig)
    return nelem_id
    

def parseNetRelations(instance, nrels):
    sig = Sig('this/NetRelation', '6', '2', [])
    i = 0
    nrel_id = {}
    for rel in nrels:
        sig.add_atom(f'NetRelation${i}')
        nrel_id[rel.get('id')] = f'NetRelation${i}'
        i += 1
    instance.add_sig(sig)
    return nrel_id


def parseNetworks(instance, nets):
    sig = Sig('this/Network', '21', '2', ['some'])
    i = 0
    net_id = {}
    for net in nets:
        sig.add_atom(f'Network${i}')
        net_id[net.get('id')] = f'Network${i}'
        i += 1
    instance.add_sig(sig)
    return net_id


def parseLevels(instance, levels):
    sig = Sig('this/Level', '23', '2', [])
    i = 0
    level_id = {}
    for lvl in levels:
        sig.add_atom(f'Level${i}')
        level_id[lvl.get('id')] = f'Level${i}'
        i += 1
    instance.add_sig(sig)
    return level_id


def parseRelations(instance, nelems, map_elems, map_rels):
    field = Field('relation', '5', '4', [])
    for elem in nelems:
        for rel in elem.findall(f'{path}relation'):
            field.add_tuple([map_elems[elem.get('id')], map_rels[rel.get('ref')]])
    field.add_type(['4', '6'])
    instance.add_field(field)
    

def parseCollection(instance, nelems, map_elems):
    field = Field('elementCollectionUnordered', '7', '4', [])
    for elem in nelems:
        for part in elem.findall(f'{path}elementCollectionUnordered/{path}elementPart'):
            field.add_tuple([map_elems[elem.get('id')], map_elems[part.get('ref')]])
        for part in elem.findall(f'{path}elementCollectionOrdered/{path}elementPart'):
            field.add_tuple([map_elems[elem.get('id')], map_elems[part.get('ref')]])
    field.add_type(['4', '4'])
    instance.add_field(field)


def parseNavigability(instance, nrels, map_rels):
    field = Field('navigability', '16', '6', [])
    for rel in nrels:
        field.add_tuple([map_rels[rel.get('id')], f'{rel.get("navigability")}$0'])
    field.add_type(['6', '9'])
    instance.add_field(field)


def parsePositions(instance, nrels, map_rels):
    posAf = Field('positionOnA', '17', '6', [])
    posBf = Field('positionOnB', '18', '6', [])
    for rel in nrels:
        posA = int2Pos(rel.get('positionOnA'))
        posB = int2Pos(rel.get('positionOnB'))
        posAf.add_tuple([map_rels[rel.get('id')], posA])
        posBf.add_tuple([map_rels[rel.get('id')], posB])
    posAf.add_type(['6', '14'])
    posBf.add_type(['6', '14'])
    instance.add_field(posAf)
    instance.add_field(posBf)
    

def parseElements(instance, nrels, map_rels, map_elems):
    elemAf = Field('elementA', '19', '6', [])
    elemBf = Field('elementB', '20', '6', [])
    for rel in nrels:
        elemA = rel.find(f'{path}elementA').get('ref')
        elemB = rel.find(f'{path}elementB').get('ref')
        elemAf.add_tuple([map_rels[rel.get('id')], map_elems[elemA]])
        elemBf.add_tuple([map_rels[rel.get('id')], map_elems[elemB]])
    elemAf.add_type(['6', '4'])
    elemBf.add_type(['6', '4'])
    instance.add_field(elemAf)
    instance.add_field(elemBf)


def parseNetLevels(instance, nets, map_nets, map_lvls):
    field = Field('level', '22', '21', [])
    for net in nets:
        for lvl in net.findall(f'{path}level'):
            field.add_tuple([map_nets[net.get('id')], map_lvls[lvl.get('id')]])
    field.add_type(['21', '23'])
    instance.add_field(field)


def parseDescriptionLevel(instance, nlvls, map_lvls):
    field = Field('descriptionLevel', '24', '23', [])
    for lvl in nlvls:
        field.add_tuple([map_lvls[lvl.get('id')], f'{lvl.get("descriptionLevel")}$0'])
    field.add_type(['23', '25'])
    instance.add_field(field)


def parseNetworkResources(instance, nlvls, map_lvls, map_elems, map_rels):
    field = Field('networkResource', '26', '23', [])
    for lvl in nlvls:
        for elem in lvl.findall(f'{path}networkResource'):
            if elem.get('ref') in map_elems:
                netr = map_elems[elem.get('ref')]
            else:
                netr = map_rels[elem.get('ref')]
            field.add_tuple([map_lvls[lvl.get('id')], netr])
    field.add_type(['23', '4'])
    field.add_type(['23', '6'])
    instance.add_field(field)


def parseToAlloy(filename, alloyfile):
    alloy = Alloy()

    tree = ET.parse(filename)
    root = tree.getroot()

    netElements = root.find(f'.//{path}netElements')
    netRelations = root.find(f'.//{path}netRelations')
    networks = root.find(f'.//{path}networks')
    network_levels = networks.findall(f'.//{path}level')

    instance = Instance(alloyfile)
    init_decl(instance)

    map_elems = parseNetElements(instance, netElements)
    map_rels = parseNetRelations(instance, netRelations)
    map_nets = parseNetworks(instance, networks)
    map_lvls = parseLevels(instance, network_levels)

    parseRelations(instance, netElements, map_elems, map_rels)
    parseCollection(instance, netElements, map_elems)
    parseNavigability(instance, netRelations, map_rels)

    parsePositions(instance, netRelations, map_rels)
    parseElements(instance, netRelations, map_rels, map_elems)

    parseNetLevels(instance, networks, map_nets, map_lvls)
    parseDescriptionLevel(instance, network_levels, map_lvls) 
    parseNetworkResources(instance, network_levels, map_lvls, map_elems, map_rels)


    alloy.add_instance(instance)

    return alloy
