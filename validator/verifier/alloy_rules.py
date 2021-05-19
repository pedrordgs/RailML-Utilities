from collections import Counter
from colorama import Fore, Back, Style
from verifier.xml_checker import p_print

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
  list_elements  = [(e,r) for e in railw.netElements for r in e.relations]
  list_relations = []
  for r in railw.netRelations:
    list_relations.append((r.elementA, r))
    list_relations.append((r.elementB, r))

  # Counters for each
  c_elements  = Counter(list_elements)
  c_relations = Counter(list_relations)

  err = ""
  if c_elements == c_relations:
    p_print('Relations are redudant.', True, err)
  else:
    if c_elements - c_relations:
      # There are some relations defined in elements, which do not correspond to the relation declaration.
      s = c_elements - c_relations
      for ((elem, rel),_) in s.items():
        err += f'\tLine {elem.line}: Element {elem.id} has as reference a not corresponding relation {rel.id}.\n'
    if c_relations - c_elements:
      # There are some relations defined where its elements don't make a reference to it.
      s = c_relations - c_elements
      for ((elem, rel),_) in s.items():
        err += f'\tLine {rel.line}: Relation {rel.id} has as reference a not corresponding element {elem.id}.\n'

    # Print errors
    p_print('Redudancy is not preserved.', False, err)

  # No loops in elementCollectionUnordered: Transitive Closure
  b = True
  err = ""

  for elm in railw.netElements:
    if elm in elm.transitive_ecu:
      err += f'\tLine {elm.line}: There are loops on elementCollectionUnordered of element {elm.id}.\n'
      b = False

  if b == True:
    p_print('No loops found on relation elementCollectionUnordered.', True, err)
  else:
    p_print('Loops found on relation elementCollectionUnordered.', False, err)


# Get relations associated with element. Returns a list with every other element and his position, as well as the relation id.
def getRelations(element) -> list:

  l = [] # list with every trio.
  for relation in railw.netRelations:

    if (relation.elementA == element):
      l.append(('B', relation.elementB, relation.positionOnB, 'A', relation.elementA, relation.positionOnA, relation.id, relation.line))

    if (relation.elementB == element):
      l.append(('A', relation.elementA, relation.positionOnA, 'B', relation.elementB, relation.positionOnB, relation.id, relation.line))

  return l


# Verify property of elementOn.
def elementOn():
  b   = True
  err = ''

  # get all elements.
  for e in railw.netElements:

    l_relations = getRelations(e.id)

    # Now, I need to check whether the relation exits between the elements.
    for e_related in l_relations:
      # Get id and position of the element related
      id_e  = e_related[1]
      pos_e = e_related[2]

      # Position of the e readed above must be preserved
      pos_readed = e_related[5]

      # Get elements related with the element e_related.
      r_aux = getRelations(id_e)
      r_aux = [(ee[1],ee[2]) for ee in r_aux]

      # Check if the elements on l_relations are related.
      r_removed = [(e_removed[1],e_removed[2]) for e_removed in l_relations if e_removed[1] != id_e and e_removed[5] == pos_outro]
      for e_r in l_relations:

        if e_r[1] != id_e and e_r[5] == pos_outro:
          if (e_r[1],e_r[2]) not in r_aux:
            b    = False
            err += f'\tElement {e_r[1].id}, declared at Line {e_r[1].line}, must have a relation with the element {id_e.id}, since they both connect to {e.id} at the same endpoint {pos_outro}.\n'

  if b == False:
    p_print('ElementOn property failed.', False, err)
  else:
    p_print('ElementOn property verified.', True, err)



# netRelations injectivity within elements and netRelations musnt have equal elements at the same position.
def netRelations_assumptions():

  b    = True # injectivity
  err  = ""
  b1   = True # repeated elements and positions
  err1 = ""

  # Auxiliar structs to find relations with the equal elements to others
  elems_relations = {}
  stored_tuples = []

  # Get each element of each relation
  for rel in railw.netRelations:
    tup     = (rel.elementA, rel.elementB)
    tup_rev = (rel.elementB, rel.elementA)

    # Store to each tuple (elementA, elementB) every corresponding relation
    if tup not in elems_relations:
      if tup_rev not in elems_relations:
        elems_relations[tup] = [rel]
      else:
        elems_relations[tup_rev].append(rel)
        stored_tuples.append(tup_rev)
        b = False
    else:
      eles_relations[tup].append(rel)
      stored_tuples.append(tup)
      b = False

    # Repeated elements with the same position
    if rel.elementA == rel.elementB and rel.positionOnA == rel.positionOnB:
      b1 = False
      err1 += f'\tLine {rel.line}: Relation {rel.id} has equal elements A and B → {rel.elementA.id}, defined in position {rel.positionOnA}.\n'

  if b:
    p_print('Relations elements injectivity verified.', True, err)
  else:
    for (ea,eb) in stored_tuples:
      err += f'\tRelations that represent the relation between these elements → {ea.id}, {eb.id}:\n'
      for rel_ in elems_relations[(ea,eb)]:
        err += f'\t  - Relation {rel_.id} declared in line {rel_.line}.\n'

    p_print('Relations elements injectivity NOT verified.', False, err)

  if b1:
    p_print('Relations with non repeated elements with same positions.', True, err1)
  else:
    p_print('Theres at least one relation that has equal elements A and B defined in the same position.', False, err1)


# Check if Micro Level extension is on Meso Level extension and so on
def extendNetwork_assumptions():

  # Bools in order to check every extended level property
  check_meso  = True
  check_macro = True
  # check if exists levels above micro - if micro doesnt exist a error must be outputed
  exist_meso  = False
  exist_macro = False

  # network with associated strings -> Print to user purposes
  dic_netw_str = {}

  # Get every network in the railway
  for netw in railw.networks:
    # bools for each network
    b  = True
    b1 = True
    micro = []
    meso  = []
    macro = []

    # String with valid networks
    correct = ''
    err_meso = ''
    err_micro_macro = ''
    err_meso_macro = ''

    #Levels in a network
    for lvl in netw.levels:
      # Get every level if exists in the network.
      if lvl.description == "Micro":
        micro = lvl
      if lvl.description == "Meso":
        meso = lvl
        exist_meso  = True
      if lvl.description == "Macro":
        macro = lvl
        exist_macro = True

    # Can't check anything further if micro isnt defined at a network
    if not micro:
      p_print(f'ERROR: Micro level does not exist in the network {netw.id}.', False, "\t- You must guarantee the existence of Micro level at every network before checking the remaining.")
      return

    # Check if Meso Level is declared
    if meso:
      err = ''
      meso_list = []

      # Creates the extended meso elements
      for m in meso.networkResources:
        if m.__class__.__name__ == "NetElement": # check if a netElement
          meso_list =  meso_list + m.transitive_ecu + [m]

      for e_micro in micro.networkResources:
        if e_micro.__class__.__name__ == "NetElement":
          if e_micro not in meso_list:
            err += f'\t  - Line {micro.line}: Element {e_micro.id} at Micro level must be at the extended Meso Level, declared in Line {meso.line}.\n'
            b = False
            check_meso = False
      if b == False:
        err_meso = f'\tNot all elements at Micro are in the extended Meso, at the network {netw.id}:\n'
        err_meso += err
      else:
        correct += f'\tThe network {netw.id} has every Micro element in the extended Meso Level.\n'

      # Check if Macro Level is declared
      if macro:
        # reset temp variables
        b = True
        err = ''
        macro_list = []

        # Creates the extended macro elements
        for mM in macro:
          if mM.__class__.__name__ == "NetElement": # check if a netElement
            macro_list = macro_list + mM.transitive_ecu + [mM]

        for e_micro in micro.networkResources:
          if e_micro.__class__.__name__ == "NetElement":
            if e_micro not in macro_list:
              err += f'\t  - Line {micro.line}: Element {e_micro.id} at Micro level must be at the extended Macro Level, declared in Line {macro.line}.\n'
              b = False
              check_macro = False
        if b == False:
          err_micro_macro = f'\tNot all elements at Micro are in the extended Macro, at the network {netw.id}:\n'
          err_micro_macro += err
        else:
          correct += f'\tThe network {netw.id} has every Micro element in the extended Macro Level.\n'

        if meso:
          err = '' # reset error string again.
          for e_meso in meso.networkResources:
            if e_meso.__class__.__name__ == "NetElement":
              if e_meso not in macro_list:
                err += f'\t  - Line {meso.line}: Element {e_meso.id} at Meso level must be at the extended Macro Level, declared in Line {macro.line}.\n'
                b1 = False
                check_macro = False
          if b1 == False:
            err_meso_macro = f'\tNot all elements at Meso are in the extended Macro, at the network {netw.id}:\n'
            err_meso_macro += err
          else:
            correct += f'\tThe network {netw.id} has every Meso element in the extended Macro Level.\n'

      dic_netw_str[netw] = (err_meso, err_micro_macro, err_meso_macro, correct)


  # Prints to the user - Error treatment
  if check_macro and check_meso:
    p_print('Every network respects the extended property.', True, 'ignore_net')
    for nt in dic_netw_str:
      (e1,e2,e3,c) = dic_netw_str[nt]
      print(f'  For the network {nt.id}:')
      print(c, end='')
  else:
    p_print('Not every network respects the extended property.', False, 'ignore_net')
    for nt in dic_netw_str:
      (e1,e2,e3,c) = dic_netw_str[nt]
      print(f'  For the network {nt.id}:')
      print(c, end='')
      if (e1):
        print(e1, end='')
      if (e2):
        print(e2, end='')
      if (e3):
        print(e3, end='')
