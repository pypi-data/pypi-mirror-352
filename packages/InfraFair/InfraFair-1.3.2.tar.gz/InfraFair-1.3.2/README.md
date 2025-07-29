![image](doc/Images/InfraFair_Logo.png)
[![Versions](https://img.shields.io/pypi/pyversions/InfraFair.svg)](https://pypi.org/project/InfraFair)
[![PyPI](https://badge.fury.io/py/InfraFair.svg)](https://badge.fury.io/py/InfraFair)
[![License](https://img.shields.io/badge/License-AGPL%20v3-blue.svg)](https://github.com/IIT-EnergySystemModels/InfraFair/blob/main/LICENSE)
[![Documentation Status](https://readthedocs.org/projects/infrafair/badge/?version=latest)](https://infrafair.readthedocs.io/en/latest/?badge=latest)
[![PePy](https://static.pepy.tech/badge/InfraFair)](https://www.pepy.tech/projects/InfraFair)

# InfraFair
*"Fairness in allocating infrastructure cost"*   

**InfraFair** has been developed at the [Instituto de Investigación Tecnológica (IIT)](https://www.iit.comillas.edu/index.php.en) 
of the [Universidad Pontificia Comillas](https://www.comillas.edu/en/).

The full documentation can be accessed [here](https://infrafair.readthedocs.io/en/latest/index.html)

## Description
The InfraFair is a modelling tool aimed at computing the allocation of the cost of energy infrastructure according 
to the economic use expected to be made by agents, driving efficient investment decisions. The modelling tool 
employs the **Average Participations Method (APM)** that allocates the 
cost based on the electrical usage that each agent makes of each infrastructure asset as a reasonable proxy 
to the benefits, the former obtained from the latter. The basic intuition behind the APM is that 
energy consumed by demands and produced by generators, as well as the responsibility for causing energy 
flows, can be assigned by employing **a simple heuristic rule** that only uses the actual pattern of flows in 
the infrastructure network. 

The rule assumes that energy flows can be traced by supposing that at any network node, the inflows are distributed proportionally among the outflows. This is the so-called **proportionality rule**. Implicit in this rule is the assumption that energy does not flow in the opposite direction to that of the prevalent (net) flow over each asset, which, according to this assumption, is the only existing flow. Based on these assumptions, the method traces the flow of energy from individual sources to individual sinks in all the network assets.

## Scope
InfraFair determines the network utilisation of agents, system operators and countries. 
Based on this utilisation and assuming that it reflects the economic benefits received by agents, 
it determines the responsibility of each agent in the construction of each element in the network. 
Additionally, it can also attribute losses on the assets to their responsible agents.
In order to reasonably reflect agent utilisation of infrastructure, multiple representative snapshots 
of annual network usage should be provided. InfraFair presents a decision support tool for tariff 
design for regional power transmission infrastructure, but it can be used for national infrastructure 
as well as other types of infrastructures operating on the same principle of flow (*flow-based infrastructure*), 
such as gas and hydrogen infrastructure. 
All assets that have a flow usage can be represented in the network model. For instance, the electrical network can include
power lines, transformers, breaks, series capacitors and phase shifting transformers.


## Functionality
Inputs to the model must consist of the **map of flows** in each of the assets as well as the **injections and withdrawals** of energy at each node. Additionally, the **rating capacity and the capital cost** of each asset must be provided for the model to be able to allocate costs to network users. Other information, such as the voltage and the length of each asset, can be provided to produce optional categorised results. When provided with hourly representative snapshots of these inputs, InfraFair can calculate (per snapshot and overall annual weighted average):

* Individual agent flows, losses and cost contributions to each asset in the network.
* Country flows, losses and cost contributions to each asset in the network.
* Individual agent and country utilisation of each asset in the network.
* Individual Agent flows, losses and cost contributions to similar aggregated assets.
* Country flows, losses and cost contributions to similar aggregated assets. 
* Individual agent and country utilisation of similar aggregated assets.
* Individual Agent total cost contribution to be paid.
* Individual agent and country utilisation of the whole network.
* Country flows, losses and cost contributions made of the use of each other country.
* Country total flow and cost contributions made of the use of the rest of the network.
* Country flows, losses and cost incurred from the use made by the rest of the countries.


## Installation
InfraFair can be easily installed with pip:

      > pip install InfraFair 

Alternatively, it can be installed from its GitHub repository following these four steps:

1. Clone the InfraFair repository, which includes the folder structure and all necessary functions to run the model.
2. Launch the command prompt (Windows: Win+R, type "cmd", Enter) or the Anaconda prompt.
3. Set up the path to where the repository was cloned, using the command 
      
         > cd "C:\Users\<username>\...\InfraFair".
4. Install InfraFair via pip by using the command 
      
         > pip install . 

An already installed model can be upgraded to the latest version with the following command:

      > pip install --upgrade InfraFair 


## Dependencies
InfraFair is programmed and tested to be compatible with Python 3.8 and
above. Like any software project, InfraFair stands on the shoulders of giants. Those giants mainly include:

* [pandas](<http://pandas.pydata.org/>) for storing data about the network.
* [numpy](<http://www.numpy.org/>) for calculations, such as matrix manipulation.
* [matplotlib](<https://matplotlib.org/>) for aggregating results.


## Quick start
Once installation is complete, InfraFair can be 
executed by using a command prompt. In the directory of your choice, open and execute the InfraFair.py script by using 
the following on the command prompt (Windows) or Terminal (Linux) (Depending on what your standard python version is, 
you might need to call python3 instead of python)::

    > python InfraFair.py

Then, three parameters (directory folder, and configuration file) will be asked for.

**Remark**: at this step, only press enter for each input and InfraFair will be executed with the default parameters.

After this, in a directory of your choice, make a copy of the [Simple example](<https://github.com/IIT-EnergySystemModels/InfraFair/tree/main/Examples/Simple_ex>) or [EU example](<https://github.com/IIT-EnergySystemModels/InfraFair/tree/main/Examples/EU_ex>) case to create a new 
case of your choice but using the current format of the .csv files.
Proper execution of InfraFair.py can be made by introducing the new case and the directory of your choice. 

Then, the output results should be written in the same folder as the case input. 

**Note**: An alternative way to run the model is by creating a new script **script.py**, and writing the following::
        
    from InfraFair import InfraFair_run
        
    InfraFair_run(<dir>, <case>, <config_file>)

## Developers
| Member                     | Username  | 
| -------------------------- | --------- |
| Mohamed A.Eltahir Elabbas | [@MohElabbas](https://github.com/MohElabbas) |

We strongly welcome anyone interested in contributing to this project.


## License
Copyright 2023 [Universidad Pontificia Comillas](https://www.comillas.edu/en/).

InfraFair is licensed under the open source [AGPL-3.0 license](https://github.com/IIT-EnergySystemModels/InfraFair/tree/main/LICENSE).


## Execution
![image](doc/Images/Execution.png)


## Reference
Mohamed A. Eltahir Elabbas, Luis Olmos Camacho, Ignacio Pérez-Arriaga, *[InfraFair: Infrastructure cost allocation](<https://www.sciencedirect.com/science/article/pii/S2352711025000366>)*, 2025, [SoftwareX](<https://www.sciencedirect.com/journal/softwarex>), Vol. 29, pp. 102069-1 - 102069-9, [DOI:10.1016/j.softx.2025.102069](<https://doi.org/10.1016/j.softx.2025.102069>).

InfraFair [presentation](<https://github.com/IIT-EnergySystemModels/InfraFair/tree/main/doc/Presentation/InfraFair_Introduction.pdf>).
