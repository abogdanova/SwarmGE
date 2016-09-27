------------
Introduction
------------

Grammatical evolution (GE) is a population-based evolutionary algorithm, where
a formal BNF-style grammar is used in the genotype to phenotype mapping
process.

PonyGE2 is an implementation of GE in Python. It's intended as an advertisement
and a starting-point for those new to GE, a reference for students and
researchers, a rapid-prototyping medium for our own experiments, and as a
Python workout.

The original version of PonyGE (https://github.com/jmmcd/ponyge) was originally
designed to be a small single-file implementation of GE. However, over time
this has grown to a stage where a more formal structured approach was needed.
This has led to the development of PonyGE2 (https://github.com/jmmcd/ponyge2),
presented here.

The PonyGE2 development team can be contacted at:

    James McDermott <jamesmichaelmcdermott@gmail.com>,
    Erik Hemberg <erik.hemberg@gmail.com>,
    Michael Fenton <michaelfenton1@gmail.com>,
    David Fagan <fagan.david@gmail.com>.

PonyGE2 is copyright (C) 2009-2016


------------
Requirements
------------

PonyGE runs under Python 3.x.
Using matplotlib, numpy, scipy, scikit-learn (sklearn), pandas

All requirements can be satisfied with Anaconda.


--------------
Running PonyGE
--------------

We don't provide any setup script. You can run an example problem (the default
is regression, see below) just by typing:

$ cd src
$ python ponyge.py

This will run an example problem and generate a results folder. The folder
contains several files showing the run's stats, producing graphs and
documenting the parameters used, as well as a file containing the best
individuals. For a more verbose command line experience run the following:

$ cd src
$ python ponyge.py --verbose

Each line of the output corresponds to a generation in the evolution, and
prints out all statistics on the current run (only if --verbose is specified).
Upon completion of a run, the best individual is printed to the command line,
along with summary statistics.

There are a number of flags that can be used for passing values via the
command-line. To see a full list of these just run the following:

$ python ponyge.py --help


-------------
About PonyGE2
-------------

#TODO: Fill out this section heftily.

A full breakdown of the currently implemented elements in PonyGE2 is provided
below. This includes a brief description of each individual component and how
to activate them. PonyGE2 automatically parses the correct path for all
operators, meaning you don't have to specify the full direct path but only
the name of the desired operator, e.g. "--crossover subtree" instead of
"--crossover operators.crossover.subtree". However, it is still possible to
specify the full correct path if you so desire. Specifying the full direct path
allows you to create new operators and place them wherever you like.

Evolutionary Parameters:

    - Population Size
      ---------------
        The size of the population. The default value is 500. This value can
        be changed with the flag:

        "--population_size [INT]"

        where [INT] is an integer which specifies the population size.
        Higher population sizes can improve performance on difficult
        problems, but require more computational effort and may lead to
        premature convergence.

    - Generations
      -----------
        The number of generations the evolutionary algorithm will run for.
        The default value is 50. This value can be changed with the flag:

        "--generations [INT]"

        where [INT] is an integer which specifies the number of generations.
        Higher numbers of generations can improve performance, but will lead
        to longer run-times.

The typical breakdown of a population-based evolutionary algorithm is:

    Initialisation
    Selection
    Variation
    Evaluation
    Replacement

These steps are expanded on in detail hereafter.

    - Initialisation
      --------------
        There are two main ways to initialise a GE individual: by generating a
        genome, or by generating a subtree. Generation of a genome can only be
        done by creating a random genome string and as such individuals cannot
        be controlled. Subtree generation on the other hand can be forced to
        conform to specified limits, e.g. depth limits. This is implemented in
        ramped half-half initialisation (also called Sensible initialisation).
        It is also possible to initialise a population using randomly generated
        subtrees, which is similar in theory to random genome initialisation
        except there is far less bias than random genome initialisation as a
        result of the number of production choices in the grammar.

        - Genome
            - Random
                Activate with "--genome_init"
        - Subtree
            - Random
                Activate with "--initialisation random_init"
            - Ramped Half-Half
                Activate with "--initialisation rhh"

    - Selection
      ---------
        Only valid individuals are selected by default. However, this can be
        changed with the flag:

        "--invalid_selection"

        - Tournament
            Activate with "--selection tournament"

            Tournament size is set by default at 2. This value can be changed
            with the flag:

            "--tournament_size [INT]"

            where [INT] is an integer which specifies the tournament size.
        - Truncation
            Activate with "--selection truncation"

            Selection proportion is set by default at 0.5. This value can be
            changed with the flag:

            "--selection_proportion [NUM]"

            where [NUM] is a float between 0 and 1.

    - Variation
      ---------
        - Crossover
            - Onepoint
                Activate with "--crossover onepoint"
            - Subtree
                Activate with "--crossover subtree"
        - Mutation
            The ability to specify the number of mutation events per
            individual is provided. This works for both genome mutation and
            subtree mutation. The default number of mutation events is 1 per
            individual. This value can be changed with the flag:

            "--mutation_events [INT]"

            where [INT] is an integer which specifies the number of mutation
            events per individual. Note that for subtree mutation exactly
            this number of mutation events will occur, but for integer flip
            mutation this will only affect the probability of mutation
            events occurring.

            - Int Flip
                Activate with "--mutation int_flip"

                Default mutation probability is 1 over the length of the
                genome. This can be changed with the flag:

                "--mutation_probability [NUM]"

                where [NUM] is a float between 0 and 1. This will change
                the mutation probability for each codon to the probability
                specified.
            - Subtree
                Activate with "--mutation subtree"

    - Evaluation
      ----------

    - Replacement
      -----------
        - Generational
            Activate with "--replacement generational"

            Elites can be saved between generations. The default number of
            elites is 1 percent of the population size. This value can be
            changed with the flag:

            "--elite_size [INT]"

            where [INT] is an integer which specifies the number of elites
            to be saved between generations. Elites are saved between
            generations regardless of whether or not they are better or worse
            than the new population.
        - Steady State
            Activate with "--replacement steady_state"


Writing grammars
----------------

Grammars are written in Backus-Naur form, aka BNF. See the examples in
src/grammars. Each rule is composed of a left-hand side (a single
non-terminal), followed by the "goes-to" symbol ::=, followed by a
list of productions separated by the "or" symbol |. Non-terminals are
enclosed by angle brackets <>. For example:

<a> ::= <b>c | d

You can use an "or" symbol or angle bracket in a production. Escape it
using a backslash: \|, \<, \>. You can use the "goes-to" symbol in a
production without escaping it.

Along with the fitness function, grammars are one of the most problem-specific
components of the PonyGE2 algorithm. The performance of PonyGE2 can be vastly
affected by the quality of the grammar used.


A note on unit productions
--------------------------

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


#FIXME Need to finalise a suite of problems for PonyGE2
----------------
Example Problems
----------------

Three example problems are currently provided:

    - String-match
    - Regression
    - Classification

A brief description is given below of each problem, along with the command-line
arguments necessary to call each problem. It is not necessary to specify the
desired grammar for each individual problem as PonyGE does this automatically
based on the given inputs.


String-match
------------

The grammar specifies words as lists of vowels and consonants. The aim
is to match a target word.

To use it, specify the following command-line arguments:

    "--problem string_match"
    "--target_string [TYPE_TARGET_STRING]"
        e.g. --target_string golden, --target_string ponyge_rocks


Regression
----------

The grammar generates a symbolic function composed of standard mathematical
operations and a set of variables. This function is then evaluated using a
pre-defined set of inputs, given in the datasets folder. Each problem suite has
a unique set of inputs. The aim is to minimise some error between the expected
output of the function and the desired output specified in the datasets.
This is the default problem for PonyGE.

To use it, specify the following command-line arguments:

    "--problem regression"
    "--problem_suite [PROBLEM_SUITE]"
        e.g. --problem_suite Keijzer6, --problem_suite Vladislavleva4


Classification
--------------

#TODO Explain classificaiton problem here


-----------------
Post-run Analysis
-----------------

We don't provide any experiment managers other than the ability to save runs
to specific folders using the --experiment_name handle. However, there are a
number of functions available in utilities.save_plots which allow for plotting
of run statistics.


Post-run Analysis - Single Runs
-------------------------------

By default, runs save a plot of best fitness (unless --debug is specified).
Additionally, users can save plots from pre-existing stats.tsv files (i.e.
stats files generated upon completion of a run) using:

    utilities.save_plot.save_plot_from_file(file_name, stat_name)

where:

    file_name = "./results/folder_name/stats.tsv" (the full file path to the
                file)
    stat_name = a valid key from the stats.stats.stats dictionary.

This will generate a plot of the given stat and save it in the same location as
the original stats file.


Alternatively, users can directly pass data in to:

    utilities.save_plot.save_plot_from_data(stat_data, stat_name)

where:

    stat_data = some list of data, i.e. [data[stat_name] for data in
                                         utilities.trackers.stats_list]
    stat_name = a valid key from the stats.stats.stats dictionary.


Post-run Analysis - Multiple Runs
---------------------------------

If multiple runs are saved in a folder using the --experiment_name handle, a
file is given for generating plots of the average stat values across these
multiple runs, as given by:

    stats.parse_stats.py

There are a number of flags that must be used for passing values via
the command-line. To see a full list of these just run the following

$ python stats/parse_stats.py --help

----------
References
----------

Michael O'Neill and Conor Ryan, "Grammatical Evolution: Evolutionary
Automatic Programming in an Arbitrary Language", Kluwer Academic
Publishers, 2003.

Michael O'Neill, Erik Hemberg, Conor Gilligan, Elliott Bartley, and
James McDermott, "GEVA: Grammatical Evolution in Java", ACM
SIGEVOlution, 2008. http://portal.acm.org/citation.cfm?id=1527066. Get
GEVA: http://ncra.ucd.ie/Site/GEVA.html