------------
#Introduction
------------

Grammatical Evolution (GE) is a population-based evolutionary algorithm, where a BNF-style grammar is used in the genotype to phenotype mapping process.

PonyGE2 is an implementation of GE in Python. It's intended as an advertisement and a starting-point for those new to GE, a reference for students and researchers, a rapid-prototyping medium for our own experiments, and as a Python workout.

The original version of PonyGE (https://github.com/jmmcd/ponyge) was originally designed to be a small single-file implementation of GE. However, over time this has grown to a stage where a more formal structured approach was needed. This has led to the development of PonyGE2 (https://github.com/jmmcd/ponyge2), presented here.

The PonyGE2 development team can be contacted at:

    Michael Fenton <michaelfenton1@gmail.com>,
    James McDermott <jamesmichaelmcdermott@gmail.com>,
    Erik Hemberg <erik.hemberg@gmail.com>,
    David Fagan <fagan.david@gmail.com>,
    Stefan Forstenlechner.

PonyGE2 is copyright (C) 2009-2017


------------
#Requirements
------------

PonyGE requires Python 3.5 or higher.
Using matplotlib, numpy, scipy, scikit-learn (sklearn), pandas.

All requirements can be satisfied with Anaconda.


--------------
#Running PonyGE
--------------

We don't provide any setup script. You can run an example problem (the default is regression, see below) just by typing:

    $ cd src
    $ python ponyge.py

This will run an example problem and generate a results folder. The folder contains several files showing the run's stats, producing graphs and documenting the parameters used, as well as a file detailing the best individual. For a more verbose command line experience run the following:

    $ cd src
    $ python ponyge.py --verbose

Each line of the verbose output corresponds to a generation in the evolution, and prints out all statistics on the current run (only if `--verbose` is specified). Upon completion of a run, the best individual is printed to the command line, along with summary statistics.

There are a number of flags that can be used for passing values via the command-line. To see a full list of these just run the following:

    $ python ponyge.py --help


-------------
#About PonyGE2
-------------

PonyGE2 is primarily a Python implementation of canonical Grammatical Evolution, but it also includes a number of other popular techniques and EC aspects.  


#Representation
---------------

There are two ways in which an individual can be represented in PonyGE2: with a linear genome, and with a derivation tree.

##Linear Genome Representation

Traditional Grammatical Evolution uses linear genomes (also called chromosomes) to encode genetic information [O'Neill & Ryan, 2003]. These linear genomes are then mapped via the use of a formal BNF-style grammar to produce a phenotypic output. All individuals in PonyGE2 have an associated linear genome which can be used to exactly reproduce that individual.
 
PonyGE2 contains a number of operators that manage linear genomes. These are discussed in later sections.

*__NOTE__ that in general the use of a linear genome does not allow for "intelligent" operations. Although intelligent linear genome operators exist [Byrne et al., 2009], they are not implemented here as similar functions can be performed using derivation-tree based operations.*

##Derivation Tree Representation

##Bloat

There are currently three methods implemented to control genetic bloat in PonyGE2:
1. Limiting the maximum derivation tree depth
2. Limiting the number of nodes in a derivation tree
3. Limiting the maximum length of the genome.   

###Max Tree Depth

By default there are no limits to the maximum depth a derivation tree can take. This can lead to genetic bloat, dramaticaly slowing down the overall evolutionary process. One way to prevent this is to specify a global maximum tree depth with the flag:

    --max_tree_depth [INT]
    
or by setting the parameter `MAX_TREE_DEPTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the desired maximum depth limit for derivation trees.

*__NOTE__ that setting the parameter* `MAX_TREE_DEPTH` *or flag* `--max_tree_depth` *to 0 is the same as setting no maximum tree depth, i.e. trees will be allowed to grow in an un-controlled manner.*

*__NOTE__ that the parameter* `MAX_TREE_DEPTH` *is distinct from the parameter* `MAX_INIT_TREE_DEPTH`, *which is used solely to control derivation tree depth during derivation tree-based initialisation.*

###Max Tree Nodes

By default there are no limits to the maximum number of nodes a derivation tree can have. This can lead to genetic bloat, dramaticaly slowing down the overall evolutionary process. One way to prevent this is to specify a global maximum number of derivation tree nodes with the flag:

    --max_tree_nodes [INT]
    
or by setting the parameter `MAX_TREE_NODES` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the desired maximum number of nodes for derivation trees.

*__NOTE__ that setting the parameter* `MAX_TREE_NODES` *or flag* `--max_tree_nodes` *to 0 is the same as setting no limit on the maximum number of nodes a derivation tree can have, i.e. trees will be allowed to grow in an un-controlled manner.*

###Max Genome Length

By default there are no limits to the maximum length a genome can take. This can lead to genetic bloat, dramaticaly slowing down the overall evolutionary process. One way to prevent this is to specify a global maximum genome length with the flag:

    --max_genome_length [INT]
    
or by setting the parameter `MAX_GENOME_LENGTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the desired maximum global genome length.

*__NOTE__ that setting the parameter* `MAX_GENOME_LENGTH` *or flag* `--max_genome_length` *to 0 is the same as setting no limit to the lengths of genomes, i.e. genomes will be allowed to grow in an un-controlled manner.*

*__NOTE__ that the parameter* `MAX_GENOME_LENGTH` *is distinct from the parameter* `MAX_INIT_GENOME_LENGTH`, *which is used solely to control genome size during genome-based initialisation.*

A full breakdown of the currently implemented elements in PonyGE2 is provided below. This includes a brief description of each individual component and how to activate them.

#Evolutionary Parameters:
------------------------

One of the central components of PonyGE is the `algorithm.parameters.params` dictionary. This dictionary is referenced throughout the entire program and is used to streamline the whole process by keeping all optional parameters in the one place. This also means that there is little to no need for arguments to the various functions in PonyGE, as these arguments can often be read directly from the parameters dictionary. Furthermore, the parameters dictionary is used to specify and store optional functions such as `initialisation`, `crossover`, `mutation`, and `replacement`.

There are three different ways to specify operational parameters with PonyGE.

1. The first and most basic method is to modify the algorithm.parameters.params dictionary directly in the code.
2. The second method is to list your desired parameters in a specialised parameters text file. Example parameters files are located in the `parameters` folder. When using parameters files, it is necessary to specify the desired parameter file from the command line. This is done by calling

        --parameters [FULL FILE NAME INCLUDING EXTENSION]
    
3. The third and final method is to list desired parameters from the command line. To see a list of all currently available command-line arguments implemented in the parser, type

        $ python ponyge.py --help
    
*__NOTE__ that each of the above three options successively supersedes the previous ones, i.e. parameters specified in a parameters file will over-write those set in the original* `algorithm.parameters.params` *dictionary, and parameters set from the command line will over-write those set in the parameters file.*

PonyGE2 automatically parses the correct path for all operators, meaning you don't have to specify the full direct path but only the name of the desired operator, e.g.

    --crossover subtree

instead of

    --crossover operators.crossover.subtree

However, it is still possible to specify the full correct path if you so desire. Specifying the full direct path allows you to create new operators and place them wherever you like.


#Population Options
-------------------

There are a number of parameters within PonyGE2 for controlling both overall populations and the individuals within those populations.

##Population Size

The population size controls the total number of individuals to be generated at each generation. The default value is 500. This value can be changed with the flag:

    --population_size [INT]

or by setting the parameter `POPULATION_SIZE` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the population size. 

Higher population sizes can improve performance on difficult problems, but require more computational effort and may lead to premature convergence.

##Generations

The number of generations the evolutionary algorithm will run for. The default value is 50. This value can be changed with the flag:

    --generations [INT]

or by setting the parameter `GENERATIONS` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the number of generations.

Higher numbers of generations can improve performance, but will lead to longer run-times.

*__NOTE__ that in PonyGE2 the total number of generations refers to the number of generations over which evolution occurs, __NOT__ including initialisation. Thus, specifying 50 generations will mean 50 generations will be evolved. Since the initialised generation will be Generation 0, the total number of individuals evaluated across an entire evolutionary run will by __population x (generations + 1)__.*

##Individual Size

There are a number of parameters for controlling the size and various aspects of individuals. 

###Linear Genome Parameters

There are a number of aspects to a linear genome:

1. the individual codons that make up that genome,
2. the total length of the genome, and
3. the number of times the mapping process will wrap across the genome.

####Codon Size

Each codon in a genome is an integer value. When generating a codon to represent a production choice, a random integer value is chosen that represents that correct production choice. The maximum value a codon can take is set by default at 10000. This value can be changed with the flag:

    --codon_size [INT]
    
or by setting the parameter `CODON_SIZE` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the maximum value a codon can take.

####Genome Length Limits

The total length of a genome is a global parameter that is often used for controlling genetic bloat. If left unchecked, it is possible for the evolutionary process in GE to generated extremely long genomes if variable length linear crossover operators are used. As such, provision is made in PonyGE2 for a global length limit for genomes. If specified, this limit will prevent crossover from generating individuals whose genomes violate this length limit. The default value is set to `None`, i.e. there is no length limit on linear genomes by default. This limit can be specified with the flag:
 
     --max_genome_length [INT]
 
or by setting the parameter `MAX_GENOME_LENGTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the maximum length a genome can take.

####Wrapping

TODO: Explain wrapping here. Cite wrapping paper.

###Derivation Tree Parameters

#Initialisation
--------------

There are two main ways to initialise a GE individual: by generating a genome, or by generating a derivation tree. Generation of a genome can only be done by creating a random genome string, and as such the use of genome initialisation cannot guarantee control over any aspects of the initial population. Population initialisation via derivation tree generation on the other hand allows for fine control over many aspects of the initial population, e.g. depth limits. Unlike with genome initialisation,there are a number of different ways to initialise a population using derivation trees. Currently implemented methods are detailed below. 

##Genome

###Random

To generate individuals from initialised genomes, the only option currently implemented is to generate random genome strings.

Activate with:

    --initialisation uniform_genome

or by setting the parameter `INITIALISATION` in either a parameters file or in the params dictionary.

By default in PonyGE2, genomes of length 200 codons are generated when using random genome initialisation. However, this parameter can be changed using the flag:

    --init_genome_length [INT]

or by setting the parameter `INIT_GENOME_LENGTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the length of genomes to be initialised.

*__NOTE__ that random genome initialisation in Grammatical Evolution should be used with caution as poor grammar design can have a negative impact on the quality of randomly initialised solutions due to the inherent bias capabilities of GE [Fagan et al., 2016; Nicolau & Fenton, 2016].*

##Derivation Tree

There are currently three options provided in PonyGE2 for initialising a population of individuals using derivation tree methods. You can either initialise a population of random derivation trees, or you can use various "smart" initialisation methods implemented here.

###Random

Random derivation tree initialisation generates individuals by randomly building derivation trees up to the specified maximum initialisation depth limit.

Activate with:

    --initialisation uniform_tree

or by setting the parameter `INITIALISATION` in either a parameters file or in the params dictionary.

*__NOTE__ that there is no obligation that randomly generated derivation trees will extend to the depth limit; they will be of random size [Fagan et al., 2016].*

*__NOTE__ that randomly generated derivation trees will have a tendency towards smaller tree sizes [Fagan et al., 2016].*

###Ramped Half-Half

Ramped Half-Half initialisation in Grammatical Evolution is often called "Sensible Initialisation" [Ryan and Azad, 2003]. Sensible Initialisation follows traditional GP Ramped Half-Half initialisation by initialising a population of individuals using two separate methods: `Full` and `Grow`.

`Full` initialisation generates a derivation tree where all branches extend to the specified depth limit. This tends to generate very bushy, evenly balanced trees [Fagan *et al.*, 2016].

`Grow` initialisation generates a randomly built derivation tree where no branch extends *past* the depth limit.

*__NOTE__ that `Grow` is analogous to random derivation tree initialisation, i.e. no branch in the tree is __forced__ to reach the specified depth.*

Activate with:

    --initialisation rhh

or by setting the parameter `INITIALISATION` in either a parameters file or in the params dictionary.

RHH initialisation generates pairs of solutions using both `full` and `grow` methods for a ramped range of depths. The maximum initialisation depth is set with the flag:

    --max_init_tree_depth [INT]

or by setting the parameter `MAX_INIT_TREE_DEPTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the maximum depth to which derivation trees are to be initialised. The default value is set at 10.

By default in PonyGE, initialisation ramping _begins_ at a depth where sufficient unique solutions can be generated for the number of required solutions at that depth [Nicolau & Fenton, 2016]. However, this value can be over-written in favor of a user-defined minimum ramping depth. This can be set with the flag:

    --min_init_tree_depth [INT]

or by setting the parameter `MIN_INIT_TREE_DEPTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the minimum depth from which derivation trees are to be initialised.

###Position Independent Grow (PI Grow)

Position Independent Grow (PI Grow) initialisation in Grammatical Evolution mirrors Sensible/Ramped Half-Half initialisation by initialising a population of individuals over a ramped range of depths. However, while RHH uses two separate methods `Full` and `Grow` to generate pairs of individuals at each depth, PI Grow eschews the `Full` component and only uses the `Grow` aspect. There are two further differences between traditional GP `Grow` and PI Grow [Fagan et al., 2016]:

1. At least one branch of the derivation tree is forced to the specified maximum depth in PI Grow, and
2. Non-terminals are expanded in random (i.e. position independent) order rather than the left-first derivation of traditional mappers. 

Activate with:

    --initialisation PI_grow

or by setting the parameter `INITIALISATION` in either a parameters file or in the params dictionary.

As with RHH initialisation, PI Grow initialisation generates individuals for a ramped range of depths. The maximum initialisation depth is set with the flag:

    --max_init_tree_depth [INT]

or by setting the parameter `MAX_INIT_TREE_DEPTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the maximum depth to which derivation trees are to be initialised. The default value is set at 10.

By default in PonyGE, initialisation ramping _begins_ at a depth where sufficient unique solutions can be generated for the number of required solutions at that depth [Nicolau & Fenton, 2016]. However, this value can be over-written in favor of a user-defined minimum ramping depth. This can be set with the flag:

    --min_init_tree_depth [INT]

or by setting the parameter `MIN_INIT_TREE_DEPTH` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the minimum depth from which derivation trees are to be initialised.

#Selection
---------

The selection process is a key step in Evolutionary Algorithms.

The mapping process in Grammatical Evolution can generate "invalid" individuals. Only valid individuals are selected by default. However, this can be changed with the flag:

    --invalid_selection

or by setting the parameter `INVALID_SELECTION` in either a parameters file or in the params dictionary.

##Tournament

Tournament selection selects `TOURNAMENT_SIZE` individuals from the overall population, sorts them, and then returns the single individual with the best fitness. Since no individuals are removed from the original population, it is possible that the same individuals may be selected multiple times to appear in multiple tournaments, although the same individual may not appear multiple times _in the same tournament_.

Activate with:

    --selection tournament

or by setting the parameter `SELECTION` in either a parameters file or in the params dictionary.

Tournament size is set by default at 2. This value can be changed with the flag:

    --tournament_size [INT]

or by setting the parameter `TOURNAMENT_SIZE` in either a parameters file or in the params dictionary, where `[INT]` is an integer which specifies the tournament size.

##Truncation

Truncation selection takes an entire population, sorts it, and returns the best `SELECTION_PROPORTION` of that population.  

Activate with:

    --selection truncation

or by setting the parameter `SELECTION` in either a parameters file or in the params dictionary.

Selection proportion is set by default at 0.5 (i.e. return the top 50% of the population). This value can be changed with the flag:

    --selection_proportion [NUM]

or by setting the parameter `SELECTION_PROPORTION` in either a parameters file or in the params dictionary, where `[NUM]` is a float between 0 and 1.

*__NOTE__ that unless the specified* `SELECTION_PROPORTION` *is 1 (i.e. 100%), truncation selection necessarily returns a selected parent population that is smaller in size than the original population.*

#Variation
---------

##Crossover

Crossover directly swaps genetic material between two chosen individuals. The
probability of crossover occurring is set with the flag:

    "--crossover_probability [NUM]

where `[NUM]` is a float between 0 and 1. The default value for crossover is
0.75.

###Fixed Onepoint

Activate with:

    --crossover fixed_onepoint

Given two individuals, create two children using fixed one-point crossover and return
them. The same point is selected on both genomes for crossover to occur.
This means that genomes will always remain the same length (as long as 
int_flip mutation is used). Crossover points are selected within the 
used portion of the genome by default (i.e. crossover does not occur in 
the tail of the individual).

###Fixed Twopoint

Activate with:

    --crossover fixed_twopoint

Given two individuals, create two children using fixed two-point crossover and return
them. The same points are selected on both genomes for crossover to occur.
This means that genomes will always remain the same length (as long as 
int_flip mutation is used). Crossover points are selected within the 
used portion of the genome by default (i.e. crossover does not occur in 
the tail of the individual).

###Variable Onepoint

Activate with:

    --crossover variable_onepoint

Given two individuals, create two children using variable one-point 
crossover and return them. A different point is selected on each genome 
for crossover to occur. This allows genomes to grow or shrink in length.
Crossover points areselected within the used portion of the genome by 
default (i.e. crossover does not occur in the tail of the individual).

*__NOTE__ that variable onepoint crossover can cause individuals to grow*
*, leading to bloat.*

###Variable Twopoint

Activate with:

    --crossover variable_twopoint

Given two individuals, create two children using variable two-point 
crossover and return them. Two different points are selected on each genome 
for crossover to occur. This allows genomes to grow or shrink in length.
Crossover points are selected within the used portion of the genome by 
default (i.e. crossover does not occur in the tail of the individual).

*__NOTE__ that variable onepoint crossover can cause individuals to grow*
*, leading to bloat.*

For a more in-depth discussion on crossover in Grammatical Evolution,
see [O'Neill *et al.*, 2003].

###Subtree

Activate with:

    --crossover subtree

Given two individuals, create two children using subtree crossover and
return them. Candidate subtrees are selected based on matching non-terminal
nodes rather than matching terminal nodes.

##Mutation

The ability to specify the number of mutation events per individual is
provided. This works for both genome mutation and subtree mutation. The
default number of mutation events is 1 per individual. This value can be
changed with the flag:

    --mutation_events [INT]

where `[INT]` is an integer which specifies the number of mutation events per
individual. Note that for subtree mutation exactly this number of mutation
events will occur, but for integer flip mutation this will only affect the
probability of mutation events occurring.

###Int Flip

Activate with:

    --mutation int_flip

Default mutation probability is 1 over the length of the genome. This can be
changed with the flag:

    --mutation_probability [NUM]

where `[NUM]` is a float between 0 and 1. This will change the mutation
probability for each codon to the probability specified. Mutation is
performed over the entire length of the genome by default, but the flag
within_used is provided to limit mutation to only the effective length of
the genome.

###Subtree

Activate with:

    --mutation subtree

Mutate the individual by replacing a randomly selected subtree with a new
randomly generated subtree. Guaranteed one event per individual, unless
`params['MUTATION_EVENTS']` is specified as a higher number.

#Evaluation
----------

##Multicore evaluation

Evaluation of a population of individuals can be done in series (single core
evaluation) or in parallel (multi core evaluation). Multicore evaluation can
be activated with the flag:

    --multicore

Additionally, the number of processor cores used for multicore evaluation
can be controlled with the flag:

    --cores [INT]

where `[INT]` is an integer which specifies the number of cores used for
fitness evaluations. The default value is to use all available cores.

*__NOTE__ that multicore evaluations may not necessarily improve computational*
*runtime for small problems as a certain overhead is necessary to run the*
*multicore evaluation process.*

*__NOTE__ also that for smaller problems fitness evaluations may not*
*necessarily present a bottleneck in terms of computational run-time. It is*
*advised to use a python profiler to ascertain whether or not fitness*
*evaluations present such a bottleneck. If this is the case, multicore*
*evaluation  may improve the run-time of a single evolutionary run.*

*__NOTE__ also that when running batches of multiple experiments, it will*
*__always__ be faster to run multiple single-core experiments in parallel,*
*rather than multiple multi-core experiments in series.*

##Caching

Caching is provided in PonyGE2 to save on fitness evaluations and to track the
number of unique solutions encountered during an evolutionary run. Cached
individuals have their fitness stored in a dictionary called
`utilities.trackers.cache`. Dictionary keys are the string of the phenotype.
Caching can be activated with the flag:

    --cache

There are currently three options for use with the cache:

###1. Fitness Lookup

This is the default case when caching is activated. Individuals which have
already been evaluated have their previous fitness read directly from the
cache, thus saving fitness evaluations. Fitness lookup can be
de-activated with:

    --dont_lookup_fitness

###2. Fitness Penalty

Individuals which have already been evaluated are given a default bad
fitness. Activate with:

    --lookup_bad_fitness

###3. Mutate Duplicates

Individuals which have already been evaluated are mutated to produce new
unique individuals which have not been encountered yet by the search process.
Activate with:

    --mutate_duplicates

*__NOTE__ that the various caching options are __mutually exclusive__.*
*For example, you cannot specify* `--mutate_duplicates` *with* `--lookup_bad_fitness`.

#Replacement
-----------

##Generational

Activate with:

    --replacement generational

Elites can be saved between generations. The default number of elites is 1
percent of the population size. This value can be changed with the flag:

    --elite_size [INT]

where `[INT]` is an integer which specifies the number of elites to be saved
between generations. Elites are saved between generations regardless of
whether or not they are better or worse than the new population.

##Steady State

Activate with:

    --replacement steady_state

#Grammars
---------

##Writing Grammars

Grammars are written in Backus-Naur form, aka BNF. See the examples in
grammars. Each rule is composed of a left-hand side (a single
non-terminal), followed by the "goes-to" symbol `::=`, followed by a
list of productions separated by the "or" symbol `|`. Non-terminals
are enclosed by angle brackets `<>`. For example:

    <a> ::= <b>c | d

You can use an "or" symbol or angle bracket in a production. Escape it
using a backslash: `\|, \<, \>`. You can use the "goes-to" symbol in a
production without escaping it.

A useful special case is available when writing grammars: a production
can be given as `GE_RANGE:4`, for example, and this will be replaced
by a set of productions: `0 | 1 | 2 | 3`. With
`GE_RANGE:dataset_n_vars`, the number of productions will be set by
the number of columns in the file given by the `--dataset` argument,
if any. Using grammar productions like the following, we can avoid
hard-coding the number of independent variables in the grammar:

```
<var> ::= x[<varidx>]
<varidx> ::= GE_RANGE:dataset_n_vars
```

See `grammars/supervised_learning.bnf` for a full example.

Along with the fitness function, grammars are one of the most problem-specific
components of the PonyGE2 algorithm. The performance of PonyGE2 can be vastly
affected by the quality of the grammar used.

All grammars are stored in the grammars folder. Grammars can be set
with the flag:

    --grammar_file [FILE_NAME.bnf]

*__NOTE__ that the full file extension (e.g. ".bnf") must be specified.*

*__NOTE__ that the full file path __does not__ need to be specified.*


##Parsing Grammars

Grammars are parsed using regular expressions.

You can have:
- production separators in multiple lines
- comments at the end of any line
- single quotation within double quotation and vice versa
- any characters can be used in quotation, even separators '|'

Additionally, the code becomes more readable as well as maintainable and 
it is not as error prone.

Examples on parsing some of grammars can be found here:
- [Whole grammar](https://regex101.com/r/oY2dK0/3)
- [Rule](https://regex101.com/r/rU9tA7/2)
- [Production](https://regex101.com/r/sE7eM8/1)


##A note on unit productions.

Traditionally GE would not consume a codon for unit productions. This was a
design decision taken by O'Neill et al. In PonyGE2 unit productions consume
codons. The logic being that it helps to do linear tree-style operations.
Furthermore, the checks needed for unit productions during the running of the
algorithm can add up to millions of checks that aren't needed if we just
consume codons for unit productions.

The original design decision on unit productions was also taken before the
introduction of evolvable grammars whereby the arity of a unit production
could change over time. In this case consuming codons will help to limit the
ripple effect from that change in arity. This also replicates non coding
regions of genome as seen in nature.

In summary, the merits for not consuming a codon for unit productions are not
clearly defined in the literature. The benefits in consuming codons are a
reduction in computation and improved speed with linear tree style operations.
Other benefits are an increase in non-coding regions in the chromosome (more
in line with nature) that through evolution of the grammar may then express
useful information.


#Example Problems
----------------

######FIXME Need to finalise a suite of problems for PonyGE2

Four example problems are currently provided:

1. String-match
2. Regression
3. Classification
4. Integer sequence match

A brief description is given below of each problem, along with the 
command-line arguments necessary to call each problem.

*__NOTE__ that it is necessary to specify the desired grammar for each* 
*problem. This can either be done with a unique parameters config file*
*or by passing the command-line argument in.*


##String-match
------------

The grammar specifies words as lists of vowels and consonants. The aim
is to match a target word.

To use it, specify the following command-line arguments:

    --fitness_function string_match
    --target [TYPE_TARGET_STRING]

e.g. `--target golden, --target ponyge_rocks`

Alternatively, you can specify a direct parameters file with:

    --parameters string_match.txt

##Regression
----------

The grammar generates a symbolic function composed of standard mathematical
operations and a set of variables. This function is then evaluated using a
pre-defined set of inputs, given in the datasets folder. Each problem suite has
a unique set of inputs. The aim is to minimise some error between the expected
output of the function and the desired output specified in the datasets.
This is the default problem for PonyGE.

To use it, specify the following command-line arguments:

    --fitness_function regression
    --dataset [PROBLEM_SUITE]

e.g. `--dataset Keijzer6, --dataset Vladislavleva4`

Alternatively, you can specify a direct parameters file with:

    --parameters regression.txt

##Classification
--------------

Classification can be considered a special case of symbolic regression but
with a different error metric. Like with regression, the grammar generates a
symbolic function composed of standard mathematical operations and a set of
variables. This function is then evaluated using a pre-defined set of inputs,
given in the datasets folder. Each problem suite has a unique set of inputs.
The aim is to minimise some classification error between the expected
output of the function and the desired output specified in the datasets.

To use it, specify the following command-line arguments:

    --fitness_function classification
    --dataset [PROBLEM_SUITE]

e.g. `--dataset Banknote`

Alternatively, you can specify a direct parameters file with:

    --parameters classification.txt


##Integer sequence match
------------------------

In the sequence-match problem, we're given an integer sequence target,
say [0, 5, 0, 5, 0, 5], and we try to synthesize a program (loops,
if-statements, etc) which will *yield* that sequence, one item at a
time. There are several components to the provided fitness function,
which are weighted by numerical parameters. We can specify the target
sequence and weights using parameters on the command line or in a
parameters file.

To try this problem, use command-line arguments similar to the following:

    --fitness_function sequence_match
	--grammar_file sequence_match.pybnf
	--target "[0, 5, 0, 5, 0, 5]"
	--extra_fitness_parameters "alpha=0.5, beta=0.5, gamma=0.5"
	

#Adding New Problems
--------------------

It has been made as simple as possible to add problems to PonyGE. Everything
is automated, and there is only one place where code __may__ need to be
edited in order to enable a new problem (apart from adding in the problem
itself, obviously). The flipside of this is that it is possible to easily
mis-configure PonyGE if you fail to specify everything correctly.

_**NOTE** that this can be remedied somewhat with proper use of the new parameter_
_config files._

**To add in a new problem:**
You simply need to write a **new fitness function** (if you don't want to use
one already there) and add a **new grammar file**. You may also need to add a
**new dataset** if you're using datasets.

_**NOTE** that it may be beneficial to create a **new paremeters file**_
_for any new problem._

##Fitness Functions

Fitness functions can be specified from the command line with the flag:

    --fitness_function [FIT_FUNC_NAME]

where `[FIT_FUNC_NAME]` is the name of the fitness function class.

*__NOTE__ that fitness functions __must__ be a class with the same name as the*
*file containing the class, e.g.* `fitness.regression.regression`.

*__NOTE__ that any regression-style problems that include training and test*
*data __require__ a* `self.training_test = True` *attribute in the init*
*function for your fitness function class in order for PonyGE to generate*
*training and test fitnesses for your solutions.*

##Grammar Files

Grammar files can be specified from the command line with the flag:

    --grammar_file [GRAMMAR_FILE]

where `[GRAMMAR_FILE]` is the name of the grammar file.

*__NOTE__ that when specifying the grammar file you __must__ specify the full*
*file extension, e.g. "Keijzer6.bnf".*

*__NOTE__ that you __do not need__ to specify the file path, e.g.*
*"grammars/Keijzer6.bnf."*

##Datasets

Datasets can be specified from the command line with the flag:

    --dataset [DATASET]

where `[DATASET]` is the name of the dataset.

*__NOTE__ that when specifying the dataset you __do not__ need to specify the*
*file path or the file extension.*

##Parameters files

Instead of passing in requirements from the command line, all three
requirements specified above can be set in a unique parameters file. Then,
only one flag needs to be passed in:

    --parameters [PARAMETERS_FILE]

where `[PARAMETERS_FILE]` is the name of the desired parameters file.

*__NOTE__ that when specifying the parameters file you __must__ specify the*
*full file extension, e.g. "classification.txt".*

*__NOTE__ that you __do not__ need to specify the full file path to the*
*parameters file.*

##Editing Code to enable new problems

Finally, depending on the problem itself you may need to edit
`representation.individual.Individual.evaluate` to fully integrate the new
problem to PonyGE. `individual.evaluate` is where PonyGE specifies the inputs
needed for fitness evaluation.

*__NOTE__ that it may not be necessary to edit `individual.evaluate` if you*
*only pass in the phenotype to be evaluated.*


#Post-run Analysis
-----------------

We don't provide any experiment managers other than the ability to save runs
to specific folders using the `--experiment_name` handle. However, there are a
number of functions available in `utilities.save_plots` which allow for
plotting of run statistics.


##Post-run Analysis - Single Runs
-------------------------------

By default, runs save a plot of best fitness (unless `--debug` is specified).
Additionally, users can save plots from pre-existing stats.tsv files (i.e.
stats files generated upon completion of a run) using:

    utilities.save_plot.save_plot_from_file(file_name, stat_name)

where:

file_name = "./results/folder_name/stats.tsv" (the full file path to the file)
stat_name = a valid key from the `stats.stats.stats` dictionary.

This will generate a plot of the given stat and save it in the same location as
the original stats file.


Alternatively, users can directly pass data in to:

    utilities.save_plot.save_plot_from_data(stat_data, stat_name)

where:

stat_data = some list of data, i.e. `[data[stat_name] for data in
utilities.trackers.stats_list]`
stat_name = a valid key from the `stats.stats.stats` dictionary.


##Post-run Analysis - Multiple Runs
---------------------------------

If multiple runs are saved in a folder using the `--experiment_name` handle, a
file is given for generating plots of the average stat values across these
multiple runs, as given by:

    stats.parse_stats.py

There are a number of flags that must be used for passing values via the
command-line. To see a full list of these just run the following

    $ python stats/parse_stats.py --help


#References
----------

Michael O'Neill and Conor Ryan, "Grammatical Evolution: Evolutionary
Automatic Programming in an Arbitrary Language", Kluwer Academic
Publishers, 2003.

Michael O'Neill, Erik Hemberg, Conor Gilligan, Elliott Bartley, and
James McDermott, "GEVA: Grammatical Evolution in Java", ACM
SIGEVOlution, 2008. http://portal.acm.org/citation.cfm?id=1527066. Get
GEVA: http://ncra.ucd.ie/Site/GEVA.html

O'Neill, M., Ryan, C., Keijzer, M. and Cattolico, M., 2003. "Crossover in
grammatical evolution." Genetic programming and evolvable machines, 4(1),
pp.67-93. DOI: 10.1023/A:1021877127167

Ryan, C. and Azad, R.M.A., 2003. "Sensible initialisation in grammatical 
evolution." In Proceedings of the Bird of a Feather Workshops, Genetic 
and Evolutionary Computation Conference (GECCO 2003), pp. 142-145.

Fagan, D., Fenton, M. and O'Neill, M., 2016. "Exploring Position Independent 
Initialisation in Grammatical Evolution." IEEE Congress on Evolutionary 
Computation, Vancouver, Canada. IEEE Press.

Nicolau, M. and Fenton, M., 2016. "Managing Repitition in Grammar-based 
Genetic Programming." ACM GECCO 2016 Proceedings of the Genetic and 
Evolutionary Computation Conference, Denver, Colorado, USA.

Byrne, J., O'Neill, M. and Brabazon, A., 2009, "Structural and nodal mutation in grammatical evolution." In Proceedings of the 11th Annual conference on Genetic and evolutionary computation (pp. 1881-1882). ACM.