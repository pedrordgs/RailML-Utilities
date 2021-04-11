#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import numpy as np
import sys
from colorama import Fore, Back, Style
from lxml import etree

filename = sys.argv[1]

tree = ET.parse(filename)
root = tree.getroot()

s = root.tag
p = "{" + s[s.find("{")+1:s.find("}")] + "}"

topology = root.find(f"./{p}infrastructure/{p}topology")
netElements = root.find(f"./{p}infrastructure/{p}topology/{p}netElements")
netRelations = root.find(f"./{p}infrastructure/{p}topology/{p}netRelations")
networks = root.find(f"./{p}infrastructure/{p}topology/{p}networks")

# Estruturas auxiliares para testar redundancia entre netElements e netRelations
dic_elements  = {}
dic_relations = {}

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
    print(Style.RESET_ALL)
    if erros != "":
      print(erros)

def getPositionIds():
    r = root.find(f"./{p}common/{p}positioning")
    for x in r:
        for xs in x:
                print(xs.tag, xs.attrib)

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
      if r not in dic_relations.keys():
        b1 = False
        erros1 += "  -> NetRelation " + r + ", referred in NetElement " + element + ", doesn't exist!\n"

      elif element not in dic_relations[r]:
        b1 = False
        erros1 += "  -> NetElement " + element + " is not referred in NetRelation " + r + ";\n"

  # Verifica se cada relation é referenciado nos elementos a que refere.
  for rel, elems in dic_relations.items():
    for e in elems:
      if e not in dic_elements.keys():
        b2 = False
        erros2 += "  -> NetElement " + e + ", referred in NetRelation " + rel  + ", doesn't exist!\n"

      elif rel not in dic_elements[e]:
        b2 = False
        erros2 += "  -> NetRelation " + rel + " is not referred in NetElement " + e + ";\n"

  return(b1,b2,erros1,erros2)


# (netElementRel,boolean) = netElementsFunc(netElements)
netElementsFunc(netElements) # Preenchimento das relations para cada netElement.
netRelationsFunc()

(boolean, boolean2, e1, e2) = check_redundancy() # Verificar se os dicionários elementos e relações é redundante.

# postion_ids =
# getPositionIds()

#####################################################################
#                                                                   #
#                       PRINTS TO THE USER                          #
#                                                                   #
#####################################################################
pretty_print("Validating XML", validateXMLwithXSD(filename), "")

#pretty_print("Checking if every net element relation is declared in net relations",
    #np.array_equal(sorted(netRelArray), nub(sorted(netElementRel))))

pretty_print("Checking if every relation in a netElement has that netElement", boolean , e1)

pretty_print("Checking if every relation in a netRelation has the specified elements", boolean2, e2)
