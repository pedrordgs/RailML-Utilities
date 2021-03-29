#!/usr/bin/env python3

import xml.etree.ElementTree as ET
import re

tree = ET.parse('railML.xml')
root = tree.getroot()

regex = re.compile('{.*}')

dic = {}

s = root.tag

# p = '{https://wwwd.railml.org/schemas/3.1}'
p = "{" + s[s.find("{")+1:s.find("}")] + "}"

print(p)


topology = root.find(f"./{p}infrastructure/{p}topology")

netElements = root.find(f"./{p}infrastructure/{p}topology/{p}netElement")
netRelations = root.find(f"./{p}infrastructure/{p}topology/{p}netRelations")
networks = root.find(f"./{p}infrastructure/{p}topology/{p}networks")
