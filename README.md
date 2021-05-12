# railML utilities

## The project
*railML (railway Markup Language) is an open, XML based data exchange format for data interoperability of railway applications. Valid railML models have many restrictions that cannot be captured by XML schemas alone. The primary goal of this project is to develop a formal model of railML with the goal of identifying such restrictions, with the secondary goal of developing a validator that can detect potential issues in railML files.*

## About
This project started of as a school project. The main goal was to verify if the railML format had no flaws and at the same time simplify the process of creating a railway (since railML is very complex). To do so, we used the [Alloy](https://alloy.readthedocs.io/en/latest/index.html) verification tool. Since railML is very extensive we started by verifying only the topology section. After some weekly reunions, alongside with our project manager, we decided that it would be nice to have a xml validator that validates references as well as a web visualizer to display a railway infrastructure. Both of these new features would still only focus on the topology.
The main goal of this project after finishing the topology is to expand all the features to cover 100% of the railML format.

## Features
- [Verification with Alloy](https://github.com/pedrordgs/railML/tree/master/alloy_related)
- [railML validator](https://github.com/pedrordgs/railML/tree/master/validator)
- [railML visualizer](https://github.com/pedrordgs/railML/tree/master/visualizer)

## Contributing
Contribution is much welcome! Anyone is able to contributing by submitting a PR. If you want to help but are having some difficulties either message or email any developer.

## Credits
This project was developed by:
- José Pedro Silva (a84577@alunos.uminho.pt)
- Luís Mário Ribeiro (a85954@alunos.uminho.pt)
- Pedro Rodrigues (a84783@alunos.uminho.pt)

And supervised by:
- Alcino Cunha (alcino@di.uminho.pt)
