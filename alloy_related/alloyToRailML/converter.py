from parserAlloy.parser import parseAlloyXML
import xml.etree.ElementTree as ET
import sys

input_file = sys.argv[1]
out_file = sys.argv[2]

path = '{https://www.railml.org/schemas/3.1}'

ET.register_namespace('', 'https://www.railml.org/schemas/3.1')
ET.register_namespace('dc', 'http://purl.org/dc/elements/1.1/')
ET.register_namespace('gml', 'http://www.opengis.net/gml/3.2/')
ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

tree = ET.parse('template.xml')
instance = tree.getroot()


netElements = instance.find(f'.//{path}netElements')
netRelations = instance.find(f'.//{path}netRelations')
networks = instance.find(f'.//{path}networks')


rail = parseAlloyXML(input_file)

for nelem in rail.netElements:
    new = ET.Element(f'{path}netElement')
    new.set('id', nelem.id)
    new.set('length', str(nelem.length))
    for rel in nelem.relations:
        nrel = ET.Element(f'{path}relation')
        nrel.set('ref', rel)
        new.append(nrel)
    el = ET.Element(f'{path}elementCollectionUnordered')
    el.set('id', f'ecu_{nelem.id}')
    for elem in nelem.elementCollectionUnordered:
        elemPart = ET.Element(f'{path}elementPart')
        elemPart.set('ref', elem)
        el.append(elemPart)
    new.append(el)
    assoc_pos = ET.Element(f'{path}associatedPositioningSystem')
    assoc_pos.set('id', f'aps_{nelem.id}')
    intrinsic_coord = ET.Element(f'{path}intrinsicCoordinate')
    intrinsic_coord.set('id', f'ic_aps_{nelem.id}')
    intrinsic_coord.set('intrinsicCoord', '0')
    assoc_pos.append(intrinsic_coord)
    new.append(assoc_pos)
    netElements.append(new)

for nrel in rail.netRelations:
    new = ET.Element(f'{path}netRelation')
    new.set('id', nrel.id)
    new.set('positionOnA', str(nrel.positionOnA))
    new.set('positionOnB', str(nrel.positionOnB))
    new.set('navigability', nrel.navigability)
    elemA = ET.Element(f'{path}elementA')
    elemA.set('ref', nrel.elementA)
    new.append(elemA)
    elemB = ET.Element(f'{path}elementB')
    elemB.set('ref', nrel.elementB)
    new.append(elemB)
    netRelations.append(new)


for net in rail.networks:
    new = ET.Element(f'{path}network')
    new.set('id', net.id)
    for l in net.levels:
        lvl = ET.Element(f'{path}level')
        lvl.set('id', l.id)
        lvl.set('descriptionLevel', l.description)
        for nres in l.networkResources:
            n = ET.Element(f'{path}networkResource')
            n.set('ref', nres)
            lvl.append(n)
        new.append(lvl)
    networks.append(new)

tree.write(out_file)
