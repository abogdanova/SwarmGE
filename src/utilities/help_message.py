def help_message():
    lines = ["Welcome to PonyGE - Help",
             "-------------------",
             "The following are the available command line args:",
             "\t--help: \tShows this help message",
             "\t--debug: \tDisables printing of all ancillary files",
             "\t--population: \tSets the population size, requires int value",
             "\t--generations: \tSets the number of generations, requires int value",
             "\t--initialisation: \t",
             "\t--max_init_depth: \t",
             "\t--genome_init: \t",
             "\t--max_tree_depth: \t",
             "\t--codon_size: \t",
             "\t--selection: \t",
             "\t--selection_proportion: \t",
             "\t--tournament_size: \t",
             "\t--crossover: \t",
             "\t--crossover_prob: \t",
             "\t--replacement: \t",
             "\t--mutation: \t",
             "\t--mutation_events: \t",
             "\t--random_seed: \t",
             "\t--bnf_grammar: \t",
             "\t--problem: \t",
             "\t--problem_suite: \t",
             "\t--target_string: \t",
             "\t--verbose: \t",
             "\t--elite_size: \t",
             "\t--save_all: \t",
             "\t--save_plots: \t",
             "\t--cache: \t",
             "\t--lookup_fitness: \t",
             "\t--lookup_bad_fitness: \t",
             "\t--mutate_duplicates: \t",
             "\t--complete_evals: \t"]

    for line in lines:
        print(line)

if __name__ == "__main__":
    help_message()
