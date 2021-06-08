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

def parsePosSystem(rail, pos_system, path='{https://www.railml.org/schemas/3.1}'):

  geometric = pos_system.find(f'./{path}geometricPositioningSystems')
  linear    = pos_system.find(f'./{path}linearPositioningSystems')

  for g in geometric:
    ident = g.get('id')
    # Valid
    valid_from = g.find(f'./{path}isValid').get('from')
    valid_to   = g.find(f'./{path}isValid').get('to')

    g_pos = GeometricPosition(ident, valid_from, valid_to)
    id_pos[ident] = g_pos

    rail.addPosition(g_pos)

  for l in linear:
    ident = l.get('id')
    units = l.get('units')
    start = l.get('startMeasure')
    end   = l.get('endMeasure')
    # Valid
    valid_from = l.find(f'./{path}isValid').get('from')
    valid_to   = l.find(f'./{path}isValid').get('to')

    l_pos = LinearPosition(ident, units, start, end, valid_from, valid_to)
    id_pos[ident] = l_pos

    rail.addPosition(l_pos)

def parseNetElements(rail, nelems, path='{https://www.railml.org/schemas/3.1}'):
    for elem in nelems:
        ident = elem.get('id')
        length = elem.get('length')
        line = elem.sourceline

        # associated Position System
        linear = {}
        geometric = {}

        intrisic = elem.findall(f'.//{path}intrinsicCoordinate')
        intrisic_0 = list(filter(lambda x: x.get('intrinsicCoord') == '0', intrisic))
        intrisic_1 = list(filter(lambda x: x.get('intrinsicCoord') == '1', intrisic))

        # intrisic coord as 0
        for i in intrisic_0:
              linears = i.findall(f'./{path}linearCoordinate')
              geometrics = i.findall(f'./{path}geometricCoordinate')

              for l in linears:
                ref = l.get('positioningSystemRef')
                l_system = id_pos[ref]

                if ref not in linear:
                  linear[ref] = {}
                  linear[ref]['start'] = []
                linear[ref]['start'].append((l_system, l.get('measure')))

              for g in geometrics:
                ref = g.get('positioningSystemRef')
                g_system = id_pos[ref]

                if ref not in geometric:
                  geometric[ref] = {}
                  geometric[ref]['start'] = []

                geometric[ref]['start'].append((g_system, g.get('x'), g.get('y')))

        # intrisic coord as 1
        for i in intrisic_1:
              linears = i.findall(f'./{path}linearCoordinate')
              geometrics = i.findall(f'./{path}geometricCoordinate')

              for l in linears:
                ref = l.get('positioningSystemRef')
                l_system = id_pos[ref]

                if ref not in linear:
                  print(f'\033[4mPARSING ERROR\033[0m: Element {ident} defined at Line {line} has as end coordinate reference {ref}, but not as begin reference.')
                  return

                if 'end' not in linear[ref]:
                  linear[ref]['end'] = []
                linear[ref]['end'].append((l_system, l.get('measure')))

              for g in geometrics:
                ref = g.get('positioningSystemRef')
                g_system = id_pos[ref]
                if ref not in geometric:
                  print(f'\033[4mPARSING ERROR\033[0m: Element {ident} defined at Line {line} has as end coordinate reference {ref}, but not as begin reference.')
                  return

                if 'end' not in geometric[ref]:
                  geometric[ref]['end'] = []
                geometric[ref]['end'].append((g_system, g.get('x'), g.get('y')))

        netelem = NetElement(ident,length,line, linear, geometric)
        # dict with id relationed with the element
        id_res[ident] = netelem
        rail.addNetElement(netelem)

        # If defined as reference id in elem->[elem] dict.
        if ident in elm_elm:
          for elm in elm_elm[ident]:
            elm.append_element(netelem)

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

        # Check if its defined on dict created for elems->relations
        if ident in rel_elm:
          for elm in rel_elm[ident]:
            elm.append_relation(netrel)

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
          net_resources = [id_res[e.attrib['ref']] for e in l]

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

    parsePosSystem(rail, pos_system)
    parseNetElements(rail, nelems)
    parseNetRelations(rail, nrels)
    parseNetworks(rail, networks)

    # stores the transitive elementCollectionUnordered for each element
    parseTransitiveElements(rail)

    return rail
