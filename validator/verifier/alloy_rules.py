from collections import Counter
from colorama import Fore, Back, Style
from verifier.xml_checker import p_print
import networkx as nx

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

  # No loops in elementCollectionUnordered: Transitive Closure
  b = True
  err_tr = ""

  # Pair netElement with each netRelation
  list_elements  = []
  for e in railw.netElements:

    # Pair netElement with each netRelation
    for r in e.relations:
      list_elements.append((e,r))

    # Check if there's loops at every netElement
    if e in e.transitive_ecu:
      err_tr += f'\tLine {e.line}: Loops found on elementCollectionUnordered of the NetElement {e.id}.\n'
      b = False


    '''
    # If collectionUnordered could be a connected graph.
    G = nx.Graph()
    for elm_p in e.elementCollectionUnordered:
      G.add_node(elm_p)
      # Get their relations
      for rel_p in elm_p.relations:
        if rel_p.elementA == elm_p:
          if rel_p.elementB in e.elementCollectionUnordered:
            G.add_edge(elm_p, rel_p.elementB)
        elif rel_p.elementB == elm_p:
          if rel_p.elementA in e.elementCollectionUnordered:
            G.add_edge(elm_p, rel_p.elementA)

    # Check if its connected
    '''

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

  # Treatment of errors - loops on relation elemenetCollectionUnordered
  if b == True:
    p_print('No loops found on relation elementCollectionUnordered.', True, err_tr)
  else:
    p_print('Loops found on relation elementCollectionUnordered.', False, err_tr)


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
    p_print('Element On property failed.', False, err)
  else:
    p_print('Element On property verified.', True, err)



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
        stored_tuples.append(tup)
      else:
        elems_relations[tup_rev].append(rel)
        b = False
    else:
      elems_relations[tup].append(rel)
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
  check_micro = True
  check_meso  = True
  check_macro = True
  # check if exists levels above micro - if micro doesnt exist a error must be outputed
  exist_meso  = False
  exist_macro = False

  # network with associated strings -> Print to user purposes
  dic_netw_str = {}

  # Get every network in the railway
  for netw in railw.networks:

    micro = []
    meso  = []
    macro = []

    # String with valid networks
    correct = ''

    # Error and bools for controlling that every level must be extended at the higher levels
    # bools for each network
    b  = True
    b1 = True
    # Error strings
    err_meso = ''
    err_micro_macro = ''
    err_meso_macro = ''
    err_macro = ''


    # Error Strings: Elements and Relations must be within one level only.
    err_elements_micro  = ''
    err_elements_meso   = ''
    err_elements_macro  = ''
    err_relations_micro = ''
    err_relations_meso  = ''
    err_relations_macro = ''

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
      inp = input("\tDo you want to proceed without the implemention of the Micro Level? [y/N] ")
      if inp == "N" or inp == "n" or inp == "":
        return
    # Check every relation if they have corresponding elements at the same level.
    else:

      # Relations errors
      relations_micro = True
      err_rmicro = ''
      # Elements erros
      elements_micro = True
      err_emicro = ''

      for m in micro.networkResources:
        # If its a netElement
        if m.__class__.__name__ == "NetElement":
          # Check if it has collection unordered
          if m.elementCollectionUnordered:
            elements_micro = False
            err_emicro += f'\t  - Line {micro.line}: Element {m.id}, defined at Line {m.line}, is extended by some elements and should not, since it belongs to Micro level.\n'

        # If its a netRelation
        if m.__class__.__name__ == "NetRelation":
          if m.elementA not in micro.networkResources:
            relations_micro = False
            err_rmicro += f'\t  - Line {m.line}: The element {m.elementA.id}, in this relation {m.id}, does not correspond to this network level (Micro).\n'
          if m.elementB not in micro.networkResources:
            relations_micro = False
            err_rmicro += f'\t  - Line {m.line}: The element {m.elementB.id}, in this relation {m.id}, does not correspond to this network level (Micro).\n'

      if relations_micro == False:
        check_micro = False
        err_relations_micro = f'\tThere are some relations at the Micro Level that have elements defined in a different level.\n'
        err_relations_micro += err_rmicro
      else:
        correct += f'\tEvery relation defined in Micro has valid level elements.\n'

      if elements_micro == False:
        check_micro = False
        err_elements_micro = f'\tMicro elements can not be composed by other elements, meaning that elementCollectionUnordered must be empty.\n'
        err_elements_micro += err_emicro
      else:
        correct += f'\tEvery element defined in Micro does not compose in different elements.\n'

    # Check if Meso Level is declared
    if meso:
      err = ''
      meso_list = []

      relations_meso = True
      err_rmeso  = ''
      # Creates the extended meso elements
      for m in meso.networkResources:
        if m.__class__.__name__ == "NetElement": # check if a netElement
          meso_list =  meso_list + m.transitive_ecu # + [m]
        if m.__class__.__name__ == "NetRelation":
          if m.elementA not in meso.networkResources:
            relations_meso = False
            err_rmeso += f'\t  - Line {m.line}: The element {m.elementA.id}, in this relation {m.id}, does not correspond to this network level (Meso).\n'
          if m.elementB not in meso.networkResources:
            relations_meso = False
            err_rmeso += f'\t  - Line {m.line}: The element {m.elementB.id}, in this relation {m.id}, does not correspond to this network level (Meso).\n'

      if relations_meso == False:
        check_meso = False
        err_relations_meso = f'\tThere are some relations at the Meso Level that have elements defined in a different level.\n'
        err_relations_meso += err_rmeso
      else:
        correct += f'\tEvery relation defined in Meso has valid level elements.\n'

      # If Micro Level exists
      if micro:

        # Check if every micro is at the extended meso
        for e_micro in micro.networkResources:
          if e_micro.__class__.__name__ == "NetElement":
            if e_micro not in meso_list and e_micro not in meso.networkResources:
              err += f'\t  - Line {micro.line}: Element {e_micro.id} at Micro level must be at the extended Meso Level, declared in Line {meso.line}.\n'
              b = False
              check_meso = False

        # Check if extendend meso is in micro resource
        for extended_meso in meso_list:
          if extended_meso not in micro.networkResources:
              err += f'\t  - Line {meso.line}: Element {extended_meso.id} defined as extended must be defined at the Micro Level, defined in Line {micro.line}.\n'
              b = False
              check_meso = False
          if macro:
            if extended_meso in macro.networkResources:
              err += f'\t  - Line {meso.line}: Element {extended_meso.id} defined as extended must be defined at the Micro Level, defined in Line {micro.line}, and can not be defined at the Macro Level, Line {macro.line}, as it is.\n'
              b = False
              check_meso = False

        if b == False:
          err_meso = f'\tNot all elements respect the rule of extending Meso, at the network {netw.id}:\n'
          err_meso += err
        else:
          correct += f'\tThe network {netw.id} respects the rule of extending Meso, meaning that the elements at Micro are the same as the elements at the extended Meso Level.\n'

      # Check if Macro Level is declared
      if macro:
        # reset temp variables
        b = True
        err = ''
        macro_list = []

        macro_extended_elements = True

        # Relations
        relations_macro = True
        err_rmacro  = ''

        # Creates the extended macro elements
        for mM in macro.networkResources:
          if mM.__class__.__name__ == "NetElement": # check if a netElement
            macro_list = macro_list + mM.transitive_ecu # + [mM]

            # Check if the extension of every element at macro must not be declared in macro!
            for m_transitive in mM.transitive_ecu:
              if m_transitive in macro.networkResources:
                macro_extended_elements = False
                err += f'\t  - Line {macro.line}: The element {m_transitive.id} extended by element {mM.id} can not be defined at the Macro Level, as it is.\n'

          if mM.__class__.__name__ == "NetRelation":
            if mM.elementA not in macro.networkResources:
              relations_macro = False
              err_rmacro += f'\t  - Line {mM.line}: The element {mM.elementA.id}, in this relation {mM.id}, does not correspond to this network level (Macro).\n'
            if mM.elementB not in macro.networkResources:
              relations_macro = False
              err_rmacro += f'\t  - Line {mM.line}: The element {mM.elementB.id}, in this relation {mM.id}, does not correspond to this network level (Macro).\n'

        # Check if elements extended at this level is defined at this level
        if macro_extended_elements == False:
          check_macro = False
          err_macro = f'\tThere are some elements defined at Macro Level that extend elements that are also defined at Macro Level:\n'
          err_macro += err
        else:
          correct += f'\tEvery element extended at the Macro level are either defined at the Meso Level or the Micro Level.\n'

        # Check if relations at Macro were respected
        if relations_macro == False:
          check_macro = False
          err_relations_macro = f'\tThere are some relations at the Macro Level that have elements defined in a different level:\n'
          err_relations_macro += err_rmacro
        else:
          correct += f'\tEvery relation defined in Macro has valid level elements.\n'

        # If Micro Level exists
        if micro:
          err = '' # reset error string.
          for e_micro in micro.networkResources:
            if e_micro.__class__.__name__ == "NetElement":
              if e_micro not in macro_list and e_micro not in macro.networkResources:
                err += f'\t  - Line {micro.line}: Element {e_micro.id} at Micro level must be at the extended Macro Level, declared in Line {macro.line}.\n'
                b = False
                check_macro = False
          if b == False:
            err_micro_macro = f'\tNot all elements at Micro are in the extended Macro, at the network {netw.id}:\n'
            err_micro_macro += err
          else:
            correct += f'\tThe network {netw.id} has every Micro element in the extended Macro Level.\n'

        # If Meso Level exists
        if meso:
          err = '' # reset error string again.
          for e_meso in meso.networkResources:
            if e_meso.__class__.__name__ == "NetElement":
              if e_meso not in macro_list and e_meso not in macro.networkResources:
                err += f'\t  - Line {meso.line}: Element {e_meso.id} at Meso level must be at the extended Macro Level, declared in Line {macro.line}.\n'
                b1 = False
                check_macro = False
          if b1 == False:
            err_meso_macro = f'\tNot all elements at Meso are in the extended Macro, at the network {netw.id}:\n'
            err_meso_macro += err
          else:
            correct += f'\tThe network {netw.id} has every Meso element in the extended Macro Level.\n'

      err_elements  = err_elements_micro + err_elements_meso + err_elements_macro
      err_relations = err_relations_micro + err_relations_meso + err_relations_macro
      dic_netw_str[netw] = (err_elements, err_relations, err_meso, err_macro, err_micro_macro, err_meso_macro, correct)


  # Prints to the user - Error treatment
  if check_micro and check_macro and check_meso:
    p_print('Every network respects the extended property.', True, 'ignore_net')
    for nt in dic_netw_str:
      (e1,e2,e3,e4,e5,e6,c) = dic_netw_str[nt]
      print(f'  For the network {nt.id} defined at Line {nt.line}:')
      print(Fore.GREEN + '\n\tVerified properties:')
      print(Style.RESET_ALL, end='')
      print(c, end='')
  else:
    p_print('Not every network respects the extended property.', False, 'ignore_net')
    for nt in dic_netw_str:
      (e1,e2,e3,e4,e5,e6,c) = dic_netw_str[nt]
      print(f'  For the network {nt.id} defined at Line {nt.line}:')
      print(Fore.GREEN + '\n\tVerified properties:')
      print(Style.RESET_ALL, end='')
      print(c, end='')
      if(e1 or e2 or e3 or e4 or e5 or e6):
        print(Fore.RED + '\n\tErrors found:')
        print(Style.RESET_ALL, end='')
      if (e1):
        print(e1, end='')
      if (e2):
        print(e2, end='')
      if (e3):
        print(e3, end='')
      if (e4):
        print(e4, end='')
      if (e5):
        print(e5, end='')
      if (e6):
        print(e6, end='')