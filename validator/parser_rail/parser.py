from lxml import etree
from parser_rail.netElement import NetElement
from parser_rail.netRelation import NetRelation
from parser_rail.network import Network
from parser_rail.geometricPos import GeometricPosition
from parser_rail.linearPos import LinearPosition
from parser_rail.level import Level
from parser_rail.railway import Railway

rel_elm = {}
elm_elm = {}
id_res  = {}
id_pos  = {}
id_rel  = {}

def parsePosSystem(rail, pos_system, path='{https://www.railml.org/schemas/3.1}'):

  geometric = pos_system.find(f'./{path}geometricPositioningSystems')
  linear    = pos_system.find(f'./{path}linearPositioningSystems')

  for g in geometric:
    ident = g.get('id')
    line = g.sourceline
    # Valid
    valid_from = g.find(f'./{path}isValid').get('from')
    valid_to   = g.find(f'./{path}isValid').get('to')

    g_pos = GeometricPosition(ident, line, valid_from, valid_to)
    id_pos[ident] = g_pos

    rail.addGeometric(g_pos)

  for l in linear:
    ident = l.get('id')
    units = l.get('units')
    line  = l.sourceline
    start = l.get('startMeasure')
    end   = l.get('endMeasure')
    # Valid
    valid_from = l.find(f'./{path}isValid').get('from')
    valid_to   = l.find(f'./{path}isValid').get('to')

    l_pos = LinearPosition(ident, units, line, start, end, valid_from, valid_to)
    id_pos[ident] = l_pos

    rail.addLinear(l_pos)

def parseNetElements(rail, nelems, path='{https://www.railml.org/schemas/3.1}'):
    for elem in nelems:
        ident = elem.get('id')
        length = elem.get('length')
        line = elem.sourceline

        netelem = NetElement(ident,length,line)
        # dict with id relationed with the element
        id_res[ident] = netelem
        rail.addNetElement(netelem)

        # associated Position System
        linear = {}
        geometric = {}

        intrisic = elem.findall(f'.//{path}intrinsicCoordinate')
        intrisic_0 = list(filter(lambda x: x.get('intrinsicCoord') == '0', intrisic))
        intrisic_1 = list(filter(lambda x: x.get('intrinsicCoord') == '1', intrisic))
        middle_intrinsic = list(filter(lambda x: x.get('intrinsicCoord') != '1' and x.get('intrinsicCoord') != '0', intrisic))

        # intrisic coord as 0
        for i in intrisic_0:
              linears = i.findall(f'./{path}linearCoordinate')
              geometrics = i.findall(f'./{path}geometricCoordinate')

              for l in linears:
                ref = l.get('positioningSystemRef')
                l_system = id_pos[ref]

                # Append to elements of the position system
                l_system.append_element(netelem)

                if ref not in linear:
                  linear[ref] = {}
                  linear[ref]['start'] = []
                linear[ref]['start'].append((l_system, l.get('measure')))

              for g in geometrics:
                ref = g.get('positioningSystemRef')
                g_system = id_pos[ref]

                # Append to elements of the position system
                g_system.append_element(netelem)

                if ref not in geometric:
                  geometric[ref] = {}
                  geometric[ref]['start'] = []

                geometric[ref]['start'].append((g_system, g.get('x'), g.get('y')))

        # intrisic coord between 0 and 1
        for i in middle_intrinsic:
              linears = i.findall(f'./{path}linearCoordinate')
              geometrics = i.findall(f'./{path}geometricCoordinate')

              for l in linears:
                ref = l.get('positioningSystemRef')
                l_system = id_pos[ref]

                # Append to elements of the position system
                # l_system.append_element(netelem)

                if ref not in linear:
                  linear[ref] = {}
                  linear[ref]['middle'] = []
                linear[ref]['middle'].append((i.get('intrinsicCoord'),l_system, l.get('measure')))

              for g in geometrics:
                ref = g.get('positioningSystemRef')
                g_system = id_pos[ref]

                # Append to elements of the position system
                # g_system.append_element(netelem)

                if ref not in geometric:
                  geometric[ref] = {}
                  geometric[ref]['middle'] = []

                geometric[ref]['middle'].append((i.get('intrinsicCoord'), g_system, g.get('x'), g.get('y')))

        # intrisic coord as 1
        for i in intrisic_1:
              linears = i.findall(f'./{path}linearCoordinate')
              geometrics = i.findall(f'./{path}geometricCoordinate')

              for l in linears:
                ref = l.get('positioningSystemRef')
                l_system = id_pos[ref]

                # Append to elements of the position system
                l_system.append_element(netelem)

                if ref not in linear:
                  print(f'\033[4mPARSING ERROR\033[0m: Element {ident} defined at Line {line} has as end coordinate reference {ref}, but not as begin reference.')
                  return

                if 'end' not in linear[ref]:
                  linear[ref]['end'] = []
                linear[ref]['end'].append((l_system, l.get('measure')))

              for g in geometrics:
                ref = g.get('positioningSystemRef')
                g_system = id_pos[ref]

                # Append to elements of the position system
                g_system.append_element(netelem)

                if ref not in geometric:
                  print(f'\033[4mPARSING ERROR\033[0m: Element {ident} defined at Line {line} has as end coordinate reference {ref}, but not as begin reference.')
                  return

                if 'end' not in geometric[ref]:
                  geometric[ref]['end'] = []
                geometric[ref]['end'].append((g_system, g.get('x'), g.get('y')))

        netelem.setLinear(linear)
        netelem.setGeometric(geometric)

        # If defined as reference id in elem->[elem] dict.
        if ident in elm_elm:
          for elm in elm_elm[ident]:
            elm.append_element(netelem)

        # Instead of storing just the id of the relation, its stored the realtion itself -> For that we need a auxiliar dict
        relations = elem.findall(f'./{path}relation')
        for rel in relations:
            ref = rel.get('ref')
            if ref in rel_elm:
              rel_elm[ref].append(netelem)
            else:
              rel_elm[ref] = []
              rel_elm[ref].append(netelem)


        # Elements part of this element
        ecus = elem.findall(f'./{path}elementCollectionUnordered/{path}elementPart')
        ecus = ecus + elem.findall(f'./{path}elementCollectionOrdered/{path}elementPart')
        for e in ecus:
            ref = e.get('ref')
            if ref in id_res:
              r_aux = id_res[ref]
              netelem.append_element(r_aux)
            else:
              if ref in elm_elm:
                elm_elm[ref].append(netelem)
              else:
                elm_elm[ref] = []
                elm_elm[ref].append(netelem)


def parseNetRelations(rail, nrels, path='{https://www.railml.org/schemas/3.1}'):
    for nrel in nrels:
        ident = nrel.get('id')
        line = nrel.sourceline
        posA = nrel.get('positionOnA')
        posB = nrel.get('positionOnB')
        nav = nrel.get('navigability')

        elemA = nrel.find(f'./{path}elementA').get('ref')
        netelemA = id_res[elemA]
        elemB = nrel.find(f'./{path}elementB').get('ref')
        netelemB = id_res[elemB]

        netrel = NetRelation(ident,nav,line,posA,posB,netelemA,netelemB)

        # dict with id relationed with the element
        id_res[ident] = netrel

        rail.addNetRelation(netrel)

        # Append relation to Positioning System
        for linear in netelemA.linear:
          if linear in netelemB.linear:
            posl = id_pos[linear]
            posl.append_relation(netrel)

        # Append relation to Positioning System
        for geometric in netelemA.geometric:
          if geometric in netelemB.geometric:
            posg = id_pos[geometric]
            posg.append_relation(netrel)

        # Check if its defined on dict created for elems->relations
        if ident in rel_elm:
          for elm in rel_elm[ident]:
            elm.append_relation(netrel)

        # Create associated relations for each relation -> In order to check properties like switches
        for re in id_rel:
          rel = id_rel[re]
          if rel.elementA == netelemA and rel.positionOnA == posA:
            netrel.append_relation(rel)
            rel.append_relation(netrel)
          if rel.elementB == netelemB and rel.positionOnB == posB:
            netrel.append_relation(rel)
            rel.append_relation(netrel)
          if rel.elementB == netelemA and rel.positionOnB == posA:
            netrel.append_relation(rel)
            rel.append_relation(netrel)
          if rel.elementA == netelemB and rel.positionOnA == posB:
            netrel.append_relation(rel)
            rel.append_relation(netrel)

        # dict with id -> netrel
        id_rel[ident] = netrel

def parseNetworks(rail, nets, path='{https://www.railml.org/schemas/3.1}'):
    for n in nets:

        net = n.get('id')
        line = n.sourceline
        levels = n.findall(f'./{path}level')
        lvls_associated = []

        for l in levels:

          id_l  = l.attrib['id']
          line_l = l.sourceline
          descLevel = l.attrib['descriptionLevel']

          # Get the reference to its class element
          net_resources = []
          for e in l:
            nr = id_res[e.attrib['ref']]
            nr.append_network(n)
            net_resources.append(nr)

          lvls_associated.append(Level(id_l, descLevel, line_l, net_resources))
        rail.addNetwork(Network(net, line, lvls_associated))


# Transitive closure of each element -> checked is useful in order to check for repetitive elements
def loop_elements(element, checked) -> list:
    if element.elementCollectionUnordered:
      l = element.elementCollectionUnordered
    else:
      return []
    for e in l:
      if e not in checked:
        checked.append(e)
        l = l + loop_elements(e, checked)
    return l

def parseTransitiveElements(rail):
  for elm in rail.netElements:
    list_elements = loop_elements(elm, [])
    elm.set_transitive(list_elements)


# Main function that calls every parser
def parseRailML(filename, path='{https://www.railml.org/schemas/3.1}'):
    rail = Railway()

    tree = etree.parse(filename)
    root = tree.getroot()

    pos_system = root.find(f'.//{path}positioning')
    nelems     = root.find(f'.//{path}netElements')
    nrels      = root.find(f'.//{path}netRelations')
    networks   = root.find(f'.//{path}networks')
    # buffers    = root.find(f'.//{path}bufferStops')
    # switches   = root.find(f'.//{path}switchesIS')
    # signals    = root.find(f'.//{path}signalsIS')

    if not pos_system is None:
      parsePosSystem(rail, pos_system)
    parseNetElements(rail, nelems)
    parseNetRelations(rail, nrels)
    parseNetworks(rail, networks)

    # stores the transitive elementCollectionUnordered for each element
    parseTransitiveElements(rail)

    return rail
