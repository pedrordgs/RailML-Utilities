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

def check_redundancy():
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
