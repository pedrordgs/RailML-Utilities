#!/usr/bin/env python3

import jjcli as jj
import numpy as np
import sys
from colorama import Fore, Back, Style
from lxml import etree

filename = sys.argv[1]

# tree = ET.parse(filename)
tree = etree.parse(filename)
root = tree.getroot()

s = root.tag
p = "{" + s[s.find("{")+1:s.find("}")] + "}"

topology = root.find(f"./{p}infrastructure/{p}topology")
netElements = root.find(f"./{p}infrastructure/{p}topology/{p}netElements")
netRelations = root.find(f"./{p}infrastructure/{p}topology/{p}netRelations")
networks = root.find(f"./{p}infrastructure/{p}topology/{p}networks")

# All ids and all refs.
refs = root.findall(f"./{p}infrastructure/{p}topology//*[@ref]")
#refs.extend(root.findall(f"./{p}infrastructure/{p}topology//*[@positioningSystemRef]"))
ids = root.findall(f".//*[@id]")

dic_ids_tipo = {}
for x in ids:
    dic_ids_tipo[x.attrib['id']] = x.tag

# for k,v in dic_ids_tipo.items():
#     print(k, v)

# Estruturas auxiliares para testar redundancia entre netElements e netRelations
dic_elements  = {}
dic_relations = {}
dic_positioning = {}

# ---
# - Talvez criar tags que são associadas? Do tipo id numa, vai ser ref noutra tag.
# ---

dic_temp = {
        'associatedPositioningSystem' : ['geometricPositioningSystems', 'linearPositioningSystems'],
        'elementPart' : ['netElement'],
        'geometricCoordinate' : ['geometricPositioningSystem'],
        'linearCoordinate' : ['linearPositioningSystem'],
        'relation' : ['netRelation'],
        'elementA' : ['netElement'],
        'elementB' : ['netElement'],
        'networkResource' : ['netElement', 'netRelation']
        }

def validateTopologyRefs():
    for ref in refs:
        if ref.attrib['ref'] in dic_ids_tipo:
            if not dic_ids_tipo[ref.attrib['ref']].split('}')[1] in dic_temp[ref.tag.split('}')[1]]:
                print("{}: The type of the reference {} should be {}".format(
                    ref.sourceline,
                    ref.attrib['ref'],
                    dic_temp[ref.tag.split('}')[1]]
                    ))
        else:
          print("{}: The reference {} does not exit".format(ref.sourceline, ref.attrib['ref']))

# mudar para receber ficheiro xml como argumento o path
# do ficheiro e o respetivo schema
def validateXMLwithXSD(filename):
    schema_root = etree.parse("schema/railml3.xsd")
    xml_schema = etree.XMLSchema(schema_root)
    xml_doc = etree.parse(filename)
    try:
        xml_schema.assertValid(xml_doc)
    except Exception as e:
        print(Fore.RED + "ERROR:", end="")
        print(Style.RESET_ALL, e)
        return False
    return True

def pretty_print(str, b, erros):
    print(str)
    if b:
        print(Fore.GREEN + " True")
    else:
        print(Fore.RED + " False")
    print(Style.RESET_ALL, end="")
    if erros != "":
      print(erros)
    else:
      print("")

def getPositionIds():
    r = root.find(f"./{p}common/{p}positioning")
    for x in r:
        for xs in x:
            dic_positioning[xs.attrib['id']] = xs.tag

def nub(arr):
    return list(dict.fromkeys(arr))

# Retornava boolean
def netElementFunc(r, netElementRel):

    for x in r:
        if (x.tag == f"{p}relation"):
            # boolean = boolean and (r.attrib['id'][3:] in x.attrib['ref'][3:])
            netElementRel.append(x.attrib['ref'])
    return netElementRel

# -- NetElements --
def netElementsFunc(r):
    for x in r:
        # Lista auxiliar
        netElementRel = netElementFunc(x,[])
        dic_elements[x.attrib['id'].strip()] = netElementRel

# -- NetRelations --
def netRelationsFunc():
    #boolean = True
    for x in netRelations:
        netRelArray = []
        #netRelArray.append(x.attrib['id'])
        for xs in x:
            if xs.tag == f"{p}elementA" or xs.tag == f"{p}elementB":
              #boolean = boolean and (xs.attrib['ref'][3:] in x.attrib['id'][3:])
              netRelArray.append(xs.attrib['ref'])
        dic_relations[x.attrib['id'].strip()] = netRelArray

def check_redundancy() -> (bool, bool, str, str):
  b1 = True
  b2 = True
  erros1 = ""
  erros2 = ""

  # Verifica se cada elemento é referenciado nas relations a que refere.
  for element, rel in dic_elements.items():
    for r in rel:

      find_er = tree.find(f"./{p}infrastructure/{p}topology/{p}netElements/{p}netElement[@id = '{element}']/{p}relation[@ref='{r}']")
      find_ee = tree.find(f"./{p}infrastructure/{p}topology/{p}netElements/{p}netElement[@id = '{element}']")

      if r not in dic_relations.keys():
        b1 = False
        erros1 += "  Line " + str(find_er.sourceline) + " -> NetRelation " + r + ", referred in NetElement " + element + ", doesn't exist!\n"

      elif element not in dic_relations[r]:
        b1 = False
        erros1 += "  Line " + str(find_ee.sourceline) + " -> NetElement " + element + " is not referred in NetRelation " + r + ";\n"

  # Verifica se cada relation é referenciado nos elementos a que refere.
  for rel, elems in dic_relations.items():
    for e in elems:

      find_re = tree.find(f"./{p}infrastructure/{p}topology/{p}netRelations/{p}netRelation[@id = '{rel}']/*[@ref='{e}']")
      find_rr = tree.find(f"./{p}infrastructure/{p}topology/{p}netRelations/{p}netRelation[@id = '{rel}']")

      if e not in dic_elements.keys():
        b2 = False
        erros2 += "  Line " + str(find_re.sourceline) + " -> NetElement " + e + ", referred as "+ str(find_re.tag).replace(p,"") +" in NetRelation " + rel  + ", doesn't exist!\n"

      elif rel not in dic_elements[e]:
        b2 = False
        erros2 += "  Line " + str(find_rr.sourceline) + " -> NetRelation " + rel + " is not referred in NetElement " + e + ";\n"

  return(b1,b2,erros1,erros2)


validateTopologyRefs()
#(boolean_ids, e_ids) = validaAllRefs()
## (netElementRel,boolean) = netElementsFunc(netElements)
#netElementsFunc(netElements) # Preenchimento das relations para cada netElement.
#netRelationsFunc()

##print(xml_list)
#(boolean, boolean2, e1, e2) = check_redundancy() # Verificar se os dicionários elementos e relações é redundante.

getPositionIds()
# print(dic_positioning)

######################################################################
##                                                                   #
##                       PRINTS TO THE USER                          #
##                                                                   #
######################################################################
#pretty_print("Validating XML with a predefined Schema", validateXMLwithXSD(filename), "")

##pretty_print("Checking if every ref is a valid id",
##    np.array_equal(nub(sorted(list_ids)), nub(sorted(list_refs))), "")

#pretty_print("Checking if every ref is a valid id", boolean_ids, e_ids)

#pretty_print("Checking if every relation in a netElement has that netElement", boolean , e1)

#pretty_print("Checking if every relation in a netRelation has the specified elements", boolean2, e2)
