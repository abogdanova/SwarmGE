from fitness.fitness import default_fitness
from algorithm.parameters import params
from algorithm.mapper import genome_map
from operators import initialisers
from random import randint


class individual(object):
    """A GE individual"""

    def __init__(self, genome, ind_tree, invalid=False, max_depth=20):

        if (genome is None) and (ind_tree is None):
            # Need to randomly generate a new individual
            if params['GENOME_INIT']:
                self.genome = [randint(0, params['CODON_SIZE']) for _ in
                               range(params['GENOME_LENGTH'])]
                self.phenotype, genome, self.tree, self.nodes, \
                self.invalid, self.depth, \
                self.used_codons = initialisers.genome_init(self.genome)
                self.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
            else:
                self.phenotype, genome, self.tree, self.nodes, self.invalid, \
                self.depth, self.used_codons = initialisers.tree_init(max_depth,
                                                                      "random")
                self.genome = genome + [randint(0, params['CODON_SIZE']) for _
                                        in range(int(self.used_codons/2))]
                self.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)

        elif genome and (ind_tree is None):
            # Need to generate a tree
            self.genome = list(genome)
            if params['GENOME_OPERATIONS']:
                self.phenotype, genome, self.tree, self.nodes, self.invalid, \
                self.depth, self.used_codons = genome_map(genome)
            else:
                self.phenotype, genome, self.tree, self.nodes, self.invalid, \
                self.depth, self.used_codons = \
                    initialisers.genome_init(list(genome))

        elif ind_tree and (genome is None):
            # Need to generate a genome
            self.tree = ind_tree
            self.invalid = invalid
            genome = self.tree.build_genome([])
            self.used_codons = len(genome)
            self.genome = genome + [randint(0, params['CODON_SIZE']) for _ in
                                    range(int(self.used_codons/2))]
            self.phenotype = self.tree.get_output()
        else:
            self.genome = list(genome)
            self.tree = ind_tree
            self.invalid = invalid
            self.phenotype = self.tree.get_output()
        self.fitness = default_fitness(params['FITNESS_FUNCTION'].maximise)
        self.name = None

    def __lt__(self, other):
        if params['FITNESS_FUNCTION'].maximise:
            return self.fitness < other.fitness
        else:
            return other.fitness < self.fitness

    def __str__(self):
        return ("Individual: " +
                str(self.phenotype) + "; " + str(self.fitness))

    def evaluate(self, dist="training"):
        """ Evaluates phenotype in fitness function on either training or test
        distributions and sets fitness"""

        if params['PROBLEM'] in ("regression", "classification"):
            # The problem is regression, e.g. has training and test data
            self.fitness = params['FITNESS_FUNCTION'](self.phenotype, dist)
        else:
            self.fitness = params['FITNESS_FUNCTION'](self.phenotype)

        # print("\n", self.fitness, "\t", self.phenotype)
