#!/usr/bin/python3
import sys, os
from os.path import isfile

# Created modules - Parser, ValidadorSchema and RulesAlloy
from parser_rail.parser import parseRailML
from verifier.xml_checker import check_
from verifier.topology_rules import assumptions_


# Main function which is gonna call the Schema validator, the parser and then the validator.
def main():

  if len(sys.argv) == 2 and isfile('./examples/'+sys.argv[1]):

    f = './examples/' + sys.argv[1]
    f = os.path.abspath(f)

    base, ext = os.path.splitext(f)
    if ext.lower() not in ('.xml'):
      print("ERROR: File given isn't a xml file.")
      sys.exit()


    # Validate Schema xml
    #check_(f)
    # Parse file
    r = parseRailML(f)
    # Validate alloy rules
    assumptions_(r)


  else:
    print('Must give a file as input.')
    sys.exit()

main()
