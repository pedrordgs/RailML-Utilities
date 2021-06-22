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

#### XML Schema checking
- The [schemas](https://www.railml.org/en/download/schemes.html) provided by **railVivid** were used for schema checking.
- Every attribute **ref** must be a valid attribute **id**.
- For each network, we can have at most 1 Micro, 1 Meso and 1 Macro level.

#### Alloy rules verified
- **NetElements Assumptions**
    - [0] Every element's relation must reference the latter, implying that relation must be redundant.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L77)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule0.xml)
    - [1] Elements can be referenced as part of others elements, abstracting some elements as one. However, an element can't ever be a recursively part of itself.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L83)
    - [2] An element must have at most 1 parent (By parent, we mean that each element can only be an element part of at most 1 element).[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L89)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule2.xml)
    - [3] **Element On**: If an element is connected to two different elements in the same endpoint, those must also be connected and their positions must be preserved.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L98)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule3.xml)
    - [4] Each element must have 1 associated network. An element must be a networkResource of 1 and on 1 level.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L104)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule4.xml)
- **NetRelations Assumptions**
    - [5] Each relation must have only 1 associated network. An relation must be a networkResource of 1 and only 1 level.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L126)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule5.xml)
    - [6] Must not exist different relations representing the same relation between elements.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L131)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule6.xml)
    - [7] An element can't relate to itself at the same position. So, can't exist a relation with elementA = elementB and positionA = positionB.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L140)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule7.xml)
    - [8] Each relation has a set of associated relations, where they relate with each other by having one shared element at the same position. Each relation can either have 1, 2 (switch abstraction) or 5 (double-switch abstraction) associated relations.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L150)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule8.xml)
    - [9] *Navigability Property*: If 3 relations are associated, one of them must have its navigability to None. If 5 relations are associated, two of them must have its navigability to None.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L159)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule9.xml)
- **Network Assumptions**

    Note that networks can have different levels, those being Micro, Meso and Macro, hierarchically ordered.
    - Micro level should exist in each defined network, but the user can opt for the non-declaration of this level and proceed to the verification of the remaining levels.
    - [10] Elements defined at the Micro level can't be extended by other elements, meaning that elementCollectionUnordered of these elements must be empty.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L185)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule10.xml)
    - [11] Extending every element at the Meso level, they must represent a micro element. Meaning that, Micro level must be the same as the extended Meso level.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L194)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule11.xml)
    - [12] Extending every element at the Macro level, they either represent a meso element or a micro element. Meaning that, the logic disjunction of both Micro and Meso level must be the same as the extended Macro level.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L207)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule12.xml)
    - [13] Every relation defined at any level, their corresponding elements must be defined at the same level.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L218)
    - [14] Every relation defined at any level, must be represented at the remaining levels.[alloy](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/topology.als#L227)[negation](https://github.com/pedrordgs/RailML-Utilities/blob/master/examples/railml/negRule14.xml)

#### Positioning Systems
These properties related to the positioning systems were not specified in alloy because of their complex nature, where might be some missed properties.
- **Geometric Positioning System**
    - Every GPS must be time valid, meaning that their corresponding validation date can't be outdated.
    - If one of the declared GPS has no netElement associated, a warning will be displayed.
    - The difference between endpoints of one netElement, declared at the same GPS, must be lower than its length.
    - If a netElement has elementParts associated, their combining endpoints difference must be equal to the netElement endpoints difference, for each shared GPS.
    - If both elements of one relation are represented at the same GPS, they must be connected.
- **Linear Positioning System**
    - Every LPS must be time valid, meaning that their corresponding validation date can't be outdated.
    - If one of the declared LPS has no netElement associated, a warning will be displayed.
    - The difference between endpoints of one netElement, declared at the same LPS, must be lower than its length.
    - If a netElement has elementParts associated, their combining endpoints difference must be equal to the netElement endpoints difference, for each shared LPS.
    - If both elements of one relation are represented at the same LPS, they must be connected.

**Contact us**, if you find a not mentioned property, assuring that the latter is always preserved.
