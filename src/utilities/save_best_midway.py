from datetime import datetime

def save_best_midway(gen, best_ever, TIME_STAMP, time_list):
    filename = "./Results/" + str(TIME_STAMP) + "/best_" + str(gen) + ".txt"
    savefile = open(filename, 'w')
    time = datetime.now()
    time_list.append(time)
    time_taken = time_list[-1] - time_list[0]
    savefile.write("Generation:\n" + str(gen) + "\n\n")
    savefile.write("Phenotype:\n" + str(best_ever.phenotype) + "\n\n")
    savefile.write("Genotype:\n" + str(best_ever.genome) + "\n")
    savefile.write("Tree:\n" + str(best_ever.tree) + "\n")
    savefile.write("\nFitness:\t" + str(best_ever.fitness))
    savefile.write("\nTotal time:\t" + str(time_taken))
    savefile.close()