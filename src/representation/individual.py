from representation import tree
from algorithm.parameters import CODON_SIZE,FITNESS_FUNCTION,PROBLEM
from random import randint
from fitness.fitness import default_fitness

"""Need to migrate codon size to good location, maybe the grammar???"""

class individual(object):
    """A GE individual"""
    def __init__(self, genome, ind_tree, grammar, invalid=False, max_depth=20, chromosome=False, length=500):
        if (genome == None) and (ind_tree == None):
            if chromosome:
                self.genome = [randint(0, CODON_SIZE) for _ in range(length)]
                self.phenotype, self.used_codons, self.tree, self.nodes, self.invalid = tree.genome_init(grammar, self.genome)
            else:
                self.phenotype, genome, self.tree, self.nodes, self.invalid = tree.random_init(grammar, max_depth)
                self.used_codons = len(genome)
                self.genome = genome + [randint(0, grammar.codon_size) for i in range(self.used_codons)]
        else:
            self.genome = genome
            self.tree = ind_tree
            self.invalid = invalid
        self.fitness = default_fitness(FITNESS_FUNCTION.maximise)
        self.length = length

    def __lt__(self, other):
        if FITNESS_FUNCTION.maximise:
            return self.fitness < other.fitness
        else:
            return other.fitness < self.fitness

    def __str__(self):
        return ("Individual: " +
                str(self.phenotype) + "; " + str(self.fitness))

    def evaluate(self, fitness, dist="training"):
        """ Evaluates phenotype in fitness function on either training or test
        distributions and sets fitness"""
        #IF the problem is regression eg has training and test data
        if PROBLEM == "regression":
            self.fitness = fitness(self.phenotype, dist)
        else:
            self.fitness = fitness(self.phenotype)
       # print "\n", self.fitness, "\t", self.phenotype
