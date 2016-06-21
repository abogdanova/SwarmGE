Grammatical evolution (GE) is an evolutionary algorithm which uses
formal grammars, written in BNF, to define the search space. PonyGE2 is
an implementation of GE in Python. It's intended as
an advertisement and a starting-point for those new to GE, a reference
for implementors and researchers, a rapid-prototyping medium for our
own experiments, and a Python workout.

PonyGE (https://github.com/jmmcd/ponyge) was originally designed to be
a small single file implementation of GE however over time this has
grown to a stage where a more formal structured approach was needed.

PonyGE2 is copyright (C) 2009-2016
Erik Hemberg <erik.hemberg@gmail.com>,
James McDermott <jamesmichaelmcdermott@gmail.com>,
David Fagan <fagan.david@gmail.com>,
Michael Fenton <michaelfenton1@gmail.com>.

Requirements
------------

PonyGE runs under Python 3.x.
Using matplotlib, numpy and scipy

Running PonyGE
--------------

We don't provide any setup script. You can run an example problem (the
default is String-match, see below) just by saying:

$ cd src
$ python ponyge.py

This will run an example problem and generate a results folder. The folder
contains several files showing the runs stats, producing graphs and
documenting the parameters used, aswell as a file containing the best
individuals. For a more verbose command line experience run the following

$ cd src
$ python ponyge.py --verbose

Each line of the output corresponds to a generation in the evolution, and prints
out all statistics on the current run (if --verbose is specified). Upon
completion of a run, the best individual is printed to the command line, along
with summary statistics.

There are a number of flags that can be used for passing values via
the command-line. To see a full list of these just run the following

$ python ponyge.py --help


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

#FIXME Need to finalise a suite of problems for PonyGE2
Example Problems
----------------


String-match
------------

The grammar specifies words as lists of vowels and consonants. The aim
is to match a target word. This is the default problem: as you can see
in ponyge.py, the necessary grammar and fitness function are specified
by default:

GRAMMAR_FILE, FITNESS_FUNCTION = "grammars/letter.bnf", \
StringMatch("golden")


Note on unit productions!!!!
------------------------------------

Traditionally GE would not consume a codon for unit productions. This
was a design decision taken by O'Neill et al. In PonyGE2 unit productions
consume codons. The logic being that it helps to do linear tree style
operations.

No only that but the checks needed for unit productions during
the running of the algorithm can add up to millions of checks that aren't
needed if we just consume codons for unit productions.

The original design decision on unit productions was also taken before the
introduction of evolvable grammars whereby the arity of a unit production
could change over time and in this case consuming codons will help to limit
the ripple effect from that change in arity. This also replicates non coding
regions of genome as seen in nature.

In summary, the merits for not consuming a codon for unit productions are
not clearly defined in the literature. The benifits in consuming codons are
a reduction in computation and improved speed with linear tree style operations.
Other benifits are an increase in non-coding regions in the chromosome
(more in line with nature) that through evolution of the grammar may then
express useful information.

Reference
---------

Michael O'Neill and Conor Ryan, "Grammatical Evolution: Evolutionary
Automatic Programming in an Arbitrary Language", Kluwer Academic
Publishers, 2003.

Michael O'Neill, Erik Hemberg, Conor Gilligan, Elliott Bartley, and
James McDermott, "GEVA: Grammatical Evolution in Java", ACM
SIGEVOlution, 2008. http://portal.acm.org/citation.cfm?id=1527066. Get
GEVA: http://ncra.ucd.ie/Site/GEVA.html