# Main function that will call every property verification.
def assumptions_(r):

  global railw
  railw = r


  # netElements assumptions - Redudancy and elementCollectionUnordered
  netElements_assumptions()
  # If a NetElement is connected to two different NetElements in same endpoint, those must also be connected
  elementOn()
  # netRelations assumptions
  netRelations_assumptions()
  # extendNetworks properties - extend Micro should be on extend Meso and so on
  extendNetwork_assumptions()


# Redundacy with netRelations and no loops on elementCollectionUnordered
def netElements_assumptions():

  # Pair netElement with each netRelation
  l  = [(e.id,r) for e in railw.netElements for r in e.relations]
  l1 = []
  for r in railw.netRelations:
    l1.append((r.elementA, r.id))
    l1.append((r.elementB, r.id))

  if sorted(l) == sorted(l1):
    print('Relations are redudant.')
  else:
    print('Redudancy is not preserved.')

  # Check if there's no loop in element Collection Unordered
  dic_elementsp = {}
  for e in railw.netElements:
    if e.elementCollectionUnordered:
      temp = e.elementCollectionUnordered
      dic_elementsp[e.id] = temp

  # Definition of alloy extend.
  global cU_TranClosure
  cU_TranClosure = {}


  b_cU = True
  # Transitive closure of each element
  for e in dic_elementsp:
    l_cU = calcula_cU(e, dic_elementsp)

    # dict with tranClosure of each element
    cU_TranClosure[e] = l_cU

    if e in l_cU:
      print('There are loops on elementCollectionUnordered of element', e)
      b_cU = False
  if b_cU == True:
    print('No loops found on elementCollectionUnordered.')



# Transitive closure of each element
def calcula_cU(element, struct) -> list:
    if element in struct:
      l = struct[element]
    else:
      return []
    for e in struct[element]:
      l = l + calcula_cU(e, struct)
    return l


# Get relations associated with element. Returns a list with every other element and his position, as well as the relation id.
def getRelations(element) -> list:

  l = [] # list with every trio.
  for relation in railw.netRelations:

    if (str(relation.elementA).strip() == str(element).strip()):
      l.append(('B', relation.elementB, relation.positionOnB, 'A', relation.elementA, relation.positionOnA, relation.id))

    if (str(relation.elementB).strip() == str(element).strip()):
      l.append(('A', relation.elementA, relation.positionOnA, 'B', relation.elementB, relation.positionOnB, relation.id))

  return l


# Verify property of elementOn.
def elementOn():

  b = True
  # get all elements.
  elements  = railw.netElements

  for e in elements:

    l_relations = getRelations(e.id)

    rel_ids = [(r[1],r[2],r[5]) for r in l_relations]

    # Split by position (0 or 1).

    # Now, I need to check whether the relation exits between the elements.
    for e_related in rel_ids:
      # Get id and position of the element related
      id_e  = e_related[0]
      pos_e = e_related[1]

      # Position of the e readed above must be preserved
      pos_outro = e_related[2]

      # Get elements related with the element e_related.
      r_aux = getRelations(id_e)
      r_aux = [(ee[1],ee[2]) for ee in r_aux]

      # Check if the elements on l_relations are related.
      r_removed = [(e_removed[0],e_removed[1]) for e_removed in rel_ids if e_removed[0] != id_e and e_removed[2] == pos_outro]
      if not set(r_removed).issubset(set(r_aux)):
        b = False
        print("FAILED HERE:",e_related, r_removed, r_aux)

  if b == False:
    print('ElementOn property failed.')
  else:
    print('ElementOn property verified.')



# netRelations injectivity within elements and netRelations musnt have equal elements at the same position.
def netRelations_assumptions():

  b  = True # injectivity
  b1 = True # repeated elements and positions

  # Get each element of each relation
  for r in railw.netRelations:
    tup = (r.elementA, r.elementB)

    if r.elementA == r.elementB and r.positionOnA == r.positionOnB:
      b1 = False

    r_removed = [e_removed for e_removed in railw.netRelations if e_removed != r]
    for rp in r_removed:
      tup1 = (rp.elementA, rp.elementB)
      tup2 = (rp.elementB, rp.elementA)

      if tup == tup1 or tup == tup2:
        b = False

  if b:
    print('Relations injectivity verified.')
  else:
    print('Relations injectivity NOT verified.')

  if b1:
    print('Relations with non repeated elements with same positions.')
  else:
    print('Theres at least one relation that has the same element in the same position.')


# Check if Micro Level extension is on Meso Level extension and so on
def extendNetwork_assumptions():
  check_meso  = True
  check_macro = True
  exist_meso  = False
  exist_macro = False

  # Get every network in the railway
  for netw in railw.networks:
    b  = True
    b1 = True
    micro = []
    meso  = []
    macro = []
    #Levels in a network
    for lvl in netw.levels:
      # Get every level if exists in the network.
      if lvl.description == "Micro":
        micro = lvl.networkResources
      if lvl.description == "Meso":
        meso = lvl.networkResources
        exist_meso  = True
      if lvl.description == "Macro":
        macro = lvl.networkResources
        exist_macro = True

    if not micro:
      print("ERROR: Micro level doesn't exist in the network", netw.id)
      return
    # Meso and Micro
    if meso:
      meso_list = []
      for m in meso:
        if m in cU_TranClosure: # check if a netElement
          meso_list =  meso_list + cU_TranClosure[m] + [m]

      if not set([e for e in micro if e in map(lambda x: x.id, railw.netElements)]).issubset(set(meso_list)):
        b = False
        check_meso = False
      if b == False:
        print("Not all elements at micro are in extended meso at the network", netw.id)

      # Macro and Meso and Micro
      if macro:
        macro_list = []
        for mM in macro:
          if mM in cU_TranClosure: # check if a netElement
            macro_list = macro_list + cU_TranClosure[mM] + [mM]

        if not set([e for e in meso if e in map(lambda x: x.id, railw.netElements)]).issubset(set(macro_list)):
          b1 = False
          check_macro = False
        if b1 == False:
          print("Not all elements at meso are in extended macro at the network", netw.id)

  if exist_meso:
    print("Micro in Meso extended, for each network -", str(check_meso) + ".")
  if exist_macro:
    print("Meso in Macro extended, for each network -", str(check_macro) + ".")
