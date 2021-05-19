from lxml import etree
from parser_rail.netElement import NetElement
from parser_rail.netRelation import NetRelation
from parser_rail.network import Network
from parser_rail.level import Level
from parser_rail.railway import Railway

rel_elm = {}
elm_elm = {}
id_res  = {}

def parseNetElements(rail, nelems, path='{https://www.railml.org/schemas/3.1}'):
    for elem in nelems:
        ident = elem.get('id')
        length = elem.get('length')
        line = elem.sourceline

        netelem = NetElement(ident,length,line)
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

    nelems   = root.find(f'.//{path}netElements')
    nrels    = root.find(f'.//{path}netRelations')
    networks = root.find(f'.//{path}networks')

    parseNetElements(rail, nelems)
    parseNetRelations(rail, nrels)
    parseNetworks(rail, networks)

    # stores the transitive elementCollectionUnordered for each element
    parseTransitiveElements(rail)

    return rail
