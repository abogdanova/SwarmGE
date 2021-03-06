# SwarmGE

SwarmGE is a package build on the base of PonyGE (grammatical evolution package) that evolves variations of swarm algorythms and allows benchmarking them with Black Box Optimisation framework (bbob)
BNF-style grammar for the evolution of swarms can be found in grammars/swarmge.pybnf 
At the present stage it describes hybridisation of PSO (particle swarm optimisation), ABA (artificial bee algorithm) and CSO (cockoo search optimisation). It relies on helper.py for function declarations.
We also use SwarmPackagePy for comparing and visualizing the performance of hybrids against conventional swarm algorithms.

# Instructions

To evolve swarm:
- function for training has to be declared in src/fitness folder adopting base_ff class from fitness.base_ff_classes.base_ff (TODO: declare selected functions so that the number of function evaluations to reach some accuracy margin is taken as fitness value. Right now, ackley_function.py is measuring fitness as proximity of the solution to the absolute function minimum)
- specify the desired parameters in parameters/swarmge.txt
- from the console run "python ponyge.py --parameters swarmge.txt"
- find best phenotype in results/"new experiment folder"/best.txt

To check swarm performance:
- Save result as swarm class in SwarmPackagePy/swarmtest.py
- Run example.py modified to call the new swarm

To test the swarm on bbob suite:
- insert GE output (phentype) as class swarmge(sw) in bbob/solvers.py
- run bbob/example_experiment_for_beginners.py


# PonyGE2 (https://github.com/PonyGE/PonyGE2)
--------------

Grammatical Evolution (GE) is a population-based evolutionary algorithm, where a BNF-style grammar is used in the genotype to phenotype mapping process [O'Neill & Ryan, 2003].

PonyGE2 is an implementation of GE in Python. It's intended as an advertisement and a starting-point for those new to GE, a reference for students and researchers, a rapid-prototyping medium for our own experiments, and as a Python workout.

The original version of PonyGE (https://github.com/jmmcd/ponyge) was originally designed to be a small single-file implementation of GE. However, over time this has grown to a stage where a more formal structured approach was needed. This has led to the development of PonyGE2, presented here.

A technical paper describing PonyGE2 has been published and been made freely available on arXiv at:

https://arxiv.org/abs/1703.08535

PonyGE2 can be referenced using the following citation:

        Fenton, M., McDermott, J., Fagan, D., Forstenlechner, S., Hemberg, E., and O'Neill, M. PonyGE2: Grammatical Evolution in Python. arXiv preprint, arXiv:1703.08535, 2017.

The PonyGE2 development team can be contacted via [GitHub](https://github.com/jmmcd/PonyGE2/issues/new). 

PonyGE2 is copyright (C) 2009-2017


# Requirements
--------------

PonyGE2 requires Python 3.5 or higher.
Using matplotlib, numpy, scipy, scikit-learn (sklearn), pandas.

All requirements can be satisfied with [Anaconda](https://www.continuum.io/downloads).


# Running PonyGE2
-----------------

We don't provide any setup script. You can run an example problem (the default is regression, see below) just by typing:

    $ cd src
    $ python ponyge.py

This will run an example problem and generate a results folder. The folder contains several files showing the run's stats, producing graphs and documenting the parameters used, as well as a file detailing the best individual. For a more verbose command line experience run the following:

    $ cd src
    $ python ponyge.py --verbose

Each line of the verbose output corresponds to a generation in the evolution, and prints out all statistics on the current run (only if `--verbose` is specified). Upon completion of a run, the best individual is printed to the command line, along with summary statistics.

There are a number of arguments that can be used for passing values via the command-line. To see a full list of these just run the following:

    $ python ponyge.py --help


# About PonyGE2
---------------

Grammatical Evolution (GE) [O'Neill & Ryan, 2003] is a grammar-based form of Genetic Programming [Koza, 1992]. It marries principles from molecular biology to the representational power of formal grammars. GE’s rich modularity gives a unique flexibility, making it possible to use alternative search strategies, whether evolutionary, deterministic or some other approach, and to radically change its behaviour by merely changing the grammar supplied. As a grammar is used to describe the structures that are generated by GE, it is trivial to modify the output structures by simply editing the plain text grammar. This is one of the main advantages that makes the GE approach so attractive. The genotype-phenotype mapping also means that instead of operating exclusively on solution trees, as in standard GP, GE allows search operators to be performed on the genotype (e.g., integer or binary chromosomes), in addition to partially derived phenotypes, and the fully formed phenotypic derivation trees themselves.

PonyGE2 is primarily a Python implementation of canonical Grammatical Evolution, but it also includes a number of other popular techniques and EC aspects.

# For full documentation of PonyGE2, see the [wiki](https://github.com/PonyGE/PonyGE2/wiki).
---------------------------------------------------------------------------

https://github.com/PonyGE/PonyGE2/wiki

# References
------------

Michael O'Neill and Conor Ryan, "Grammatical Evolution: Evolutionary Automatic Programming in an Arbitrary Language", Kluwer Academic Publishers, 2003.

Koza, J.R., 1992. "Genetic programming: on the programming of computers by means of natural selection (Vol. 1)". MIT press.


# SwarmPackagePy (https://github.com/SISDevelop/SwarmPackagePy)
*SwarmPackagePy* is the package, witch contains the following swarm optimization algorithms:

1. Artificial Bee Algorithm
2. Bat Algorithm
3. Bacterial Foraging Optimization
4. Cat Swarm Optimization
5. Chicken Swarm Optimization
6. Cuckoo Search Optimization
7. Firefly algorithm
8. Firework Algorithm
9. Gravitational Search Algorithm
10. Grey Wolf Optimizer
11. Harmony Search
12. Particle Swarm Optimization
13. Social Spider Algorithm
14. Whale Swarm Algorithm

Every algorithm has arguments listed below:

* n: number of agents
* function: test function
* lb: lower limits for plot axes
* ub: upper limits for plot axes
* dimension: space dimension
* iteration: number of iterations

Every algorithm has methods listed below:

* get_agents(): returns a history of all agents of the algorithm
* get_Gbest(): returns the best position of algorithm

All documentation you can view on the github repository https://github.com/SISDevelop/SwarmPackagePy.
For all questions and suggestions contact us at swarm.team.dev@gmail.com. For more info you could also write to:

* team leads - vllitskevich@gmail.com, polly.bartoshevic@gmail.com,
* programmers - alexeymaleyko@gmail.com, b317.forinko@gmail.com, vladislaw.kapustin@gmail.com.

