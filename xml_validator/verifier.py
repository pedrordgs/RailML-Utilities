#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import re
import numpy as np
from colorama import Fore, Back, Style

tree = ET.parse('railML.xml')
root = tree.getroot()

regex = re.compile('{.*}')

dic = {}

s = root.tag

# p = '{https://wwwd.railml.org/schemas/3.1}'
p = "{" + s[s.find("{")+1:s.find("}")] + "}"


topology = root.find(f"./{p}infrastructure/{p}topology")

netElements = root.find(f"./{p}infrastructure/{p}topology/{p}netElements")
netRelations = root.find(f"./{p}infrastructure/{p}topology/{p}netRelations")
networks = root.find(f"./{p}infrastructure/{p}topology/{p}networks")

# True if every netElement is present in its relations
boolean = True

def nub(arr):
    return list(dict.fromkeys(arr))

def netElementFunc(r, netElementRel):
    global boolean
    for x in r:
        if (x.tag == f"{p}relation"):
            boolean = boolean and (r.attrib['id'][3:] in x.attrib['ref'][3:])
            netElementRel.append(x.attrib['ref'])

def netElementsFunc(r):
    netElementRel = []
    for x in r:
        netElementFunc(x,netElementRel)
    return netElementRel

def netRelationsFunc():
    netRelArray = []
    for x in netRelations:
        netRelArray.append(x.attrib['id'])
    return netRelArray

netElementRel = netElementsFunc(netElements)
netRelArray = netRelationsFunc()

def pretty_print(str, b):
    print(str)
    if b:
        print(Fore.GREEN + " True")
    else:
        print(Fore.RED + " False")
    print(Style.RESET_ALL)








pretty_print("Checking if every net element relation is declared in net relations",
    np.array_equal(sorted(netRelArray), nub(sorted(netElementRel))))

pretty_print("Checking if every relation in a netElement has that netElement", boolean)
