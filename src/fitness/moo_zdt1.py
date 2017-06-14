from math import sqrt

from fitness import moo_fitness


class moo_zdt1(moo_fitness.moo_fitness):

    """
    Fitness function for the first problem (T_1) presented in
    [Zitzler2000].
    
    .. Zitzler, Eckart, Kalyanmoy Deb, and Lothar Thiele. Comparison
    of multiobjective evolutionary algorithms: Empirical results.
    Evolutionary computation 8.2 (2000): 173-195.
    """

    def __init__(self):
        super().__init__()
    
        # Over-write default fitness to account for multiple objectives.
        moo_zdt1.default_fitness = [super().default_fitness,
                                    super().default_fitness]

    def moo_eval(self, phen):
        min_value = [0 for _ in range(30)]
        max_value = [1 for _ in range(30)]
        real_chromosome = binary_phen_to_float(phen, 30, min_value, max_value)

        summation = 0
        for i in range(1, len(real_chromosome)):
            summation += real_chromosome[i]

        g = 1 + 9 * summation / (len(real_chromosome) - 1.0)
        h = 1 - sqrt(real_chromosome[0] / g)
        
        # Two objectives list
        objectives = [real_chromosome[0], (g * h)]
                
        return objectives

    def num_objectives(self):
        return 2


def binary_phen_to_float(phen, n_codon, min_value, max_value):
    """
    This method converts a phenotype, defined by a
    string of bits in a list of float values
    
    :param phen: Phenotype defined by a bit string
    :param n_codon: Number of codons per gene, defined in the grammar
    :param min_value: Minimum value for a gene
    :param max_value: Maximum value for a gene
    :return: A list os float values, representing the chromosome
    """

    i, count, chromosome = 0, 0, []
    
    while i < len(phen):
        
        # Get the current gene from the phenotype string.
        gene = phen[i:(i + n_codon)]
        
        # Convert the bit string in gene to an float/int
        gene_i = int(gene, 2)
        gene_f = float(gene_i) / (2 ** n_codon - 1)
        
        # Define the variation for the gene
        delta = max_value[count] - min_value[count]
        
        # Append the float value to the chromosome list
        chromosome.append(gene_f * delta + min_value[count])

        # Increment the index and count.
        i = i + n_codon
        count += 1
    
    return chromosome
