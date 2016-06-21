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


Max
---

The grammar specifies legal ways of combining numbers using arithmetic
operations. The aim is to create the largest value possible. Use the
following grammar and fitness function (in ponyge.py):

GRAMMAR_FILE, FITNESS_FUNCTION = "grammars/arithmetic.pybnf", \
MaxFitness()

XOR
---

A small version of the standard genetic programming Even-N parity
benchmark. The grammar specifies two inputs, x and y, and allows them
to be combined using AND, OR, and NOT. The aim is to evolve the XOR
function. Use the following grammar and fitness function:

GRAMMAR_FILE, FITNESS_FUNCTION = "grammars/boolean.pybnf", \
XORFitness()

EvenNParity
-----------

A standard genetic programming benchmark. The grammar specifies a list
of N-inputs, and allows them to be combined using AND, OR, NOR and
NAND, reduce(), head() and tail(). The aim is to evolve a function
that outputs true if the parity of the inputs are even. Use the
following grammar and fitness function for N=3:

GRAMMAR_FILE, FITNESS_FUNCTION = "grammars/hofBoolean.pybnf", \
EvenNParityFitness(3)


L-System and P-system
---------------------

The most interesting examples. Run it like this (no need to make any
source code changes):

$ ./start-lsystem.sh

Or:

$ ./start-psystem.sh

You'll be presented with a GUI showing nine drawings in a 3x3 grid of
cells. You click on the ones you like, and click "Next" (or hit space)
to iterate the algorithm. The drawings are made using a custom
L-system or P-system whose possible forms are specified by the
grammar. The files gui.py, drawing.py, lsystem.py, psystem.py,
grammars/lsystem.bnf, grammars/psystem.bnf all belong to this example.


N-Player Iterated Prisoner's Dilemma
------------------------------------

The other most interesting example. The prisoner's dilemma
(en.wikipedia.org/wiki/Prisoner's_dilemma) is a well-known game where
two players must decide whether to cooperate or defect: each is
individually better off to defect, but if they both cooperate they do
better than if they both defect. In the iterated version the players
play against each other multiple times, so it makes sense for them to
establish cooperation. But in the N-player version, cooperation is
less likely to arise. In our implementation, players must choose among
four hard-coded strategies which may be dependent on previous rounds.
In the next version of PonyGE we will add the possibility of more
complex, fine-grained behaviours.

Run it like this, for a basic 2-player game (no need for source code
changes):

./ponyge.py -b grammars/nipd.pybnf -f \
"NPlayerIteratedPrisonersDilemmaFitness(100, 2, 50)" -p 10 -g 50 -e 0 \
-m 0.2

Here, 100 is the number of rounds to play in each game; 2 is the
number of players in each game, sampled randomly from population; 50
is the number of games to play in each generation (should be enough to
make sure every player in population plays often); 10 is the
population size (must be greater than number of players); 50 is the
number of generations; 0 is the elite size (zero here, because in this
coevolutionary setup a player's fitness depends on its opponents, so
players shouldn't keep their fitness from previous generations); and
0.2 is the mutation rate.

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
the ripple effect from that change in arity.

In summary, the merits for not consuming a codon for unit productions are
not defined. The benifits in consuming codons are a reduction in computation
and improved speed with linear tree style operations. The other benifits are
an increase in non-coding regions in the chromosome (more in line with nature)
that through evolution of the grammar may then express useful information.

Reference
---------

Michael O'Neill and Conor Ryan, "Grammatical Evolution: Evolutionary
Automatic Programming in an Arbitrary Language", Kluwer Academic
Publishers, 2003.

Michael O'Neill, Erik Hemberg, Conor Gilligan, Elliott Bartley, and
James McDermott, "GEVA: Grammatical Evolution in Java", ACM
SIGEVOlution, 2008. http://portal.acm.org/citation.cfm?id=1527066. Get
GEVA: http://ncra.ucd.ie/Site/GEVA.html