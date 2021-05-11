#!/usr/bin/env python3
import jjcli as jj
import numpy as np
import sys
from colorama import Fore, Back, Style
from lxml import etree


def check_(filename):

  tree = etree.parse(filename)
  root = tree.getroot()

  s = root.tag
  p = "{" + s[s.find("{")+1:s.find("}")] + "}"

  # topology = root.find(f"./{p}infrastructure/{p}topology")
  # netElements = root.find(f"./{p}infrastructure/{p}topology/{p}netElements")
  # netRelations = root.find(f"./{p}infrastructure/{p}topology/{p}netRelations")
  # networks = root.find(f"./{p}infrastructure/{p}topology/{p}networks")

  # All ids and all refs.
  refs = root.findall(f"./{p}infrastructure/{p}topology//*[@ref]")
  ids = root.findall(f".//*[@id]")

  dic_ids_tipo = {}
  for x in ids:
    dic_ids_tipo[x.attrib['id']] = x.tag


  # Estruturas auxiliares para testar redundancia entre netElements e netRelations
  dic_elements  = {}
  dic_relations = {}
  dic_positioning = {}

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

  (b,e) = validateTopologyRefs(dic_ids_tipo, refs, dic_temp)

  ######################################################################
  ##                                                                   #
  ##                       PRINTS TO THE USER                          #
  ##                                                                   #
  ######################################################################
  pretty_print("Validating XML with a predefined Schema.", validateXMLwithXSD(filename), "")

  pretty_print("Checking if every ref is a valid id.", b, e)



def validateTopologyRefs(dic_ids_tipo, refs, dic_temp):
    b = True
    erros = ""

    for ref in refs:
        if ref.attrib['ref'] in dic_ids_tipo:
            if not dic_ids_tipo[ref.attrib['ref']].split('}')[1] in dic_temp[ref.tag.split('}')[1]]:
                erros += "Line {}: The type of the reference {} should be {}".format(
                    ref.sourceline,
                    ref.attrib['ref'],
                    dic_temp[ref.tag.split('}')[1]]
                    )
                b = False
        else:
          erros += "Line {}: The reference {} does not exit".format(ref.sourceline, ref.attrib['ref'])
          b = False
    return (b,erros)


# mudar para receber ficheiro xml como argumento o path
# do ficheiro e o respetivo schema
def validateXMLwithXSD(filename):
    schema_root = etree.parse("verifier/schema/railml3.xsd")
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

