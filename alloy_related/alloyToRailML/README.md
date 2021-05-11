# Alloy to railML

This model has the goal of transforming alloy instances in railML. The main goal here is to represent and visualize alloy instances for easier interpretation as well as create test cases for software that uses railML. 

## Usage

An alloy instance can be [exported from alloy](https://alloy.readthedocs.io/en/latest/tooling/visualizer.html#file).

```python alloy2railml.py [input file]```

There are some input examples [here](https://github.com/pedrordgs/railML/tree/master/alloy_related/alloyToRailML/examples)

##### Example

```python alloy2railml.py examples/three_levels.xml```
