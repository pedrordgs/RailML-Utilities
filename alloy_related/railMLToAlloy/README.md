# RailML to alloy

This model converts railML into alloy instances that can be imported on [AlloyAnalizer](https://alloytools.org/). The main goal for this model is to get a railML example into alloy to check desired properties with alloy evaluator. More information on how to use the alloy evaluator can be found [here](https://alloy.readthedocs.io/en/latest/tooling/visualizer.html#evaluator).


## Usage

Alloy file path needs to be specified.

```python railml2alloy.py [alloy file path] [input file]```

There are some input examples [here](https://github.com/pedrordgs/RailML-Utilities/tree/master/examples/railml/).

Note that alloy file needs to be `test.als` in order to take full advantage of evaluator.

##### Example

```python railml2alloy.py ../test.als examples/railml.xml```
