# RailML Validator

The purpose of this validator is to extend the verification tool that railML provides ([railVivid](https://www.railml.org/en/user/railvivid.html)), and go beyond the XML schema checking and validate properties that should be valid in every railML file. As mentioned [here](https://github.com/pedrordgs/railML/blob/master/alloy_related/README.md), alloy was a great help in finding and validating properties that were later verified in this validator.

The [schemas](https://www.railml.org/en/download/schemes.html) provided by **railVivid** were used for schema checking.

## Usage

In order to use this validator, it must be given a railML file to the main program named **validator_rml.py**.

```python validator_rml.py [input file]```

A railML instance can be found [here](https://github.com/pedrordgs/railML/blob/master/validator/examples/railML.xml).

The file must be downloaded and copied to the [examples](https://github.com/pedrordgs/railML/tree/master/validator/examples) folder.
