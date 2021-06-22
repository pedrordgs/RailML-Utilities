# Using alloy

In this project we used alloy to represent railML in a more simple and abstract way. With railML modeled in alloy, we were able to find properties that would later be used in the [validator](https://github.com/pedrordgs/RailML-Utilities/tree/master/validator).

## How to use alloy
We recommend to read the [alloy](https://github.com/AlloyTools/org.alloytools.alloy) github page.

### TL;DR
1. Grab the latest `.jar` file available in the alloy github page.
2. Run `java -jar latest_alloy_version.jar`.

## railML to alloy
This module is used to import railML instances to alloy. The main goal here is to test if the specified railML instance holds on all the properties. For more information on how to convert railML into alloy instances, click [here](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/railMLToAlloy/README.md).

## alloy to railML
Similar to the topic described above, this module has the goal of transforming alloy instances in railML. For more information, click [here](https://github.com/pedrordgs/RailML-Utilities/blob/master/alloy_related/alloyToRailML/README.md).
