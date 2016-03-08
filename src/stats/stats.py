from algorithm import parameters
from datetime import timedelta
import time

def ave(x):
    """Returns the average of a given list."""

    return sum(x)/len(x)

def print_stats(generation, individuals, best_ever, phenotypes, total_inds, invalids, regens, time_list, TIME_STAMP):
    """Print the statistics for the generation and individuals"""
    t1 = time.clock()
    time_list.append(t1)
    time_taken = timedelta(seconds = time_list[-1] - time_list[-2])

    print "\nGen:\t", generation
    print "  Best fitness:\t", best_ever.fitness
    print "  Total inds: \t", total_inds
    if parameters.CACHE:
        print "  Re-generated:\t", regens
        print "  Unique evals:\t", len(phenotypes)
    print "  Invalid inds:\t", invalids
    if parameters.CACHE:
        print "  Unused search:",100 - len(phenotypes)/float(total_inds)*100,"percent"

    if parameters.GENOME_OPERATIONS:
        max_depth = max([len(i.genome) for i in individuals
                            if i.phenotype is not None])
        ave_depth = ave([len(i.genome) for i in individuals
                            if i.phenotype is not None])
        max_nodes = max([i.used_codons for i in individuals
                            if i.phenotype is not None])
        ave_nodes = ave([i.used_codons for i in individuals
                            if i.phenotype is not None])
        print "  Ave genome length:", ave_depth
        print "  Max genome length:", max_depth
        print "  Ave used codons  :", ave_nodes
        print "  Max used codons  :", max_nodes

    else:
        max_depth = max([i.depth for i in individuals
                            if i.phenotype is not None])
        ave_depth = ave([i.depth for i in individuals
                            if i.phenotype is not None])
        max_nodes = max([i.nodes for i in individuals
                            if i.phenotype is not None])
        ave_nodes = ave([i.nodes for i in individuals
                            if i.phenotype is not None])
        print "  Ave tree depth:", ave_depth
        print "  Max tree depth:", max_depth
        print "  Ave tree nodes:", ave_nodes
        print "  Max tree nodes:", max_nodes

    print "  Time Taken: \t", time_taken, "\n"
    if not parameters.DEBUG:
        save_results(generation, best_ever.fitness, time_taken, len(phenotypes), total_inds, invalids, regens, ave_depth, max_depth, ave_nodes, max_nodes, TIME_STAMP)
        if parameters.SAVE_ALL:
            save_best(generation, generation, best_ever, TIME_STAMP)
        else:
            save_best("best", generation, best_ever, TIME_STAMP)

def save_results(generation, fitness, time_taken, phenotypes, total_inds, invalids, regens, ave_depth, max_depth, ave_nodes, max_nodes, TIME_STAMP, total_time=None, END=False):
    """Write the results to a results file for later analysis"""

    filename = "./Results/" + str(TIME_STAMP) + "/" + str(TIME_STAMP)+ ".txt"
    savefile = open(filename, 'a')
    if not END:
        savefile.write("Gen:\t" + str(generation))
        savefile.write("\tfitness:\t" + str(fitness))
        savefile.write("\tTotal inds:\t" + str(total_inds))
        savefile.write("\tRe-generated:\t" + str(regens))
        savefile.write("\tUnique evals:\t" + str(phenotypes))
        savefile.write("\tInvalid inds:\t" + str(invalids))
        savefile.write("\tUnused search:\t" + str(100 - (phenotypes/float(total_inds))*100) + " percent")
        if parameters.GENOME_OPERATIONS:
            savefile.write("\tAve genome length:\t" + str(ave_depth))
            savefile.write("\tMax genome length:\t" + str(max_depth))
            savefile.write("\tAve used codons:\t" + str(ave_nodes))
            savefile.write("\tMax used codons:\t" + str(max_nodes))
        else:
            savefile.write("\tAve tree depth:\t" + str(ave_depth))
            savefile.write("\tMax tree depth:\t" + str(max_depth))
            savefile.write("\tAve tree nodes:\t" + str(ave_nodes))
            savefile.write("\tMax tree nodes:\t" + str(max_nodes))
        savefile.write("\tTime Taken:\t" + str(time_taken) + "\n")
    elif END:
        savefile.write("\n\nGrammar =      \t" + str(parameters.GRAMMAR_FILE.split("/")[1].split(".")[0])
                       + "\nBest fitness = \t" + str(fitness)
                       + "\nPopulation Size = " + str(parameters.POPULATION_SIZE)
                       + "\nGenerations =  \t" + str(parameters.GENERATIONS)
                       + "\nMutation =     \t" + str(parameters.MUTATION_PROBABILITY)
                       + "\nCrossover =    \t" +str(parameters.CROSSOVER_PROBABILITY)
                       + "\nCodon Size =   \t" + str(parameters.CODON_SIZE)
                       + "\nTotal inds =   \t" + str(total_inds)
                       + "\nRe-generated = \t" + str(regens)
                       + "\nUnique evals = \t" + str(phenotypes)
                       + "\nInvalid inds = \t" + str(invalids)
                       + "\nUnused search =\t" + str(100 - (phenotypes/float(total_inds))*100) + " percent"
                       + "\nTotal time:\t" + str(total_time))
    savefile.close()

def save_best(name, gen, best_ever, TIME_STAMP):
    filename = "./Results/" + str(TIME_STAMP) + "/" + str(name) + ".txt"
    savefile = open(filename, 'w')
    savefile.write("Generation:\n" + str(gen) + "\n\n")
    savefile.write("Phenotype:\n" + str(best_ever.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(best_ever.genome) + "\n")
    savefile.write("Tree:\n" + str(best_ever.tree) + "\n")
    savefile.write("\nfitness:\t" + str(best_ever.fitness))
    savefile.close()