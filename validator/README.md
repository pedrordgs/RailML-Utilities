# RailML Validator

The purpose of this validator is to extend the verification tool that railML provides ([railVivid](https://www.railml.org/en/user/railvivid.html)), and go beyond the XML schema checking and validate properties that should be valid in every railML file. As mentioned [here](https://github.com/pedrordgs/railML/blob/master/alloy_related/README.md), alloy was a great help in finding and validating properties that were later verified in this validator.

The [schemas](https://www.railml.org/en/download/schemes.html) provided by **railVivid** were used for schema checking.

## Usage

In order to use this validator, it must be given a railML file to the main program named **validator_rml.py**.

```python validator_rml.py [input file]```

A railML instance can be found [here](https://github.com/pedrordgs/RailML-Utilities/blob/master/validator/examples/tutorial.xml).

The file must be downloaded and copied to the [examples](https://github.com/pedrordgs/RailML-Utilities/tree/master/validator/examples/) folder.

## Verifier
The folder [verifier](https://github.com/pedrordgs/RailML-Utilities/blob/master/validator/verifier/) contains every file used for validation purposes. Before verifying the rules explored using **Alloy**, schema must be valid. Therefore, this verification process was divided in different files.

#### [XML Schema checking](https://github.com/pedrordgs/RailML-Utilities/blob/master/validator/verifier/xml_checker.py)
- The [schemas](https://www.railml.org/en/download/schemes.html) provided by **railVivid** were used for schema checking.
- Every attribute **ref** must be a valid attribute **id**.

#### [Alloy rules verified](https://github.com/pedrordgs/RailML-Utilities/blob/master/validator/verifier/alloy_rules.py)
- **NetElements Assumptions**
    - Every element's relation must reference the latter, implying that relation must be redundant.
    - Elements can be referenced as part of others elements, abstracting some elements as one. However, an element can't ever be a recursively part of itself.
- **NetRelations Assumptions**
    - Must not exist different relations representing the same relation between elements.
    - An element can't relate to itself at the same position. So, can't exist a relation with elementA = elementB and positionA = positionB.
    - **Element On**: If an element is connected to two different elements in same endpoint, those must also be connected and their positions must be preserved.
- **Network Assumptions:** \
Note that, networks can have different levels, those being Micro, Meso and Macro, hierarchically ordered.
    - Micro level should exist in each defined network, but the user can opt for the non-declaration of this level and proceed to the verification of the remaining levels.
    - Elements defined at the Micro level can't be extended by other elements, meaning that elementCollectionUnordered of these elements must be empty.
    - Extending every element at the Meso level, they must represent a micro element. Meaning that, Micro level must be the same as the extended Meso level.
    - Extending every element at the Macro level, they either represent a meso element or a micro element. Meaning that, the logic disjunction of both Micro and Meso level must be the same as the extended Macro level.
    - Every relation defined at any level, their corresponding elements must be defined at the same level.
    - Relations defined at the Micro level, must also be defined at both Meso and Macro levels. Same for relations defined at the Meso level, which must be defined at the Macro level.
