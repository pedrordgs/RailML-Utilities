from collections import Counter
from colorama import Fore, Back, Style
from verifier.xml_checker import p_print
from datetime import datetime
import math
import networkx as nx

# Main function that will call every property verification.
def assumptions_(r):

  global railw
  railw = r

  print("\n\033[4mChecking Topology properties:\033[0m")

  # Needs to be rethought - not that simple to implement
  if railw.linear != [] or railw.geometric != []:
    print("\n \x1B[3mPositioning System Assumptions:\x1B[23m\n")
    positionSystem_assumptions()
  else:
    print("\n \x1B[3mNo Positioning System declared.\x1B[23m")

  # netElements assumptions - Redudancy and elementCollectionUnordered
  print("\n \x1B[3mNetElement Assumptions:\x1B[23m\n")
  netElements_assumptions()
  # If a NetElement is connected to two different NetElements in same endpoint, those must also be connected
  elementOn()

  # netRelations assumptions
  print("\n \x1B[3mNetRelation Assumptions:\x1B[23m\n")
  netRelations_assumptions()

  # extendNetworks properties - extend Micro should be on extend Meso and so on
  print("\n \x1B[3mNetwork Assumptions:\x1B[23m\n")
  extendNetwork_assumptions()


def positionSystem_assumptions():

  # Inorder to check if isValid
  today = datetime.today()
  today = today.strftime("%Y-%m-%d")


  # GEOMETRIC POSITION SYSTEM
  if not railw.geometric == []:
    atleast1 = False
    fill = False
    fill_rel = False
    # Should be reseted in linear
    b_length = True
    err_length = ''
    valid_time = True
    err_time = ''
    non_empty = True
    err_empty = ''
    b_cU = True
    err_cU = ''
    relation_con = True
    err_rel_con = ''
    warning = False
    warning_str = ''
    print('  • \x1B[3mGeometric\'s System Assumptions:\x1B[23m\n')
    # Process every Geometric Positioning System
    for g in railw.geometric:

      if not datetime.strptime(g.valid_from, "%Y-%m-%d") <= datetime.strptime(today, "%Y-%m-%d") <= datetime.strptime(g.valid_to, "%Y-%m-%d"):
        valid_time = False
        err_time += f'\tLine {g.line}: The positioning system {g.id} is currently time invalid.\n'

      if not len(g.elements) == 0:
        fill = True
        for elem in g.elements:
          # check if element respects the element length property
          length = elem.length

          if 'start' in elem.geometric[g.id]:
            s = elem.geometric[g.id]['start'][0]
            if 'end' in elem.geometric[g.id]:
              e = elem.geometric[g.id]['end'][0]
            else:
              # If there is more than 1 in start
              if len(elem.geometric[g.id]['start']) == 2:
                e = elem.geometric[g.id]['start'][1]
                elem.geometric[g.id]['end'] = [e]
              else:
                warning = True
                warning_str += f'\tLine {elem.line}: Not possible to determine the distance in the system {g.id}, since this element does not provide information about intrinsic coordinate 1.\n'
                continue
          else:
            warning = True
            warning_str += f'\tLine {elem.line}: Not possible to determine the distance in the system {g.id}, since this element does not provide information about intrinsic coordinate 0.\n'
            continue

          # Determine the distance
          d = math.sqrt(((float(s[1])-float(e[1]))**2)+((float(s[2])-float(e[2]))**2))
          if (float(s[1]), float(s[2])) <= (float(e[1]), float(e[2])):
            max_ = (float(e[1]), float(e[2]))
            min_ = (float(s[1]), float(s[2]))
          else:
            max_ = (float(s[1]), float(s[2]))
            min_ = (float(e[1]), float(e[2]))

          # check elemententCollectionUnordered
          if not elem.elementCollectionUnordered == []:
            # list of measures of every element collection unordered
            list_measures = []
            for ecu in elem.elementCollectionUnordered:
              if g.id not in ecu.linear:
                warning = True
                warning_str += f'\tLine {elem.line}: Not possible to determine the combine distances of the element {elem.id}\'s elementCollectionUnordered, since element {ecu.id} is not defined in the system {g.id}.\n'
                break

              if 'start' in ecu.geometric[g.id]:
                ss = ecu.geometric[g.id]['start'][0]
                if 'end' in elem.geometric[g.id]:
                  ee = ecu.geometric[g.id]['end'][0]
                else:
                  # If there is more than 1 in start
                  if len(ecu.geometric[g.id]['start']) == 2:
                    ee = ecu.geometric[g.id]['start'][1]
                    ecu.geometric[g.id]['end'] = [ee]
                  else:
                    warning = True
                    warning_str += f'\tLine {elem.line}: Not possible to determine the combine distances of the element {elem.id}\'s elementCollectionUnordered, since element {ecu.id} does not provide information about intrinsic coordinate 1 in the system {g.id}.\n'
                    break
              else:
                warning = True
                warning_str += f'\tLine {elem.line}: Not possible to determine the combine distances of the element {elem.id}\'s elementCollectionUnordered, since element {ecu.id} does not provide information about intrinsic coordinate 0 in the system {g.id}.\n'
                break

              list_measures.append((float(ee[1]),float(ee[2])))
              list_measures.append((float(ss[1]),float(ss[2])))

            if len(list_measures) == 2*(elem.elementCollectionUnordered):
              atleast1 = True
              mM = max(list_measures)
              mm = min(list_measures)
              if not float(d) == float(mM - mm):
                err_cU += f'\tLine {elem.line}: Element {elem.id} does not preserve the elementCollectionUnordered preservation property, where its defined between {min_} and {max_}, where the measure values of its parts are between {mm} and {mM}, in the system {g.id}\n.'
                b_cU = False


          if not length is None:
            if not float(length) == float(d):
              err_length += f'\tLine {elem.line}: Element {elem.id} does not preserve the length property, where length has value of {length}, and the difference between coordinates related to the system {g.id} has value {d}.\n'
              b_length = False
      else:
        non_empty = False
        err_empty += f'\tLine {g.line}: The positioning system {g.id} is declared but has no associated element.\n'

      # Relations properties
      for rel in g.relations:
        fill_rel = True

        elA = rel.elementA
        elB = rel.elementB

        # For element A
        if 'start' in elA.geometric[g.id]:
          sA = elA.geometric[g.id]['start'][0]
          sA = (float(sA[1]),float(sA[2]))

          if 'end' in elA.geometric[g.id]:
            eA = elA.geometric[g.id]['end'][0]
            eA = (float(eA[1]),float(eA[2]))
          else:
              # If there is more than 1 in start
              if len(elA.geometric[g.id]['start']) == 2:
                eA = elA.geometric[g.id]['start'][1]
                elA.geometric[g.id]['end'] = [eA]
                eA = (float(eA[1]),float(eA[2]))
              else:
                warning = True
                warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {g.id}, since the elementA of this relation {elA.id} does not provide information about intrinsic coordinate 1.\n'
                continue
        else:
          warning = True
          warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {g.id}, since the elementA of this relation {elA.id} does not provide information about intrinsic coordinate 0.\n'
          continue

        # For element B
        if 'start' in elB.geometric[g.id]:
          sB = elB.geometric[g.id]['start'][0]
          sB = (float(sB[1]),float(sB[2]))
          if 'end' in elB.geometric[g.id]:
            eB = elB.geometric[g.id]['end'][0]
            eB = (float(eB[1]),float(eB[2]))
          else:
              # If there is more than 1 in start
              if len(elB.geometric[g.id]['start']) == 2:
                eB = elB.geometric[g.id]['start'][1]
                elB.geometric[g.id]['end'] = [eB]
                eB = (float(eB[1]),float(eB[2]))
              else:
                warning = True
                warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {g.id}, since the elementB of this relation {elB.id} does not provide information about intrinsic coordinate 1.\n'
                continue
        else:
          warning = True
          warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {g.id}, since the elementB of this relation {elB.id} does not provide information about intrinsic coordinate 0.\n'
          continue

        if not (sA == sB or eA == sB or sA == eB or eA == eB):
          relation_con = False
          err_rel_con += f'\tLine {rel.line}: Relation {rel.id} does not preserve the connectivity property, meaning that its elements are not connected in the system {g.id}.\n'



    ### Output Treatment ###
    # Print warnings
    if warning == True:
      if fill:
        print(Fore.YELLOW + "   Warnings:\n" + Style.RESET_ALL + warning_str, end='')

    # Time valid
    if valid_time == True:
      p_print('Every GPS is, until this day, time valid.', True, err_time)
    else:
      p_print('Not every GPS is time valid.', False, err_time)

    # Empty warning
    if non_empty == True:
      p_print('Every GPS declared has associated elements.', True, err_empty)
    else:
      p_print('There are some GPS declared with no associated element.', False, err_empty)

    # Length property
    if b_length == True:
      if fill:
        p_print('Every element respects the length property.', True, err_length)
    else:
      if fill:
        p_print('Elements found that disrespect the length property.', False, err_length)

    # elementCollectionUnordered property
    if b_cU == True:
      if atleast1:
        p_print('Every element respects the preservation of the coordinates on elementCollectionUnordered.', True, err_cU)
    else:
        p_print('Elements found that disrespect the preservation of the coordinates on elementCollectionUnordered.', False, err_cU)

    # relation conectivity property
    if relation_con == True:
      if fill_rel:
        p_print('Every relation respects the connectivity of their elements.', True, err_rel_con)
    else:
      p_print('Relations found that disrespect the connectivity property.', False, err_rel_con)


  # LINEAR POSITION SYSTEM
  if not railw.linear == []:
    fill = False
    fill_rel = False
    atleast1 = False
    # Reseted after geometric
    b_length = True
    err_length = ''
    valid_time = True
    err_time = ''
    non_empty = True
    err_empty = ''
    b_cU = True
    err_cU = ''
    relation_con = True
    err_rel_con = ''
    warning = False
    warning_str = ''
    print('\n  • \x1B[3mLinear\'s System Assumptions:\x1B[23m\n')
    # Process every Linear Positioning System
    for l in railw.linear:

      if not datetime.strptime(l.valid_from, "%Y-%m-%d") <= datetime.strptime(today, "%Y-%m-%d") <= datetime.strptime(l.valid_to, "%Y-%m-%d"):
        valid_time = False
        err_time += f'\tLine {l.line}: The positioning system {l.id} is currently time invalid.\n'

      if not len(l.elements) == 0:
        fill = True
        for elem in l.elements:
          # check if element respects the element length property
          length = elem.length

          if 'start' in elem.linear[l.id]:
            s = elem.linear[l.id]['start'][0]
            if 'end' in elem.linear[l.id]:
              e = elem.linear[l.id]['end'][0]
            else:
              # If there is more than 1 in start
              if len(elem.linear[l.id]['start']) == 2:
                e = elem.linear[l.id]['start'][1]
                elem.linear[l.id]['end'] = [e]
              else:
                warning = True
                warning_str += f'\tLine {elem.line}: Not possible to determine the distance in the system {l.id}, since this element does not provide information about intrinsic coordinate 1.\n'
                continue
          else:
            warning = True
            warning_str += f'\tLine {elem.line}: Not possible to determine the distance in the system {l.id}, since this element does not provide information about intrinsic coordinate 0.\n'
            continue

          # Determine the distance
          d = abs(float(e[1]) - float(s[1]))
          if float(e[1]) >= float(s[1]):
            max_ = float(e[1])
            min_ = float(s[1])
          else:
            max_ = float(s[1])
            min_ = float(e[1])

          # check elemententCollectionUnordered
          if not elem.elementCollectionUnordered == []:
            # list of measures of every element collection unordered
            list_measures = []
            for ecu in elem.elementCollectionUnordered:
              if l.id not in ecu.linear:
                warning = True
                warning_str += f'\tLine {elem.line}: Not possible to determine the combine distances of the element {elem.id}\'s elementCollectionUnordered, since element {ecu.id} is not defined in the system {l.id}.\n'
                break

              if 'start' in ecu.linear[l.id]:
                ss = ecu.linear[l.id]['start'][0]
                if 'end' in elem.linear[l.id]:
                  ee = ecu.linear[l.id]['end'][0]
                else:
                  # If there is more than 1 in start
                  if len(ecu.linear[l.id]['start']) == 2:
                    ee = ecu.linear[l.id]['start'][1]
                    ecu.linear[l.id]['end'] = [ee]
                  else:
                    warning = True
                    warning_str += f'\tLine {elem.line}: Not possible to determine the combine distances of the element {elem.id}\'s elementCollectionUnordered, since element {ecu.id} does not provide information about intrinsic coordinate 1 in the system {l.id}.\n'
                    break
              else:
                warning = True
                warning_str += f'\tLine {elem.line}: Not possible to determine the combine distances of the element {elem.id}\'s elementCollectionUnordered, since element {ecu.id} does not provide information about intrinsic coordinate 0 in the system {l.id}.\n'
                break

              list_measures.append(float(ee[1]))
              list_measures.append(float(ss[1]))

            if len(list_measures) == 2*len(elem.elementCollectionUnordered):
              atleast1 = True
              mM = max(list_measures)
              mm = min(list_measures)
              if mM != max_ or mm != min_:
                err_cU += f'\tLine {elem.line}: Element {elem.id} does not preserve the elementCollectionUnordered preservation property, where its defined between {min_} and {max_}, where the measure values of its parts are between {mm} and {mM}, in the system {l.id}.\n'
                b_cU = False

          # out of elementCollectionUnordered cycle
          if not length is None:
            if not float(length) == float(d):
              err_length += f'\tLine {elem.line}: Element {elem.id} does not preserve the length property, where length has value of {length}, and the difference between measures related to the system {l.id} has value {d}.\n'
              b_length = False
      else:
        non_empty = False
        err_empty += f'\tLine {l.line}: The positioning system {l.id} is declared but has no associated element.\n'


      # Relations properties
      for rel in l.relations:
        fill_rel = True

        elA = rel.elementA
        elB = rel.elementB

        # For element A
        if 'start' in elA.linear[l.id]:
          sA = elA.linear[l.id]['start'][0]
          sA = float(sA[1])

          if 'end' in elA.linear[l.id]:
            eA = elA.linear[l.id]['end'][0]
            eA = float(eA[1])
          else:
              # If there is more than 1 in start
              if len(elA.linear[l.id]['start']) == 2:
                eA = elA.linear[l.id]['start'][1]
                elA.linear[l.id]['end'] = [eA]
                eA = float(eA[1])
              else:
                warning = True
                warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {l.id}, since the elementA of this relation {elA.id} does not provide information about intrinsic coordinate 1.\n'
                continue
        else:
          warning = True
          warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {l.id}, since the elementA of this relation {elA.id} does not provide information about intrinsic coordinate 0.\n'
          continue

        # For element B
        if 'start' in elB.linear[l.id]:
          sB = elB.linear[l.id]['start'][0]
          sB = float(sB[1])
          if 'end' in elB.linear[l.id]:
            eB = elB.linear[l.id]['end'][0]
            eB = float(eB[1])
          else:
              # If there is more than 1 in start
              if len(elB.linear[l.id]['start']) == 2:
                eB = elB.linear[l.id]['start'][1]
                elB.linear[l.id]['end'] = [eB]
                eB = float(eB[1])
              else:
                warning = True
                warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {l.id}, since the elementB of this relation {elB.id} does not provide information about intrinsic coordinate 1.\n'
                continue
        else:
          warning = True
          warning_str += f'\tLine {rel.line}: Not possible to verify the connection in the relation {rel.id} in the system {l.id}, since the elementB of this relation {elB.id} does not provide information about intrinsic coordinate 0.\n'
          continue

        if not (sA == sB or eA == sB or sA == eB or eA == eB):
          relation_con = False
          err_rel_con += f'\tLine {rel.line}: Relation {rel.id} does not preserve the connectivity property, meaning that its elements are not connected in the system {l.id}.\n'


    ### Output Treatment ###
    # Print warnings
    if warning == True:
      if fill:
        print(Fore.YELLOW + "   Warnings:\n" + Style.RESET_ALL + warning_str, end='')

    # Time valid
    if valid_time == True:
      p_print('Every LPS is, until this day, time valid.', True, err_time)
    else:
      p_print('Not every LPS is time valid.', False, err_time)

    # Empty warning
    if non_empty == True:
      p_print('Every LPS declared has associated elements.', True, err_empty)
    else:
      p_print('There are some LPS declared with no associated element.', False, err_empty)

    # Length property
    if b_length == True:
      if fill:
        p_print('Every element respects the length property.', True, err_length)
    else:
      if fill:
        p_print('Elements found that disrespect the length property.', False, err_length)

    # elementCollectionUnordered property
    if b_cU == True:
      if atleast1:
        p_print('Every element respects the preservation of the measures on elementCollectionUnordered.', True, err_cU)
    else:
      if atleast1:
        p_print('Elements found that disrespect the preservation of the measures on elementCollectionUnordered.', False, err_cU)

    # relation conectivity property
    if relation_con == True:
      if fill_rel:
        p_print('Every relation respects the connectivity of their elements.', True, err_rel_con)
    else:
      p_print('Relations found that disrespect the connectivity property.', False, err_rel_con)




# Redundacy with netRelations and no loops on elementCollectionUnordered
def netElements_assumptions():

  # No loops in elementCollectionUnordered: Transitive Closure
  b = True
  err_tr = ""

  b_network = True
  err_network = ""

  b_level = True
  err_level = ""

  b_parent = True
  err_parent = ""
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

    # Check if every element is defined at most one network
    if len(e.networks) != 1:
      err_network += f'\tLine {e.line}: The element {e.id} has {len(e.networks)} networks associated: {[n.id for n in list(e.networks)]}, where must have just 1 associated network.\n'
      b_network = False

    # Check if every element is defined at one level
    if len(e.levels) != 1:
      err_level += f'\tLine {e.line}: The element {e.id} is defined at {len(e.levels)} levels, but it can only be defined at 1 level.\n'
      b_level = False

    # Check if every element has only one parent
    if len(e.parents) > 1:
      err_parent += f'\tLine {e.line}: The element {e.id} has {len(e.parents)} associated parents, but it can have at most 1.\n'
      b_parent = False

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
    if r.elementA == r.elementB:
        list_relations.append((r.elementA, r))
    else:
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

  if b_parent == True:
    p_print('Every defined element has at most 1 parent.', True, err_parent)
  else:
    p_print('Elements found that disrespect the element-parent property.', False, err_parent)

  if b_network == True:
    p_print('Every defined element has 1 network associated.', True, err_network)
  else:
    p_print('Elements found that disrespect the network associated property.', False, err_network)

  if b_level == True:
    p_print('Every defined element is defined at only 1 level.', True, err_level)
  else:
    p_print('Elements found that disrespect the associated level property.', False, err_level)

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

    l_relations = getRelations(e)

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
      r_removed = [(e_removed[1],e_removed[2]) for e_removed in l_relations if e_removed[1] != id_e and e_removed[5] == pos_readed]
      for e_r in l_relations:

        if e_r[1] != id_e and e_r[5] == pos_readed:
          if (e_r[1],e_r[2]) not in r_aux:
            b    = False
            err += f'\tLine {e_r[1].line}: Element {e_r[1].id} must have a relation with the element {id_e.id}, since they both connect to {e.id} at the same endpoint {pos_readed}.\n'

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
  b_network = True
  err_network = ""
  b_level = True
  err_level = ""

  b_associated = True
  b_navigability = True
  control_1 = False
  control_2 = False
  err_associated = ''
  err_nav = ''

  # Auxiliar structs to find relations with the equal elements to others
  elems_relations = {}
  stored_tuples = []

  # Get each element of each relation
  for rel in railw.netRelations:
    tup     = (rel.elementA, rel.elementB)
    tup_rev = (rel.elementB, rel.elementA)

    # Check if every relation is defined at one network
    if len(rel.networks) != 1:
      err_network += f'\tLine {rel.line}: The relation {rel.id} has {len(rel.networks)} networks associated: {[n.id for n in list(rel.networks)]}, where must have just 1 associated network.\n'
      b_network = False

    # Check if every relation is defined at one level
    if len(rel.levels) != 1:
      err_level += f'\tLine {rel.line}: The relation {rel.id} is defined at {len(rel.levels)} levels, but it can only be defined at 1 level.\n'
      b_level = False

    if len(rel.levels) == 1:
      # Check associated property - Can only be defined at micro
      if len(rel.associated) < 6 and len(rel.associated) != 4 and len(rel.associated) != 3 and list(rel.levels)[0] == "Micro":

        if len(rel.associated) == 2:
          # It's a switch
          control_1 = True
          count = 0
          if rel.navigability == 'None':
            count += 1
          for r in rel.associated:
            if "Micro" not in list(r.levels):
              b_associated = False
              err_associated += f'\tLine {r.line}: The relations {rel.id} and {r.id} can not be associated, because {r.id} does not belong to the Micro level.\n'
              b_navigability = False
              err_navigability += f'\tLine {r.line}: The relations {rel.id} and {r.id} can not be associated, and therefore the navigability property can not be proved because {r.id} does not belong to the Micro level.\n'

            if r.navigability == 'None':
              count += 1

          if count != 1:
            b_navigability = False
            err_nav += f'\tLine {rel.line}: The relation {rel.id} and their associated relations -> {", ".join(map(lambda x: str(x.id), rel.associated))} <- form a switch, but do not respect the navigability property, where just 1 of them must have its navigability as None.\n'

        if len(rel.associated) == 5:
          # It's a double switch
          control_2 = True
          count = 0
          if rel.navigability == 'None':
            count += 1
          for r in rel.associated:
            if "Micro" not in list(r.levels):
              b_associated = False
              err_associated += f'\tLine {r.line}: The relations {rel.id} and {r.id} can not be associated, because {r.id} does not belong to the Micro level.\n'
              b_navigability = False
              err_navigability += f'\tLine {r.line}: The relations {rel.id} and {r.id} can not be associated, and therefore the navigability property can not be proved because {r.id} does not belong to the Micro level.\n'

            if r.navigability == 'None':
              count += 1
          if count != 2:
            b_navigability = False
            err_nav += f'\tLine {rel.line}: The relation {rel.id} and their associated relations -> {", ".join(map(lambda x: str(x.id), rel.associated))} <- form a double-switch, but do not respect the navigability property, where just 2 of them must have its navigability as None.\n'
      else:
        if list(rel.levels)[0] == "Micro":
          b_associated = False
          err_associated += f'\tLine {rel.line}: The relation {rel.id} does not respect the association between relations property, since it has {len(rel.associated)} relations associated.\n'
    else:
      if "Micro" in list(rel.levels):
        b_associated = False
        b_navigability = False
        err_associated += f'\tLine {rel.line}: Since the relation {rel.id} has more than 1 associated level, it was not possible to determine if the associated property was preserved.\n'
        err_navigability += f'\tLine {rel.line}: Since the relation {rel.id} has more than 1 associated level, it was not possible to determine if the navigability property was preserved.\n'



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

  if b_associated:
    p_print('Every defined relation respects the limited number of associated relations property.', True, err_associated)
  else:
    p_print('Relations found that disrespect the limited number of associated relations property.', False, err_associated)

  if b_navigability:
    if control_1:
      p_print('Every defined relation that form a 3-way relation with other relations, respect the navigability property.', True, err_nav)
    if control_2:
      p_print('Every defined relation that form a 6-way relation with other relations, respect the navigability property.', True, err_nav)
  else:
    if control_1:
      p_print('Not every relation that form a 3-way relation with other relations, respect the navigability property.', False, err_nav)
    if control_2:
      p_print('Not every relation that form a 6-way relation with other relations, respect the navigability property.', False, err_nav)

  if b_network == True:
    p_print('Every defined relation has 1 network associated.', True, err_network)
  else:
    p_print('Relations found that disrespect the network associated property.', False, err_network)

  if b_level == True:
    p_print('Every defined relation is defined at only 1 level.', True, err_level)
  else:
    p_print('Relations found that disrespect the associated level property.', False, err_level)

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
    err_relatedOn_meso  = ''
    err_relatedOn_macro = ''

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

      # Elements of each relation at Micro -> Inorder to check relatedOn
      elems_relation_micro = []

      # Relations errors
      relations_micro = True
      err_rmicro = ''
      # Elements erros
      elements_micro = True
      err_emicro = ''

      err_rel_micro_meso = ''
      micro_relatedOn = True
      err_relatedOn_micro = ''

      if meso:
        h = meso
        t_h = "Meso"
      if macro and not meso:
        h = macro
        t_h = "Macro"

      for m in micro.networkResources:
        # If its a netElement
        if m.__class__.__name__ == "NetElement":
          # Check if it has collection unordered
          if m.elementCollectionUnordered:
            elements_micro = False
            err_emicro += f'\t  - Line {micro.line}: Element {m.id}, defined at line {m.line}, is extended by some elements and should not, since it belongs to Micro level.\n'

        # If its a netRelation
        if m.__class__.__name__ == "NetRelation":
          elems_relation_micro.append((m.elementA, m.elementB))

          if m.elementA not in micro.networkResources:
            relations_micro = False
            err_rmicro += f'\t  - Line {m.line}: The element {m.elementA.id}, in this relation {m.id}, does not correspond to this network level (Micro).\n'
          if m.elementB not in micro.networkResources:
            relations_micro = False
            err_rmicro += f'\t  - Line {m.line}: The element {m.elementB.id}, in this relation {m.id}, does not correspond to this network level (Micro).\n'

          eA = m.elementA
          eB = m.elementB

          # related on - check if the relations at micro are preserved at meso
          if not h is None:
            if len(m.elementA.parents) == 1 and len(m.elementB.parents) == 1:
                pA = list(m.elementA.parents)[0]
                pB = list(m.elementB.parents)[0]

                if len(pA.levels) == 1 and len(pB.levels) == 1:
                  lvlA = list(pA.levels)[0]
                  lvlB = list(pA.levels)[0]
                  if lvlA == t_h and lvlB == t_h:
                    if not pA == pB:
                      f = False
                      for nr in h.networkResources:
                        if nr.__class__.__name__ == "NetRelation":
                          tp = (nr.elementA, nr.elementB)
                          if (pA, pB) == tp or (pB, pA) == tp:
                            f = True
                            break
                      if f == False:
                        err_rel_micro_meso += f'\t  - Line {m.line}: The relation {m.id}, represented at Micro, has no representation at the {t_h} level.\n'
                        micro_relatedOn = False
                  else:
                    err_rel_micro_meso += f'\t  - Line {m.line}: The relation {m.id}, represented at Micro, one of its elements\'s parent ({pA.id} or {pB.id}) is not represented at the {t_h}, so it is not possible to determine the representation at the {t_h} level.\n'
                    micro_relatedOn = False
                else:
                  err_rel_micro_meso += f'\t  - Line {m.line}: The relation {m.id}, represented at Micro, one of its elements\'s parent ({pA.id} or {pB.id}) does not respect the associated level property, so it is not possible to determine the representation at the {t_h} level.\n'
                  micro_relatedOn = False
            else:
              err_rel_micro_meso += f'\t  - Line {m.line}: The relation {m.id}, represented at Micro, one of its elements does not respect the element-parent property, so it is not possible to determine the representation at the {t_h} level.\n'
              micro_relatedOn = False

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

      if micro_relatedOn == False:
        check_micro = False
        err_relatedOn_micro = f'\tThere are some relations at the Micro Level that do not have a representation at {t_h} (Its parent level):\n'
        err_relatedOn_micro += err_rel_micro_meso
      else:
        correct += f'\tEvery relation defined in Micro has its representation at {t_h} Level (Its parent level).\n'

    # Check if Meso Level is declared
    if meso:
      err = ''
      meso_list = []
      temp_l = []
      # Elements of each relation at Meso -> Inorder to check relatedOn
      elems_relation_meso = []
      err_rel_meso_macro = ''
      relations_meso = True
      meso_relatedOn = True
      err_romeso = ''
      err_rmeso  = ''
      # Creates the extended meso elements
      for m in meso.networkResources:
        if m.__class__.__name__ == "NetElement": # check if a netElement
          meso_list =  meso_list + m.transitive_ecu # + [m]
        if m.__class__.__name__ == "NetRelation":

          temp_l = []
          elems_relation_meso.append((m.elementA, m.elementB))
          bool_temp = False

          eA = m.elementA
          eB = m.elementB

          # related on - check if the relations at meso are preserved at macro
          if macro:
            if len(m.elementA.parents) == 1 and len(m.elementB.parents) == 1:
                pA = list(m.elementA.parents)[0]
                pB = list(m.elementB.parents)[0]

                if len(pA.levels) == 1 and len(pB.levels) == 1:
                  lvlA = list(pA.levels)[0]
                  lvlB = list(pA.levels)[0]
                  if lvlA == "Macro" and lvlB == "Macro":
                    if not pA == pB:
                      f = False
                      for macro_net in macro.networkResources:
                        if macro_net.__class__.__name__ == "NetRelation":
                          tp = (macro_net.elementA, macro_net.elementB)
                          if (pA, pB) == tp or (pB, pA) == tp:
                            f = True
                            break
                      if f == False:
                        err_rel_meso_macro += f'\t  - Line {m.line}: The relation {m.id}, represented at Meso, has no representation at the Macro level.\n'
                        meso_relatedOn = False
                  else:
                    err_rel_meso_macro += f'\t  - Line {m.line}: The relation {m.id}, represented at Meso, one of its elements\'s parent ({pA.id} or {pB.id}) is not represented at the Macro, so it is not possible to determine the representation at the Macro level.\n'
                    meso_relatedOn = False
                else:
                  err_rel_meso_macro += f'\t  - Line {m.line}: The relation {m.id}, represented at Meso, one of its elements\'s parent ({pA.id} or {pB.id}) does not respect the associated level property, so it is not possible to determine the representation at the Macro level.\n'
                  meso_relatedOn = False
            else:
              err_rel_meso_macro += f'\t  - Line {m.line}: The relation {m.id}, represented at Meso, one of its elements does not respect the element-parent property, so it is not possible to determine the representation at the Macro level.\n'
              meso_relatedOn = False

          if micro:
            for m1 in m.elementA.elementCollectionUnordered:
              for m2 in m.elementB.elementCollectionUnordered:
                temp_l.append((m1,m2))

            for tup in elems_relation_micro:
              if tup in temp_l or tup[::-1] in temp_l:
                bool_temp = True
                break

            if bool_temp == False:
              err_romeso += f'\t  - Line {m.line}: The relation {m.id} represented at Meso Level, with {m.elementA.id} and {m.elementB.id} as elements, is not represented at the Micro level.\n'
              meso_relatedOn = False


          # Elements at meso relations must be defined at meso
          if m.elementA not in meso.networkResources:
            relations_meso = False
            err_rmeso += f'\t  - Line {m.line}: The element {m.elementA.id}, in this relation {m.id}, does not correspond to this network level (Meso).\n'
          if m.elementB not in meso.networkResources:
            relations_meso = False
            err_rmeso += f'\t  - Line {m.line}: The element {m.elementB.id}, in this relation {m.id}, does not correspond to this network level (Meso).\n'


      # Relations have level corresponding elements
      if relations_meso == False:
        check_meso = False
        err_relations_meso = f'\tThere are some relations at the Meso Level that have elements defined in a different level.\n'
        err_relations_meso += err_rmeso
      else:
        correct += f'\tEvery relation defined in Meso has valid level elements.\n'

      # If Micro Level or Macro exists
      if micro or macro:

        # Related On Meso
        if meso_relatedOn == False:
            check_meso = False
            err_relatedOn_meso = f'\tThere are some relations at the Meso Level that do not have a corresponding/representation relation at the remaining levels:\n'
            err_relatedOn_meso += err_romeso
            err_relatedOn_meso += err_rel_meso_macro
        else:
          if micro and not macro:
            correct += f'\tEvery relation defined in Meso has a corresponding relation at Micro.\n'
          if micro and macro:
            correct += f'\tEvery relation defined in Meso has a corresponding relation at Micro, and is represented at Macro.\n'
          if macro and not micro:
            correct += f'\tEvery relation defined in Meso is represented at Macro.\n'

      if micro:

        # Check if every micro is at the extended meso
        for e_micro in micro.networkResources:
          if e_micro.__class__.__name__ == "NetElement":
            if e_micro not in meso_list:
              err += f'\t  - Line {micro.line}: Element {e_micro.id} at Micro level must be at the extended Meso Level, declared in line {meso.line}.\n'
              b = False
              check_meso = False

            # An element can't be defined at the collectionUnordered of an element that share the same level
            if e_micro in meso_list and e_micro in meso.networkResources:
              err += f'\t  - Line {meso.line}: Element {extended_meso.id} defined as extended must be defined at the Micro Level, defined in line {micro.line}, and can not be defined at the Meso Level, line {meso.line}, as it is.\n'
              b = False
              check_meso = False

        # Check if extendend meso is in micro resource
        for extended_meso in meso_list:
          if extended_meso not in micro.networkResources:
              err += f'\t  - Line {meso.line}: Element {extended_meso.id} defined as extended must be defined at the Micro Level, defined in line {micro.line}.\n'
              b = False
              check_meso = False

          # Check for macro
          if macro:
            if extended_meso in macro.networkResources:
              err += f'\t  - Line {meso.line}: Element {extended_meso.id} defined as extended must be defined at the Micro Level, defined in line {micro.line}, and can not be defined at the Macro Level, line {macro.line}, as it is.\n'
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
        temp_l = []

        macro_extended_elements = True

        # Relations
        relations_macro = True
        macro_relatedOn = True
        err_rmacro  = ''
        err_romacro = ''
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

            temp_l = []
            # RelatedOn Property
            if micro or meso:
              # Possible Relations
              for m1 in mM.elementA.elementCollectionUnordered:
                for m2 in mM.elementB.elementCollectionUnordered:
                    temp_l.append((m1,m2))

              if micro and not meso:
                bool_temp = False
                for tup in elems_relation_micro:
                  if tup in temp_l or tup[::-1] in temp_l:
                    bool_temp = True
                    break
                if bool_temp == False:
                  macro_relatedOn = False
                  err_romacro += f'\t  - Line {mM.line}: The relation {mM.id} represented at Macro Level, with {mM.elementA.id} and {mM.elementB.id} as elements, is not represented at the Micro level.\n'

              if meso:
                bool_temp = False
                for tup in elems_relation_meso:
                  if tup in temp_l or tup[::-1] in temp_l:
                    bool_temp = True
                    break
                if bool_temp == False:
                  macro_relatedOn = False
                  err_romacro += f'\t  - Line {mM.line}: The relation {mM.id} represented at Macro Level, with {mM.elementA.id} and {mM.elementA.id} as elements, is not represented at the Meso level.\n'


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


        # Related On Meso
        if macro_relatedOn == False:
            check_macro = False
            if micro and not meso:
              err_relatedOn_macro = f'\tThere are some relations at the Macro Level that do not have a corresponding relation at Micro level:\n'
              err_relatedOn_macro += err_romacro
            if meso:
              err_relatedOn_macro = f'\tThere are some relations at the Macro Level that do not have a corresponding relation at Meso level:\n'
              err_relatedOn_macro += err_romacro
        else:
          if micro and not meso:
            correct += f'\tEvery relation defined in Macro has a corresponding relation at Micro.\n'
          if meso:
            correct += f'\tEvery relation defined in Macro has a corresponding relation at Meso.\n'

        # If Micro Level exists
        if micro:
          err = '' # reset error string.
          for e_micro in micro.networkResources:
            if e_micro.__class__.__name__ == "NetElement":
              if e_micro not in macro_list:
                err += f'\t  - Line {micro.line}: Element {e_micro.id} at Micro level must be at the extended Macro Level, declared in line {macro.line}.\n'
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
              if e_meso not in macro_list and e_meso:
                err += f'\t  - Line {meso.line}: Element {e_meso.id} at Meso level must be at the extended Macro Level, declared in line {macro.line}.\n'
                b1 = False
                check_macro = False
          if b1 == False:
            err_meso_macro = f'\tNot all elements at Meso are in the extended Macro, at the network {netw.id}:\n'
            err_meso_macro += err
          else:
            correct += f'\tThe network {netw.id} has every Meso element in the extended Macro Level.\n'

    err_elements  = err_elements_micro + err_elements_meso + err_elements_macro
    err_relations = err_relations_micro + err_relations_meso + err_relations_macro
    dic_netw_str[netw] = (err_elements, err_relations, err_relatedOn_micro, err_meso, err_relatedOn_meso, err_macro, err_micro_macro, err_meso_macro, err_relatedOn_macro, correct)


  # Prints to the user - Error treatment
  if check_micro and check_macro and check_meso:
    p_print('Every declared network respects every network property.\n', True, 'ignore_net')
    for nt in dic_netw_str:
      (e1,e2,e3,e4,e5,e6,e7,e8,e9,c) = dic_netw_str[nt]
      print(f'\n     • For the network \033[1m{nt.id}\033[0m defined at line {nt.line}:')
      print(Fore.GREEN + '\n\tVerified properties:')
      print(Style.RESET_ALL, end='')
      print(c, end='')
  else:
    p_print('Not every declared network respects the network\'s property.\n', False, 'ignore_net')
    for nt in dic_netw_str:
      (e1,e2,e3,e4,e5,e6,e7,e8,e9,c) = dic_netw_str[nt]
      print(f'     • For the network \033[1m{nt.id}\033[0m defined at line {nt.line}:')
      print(Fore.GREEN + '\n\tVerified properties:')
      print(Style.RESET_ALL, end='')
      print(c, end='')
      if(e1 or e2 or e3 or e4 or e5 or e6 or e7 or e8 or e9):
        print(Fore.RED + '\n\tRefuted properties:')
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
      if (e7):
        print(e7, end='')
      if (e8):
        print(e8, end='')
      if (e9):
        print(e9, end='')
