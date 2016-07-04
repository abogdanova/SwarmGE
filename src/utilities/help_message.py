def help_message():
    lines = ["Welcome to PonyGE - Help",
             "-------------------",
             "The following are the available command line args, "
             "please see src /algorithm/parameters.py",
             "for a more detailed explanation of each argument and possible "
             "values:",
             "\t--help: \t\tShows this help message",
             "\t--debug: \t\tDisables saving of all ancillary files",
             "\t--population: \t\tSets the population size, requires int "
             "value",
             "\t--generations: \t\tSets the number of generations, requires "
             "int value",
             "\t--initialisation: \t\tSets the initialisation, requires a "
             "string such as rhh",
             "\t--max_init_depth: \t\tSets the max tree depth for "
             "initialisation",
             "\t--genome_init: \t\tWill initialise individuals by generating "
             "a random genome for each individual",
             "\t--max_tree_depth: \t\tSets the max derivation tree depth for "
             "the algorithm, requires int value",
             "\t--codon_size: \t\tSets the range from 0 to condon_size to be "
             "used in genome, requires int value",
             "\t--genome_length: \t\tSets the maximum length for chromosomes "
             "to be initialised to, requires int value",
             "\t--selection: \t\tSets the selection to be used, requires "
             "string such as tournament",
             "\t--invalid_selection: \t\tAllow for the selection of invalid "
             "individuals during selection",
             "\t--selection_proportion: \t\tSets the proportion for truncation"
             " selection, requires float like 0.5",
             "\t--tournament_size: \t\tSets the number of indivs to contest "
             "tournament, requires int",
             "\t--crossover: \t\tSets the type of crossover to be used, "
             "requires string such as subtree",
             "\t--crossover_prob: \t\tSets the crossover probability, requires"
             " float such as 0.9",
             "\t--replacement: \t\tSets the replacement strategy, requires "
             "string such as generational",
             "\t--mutation: \t\tSets the mutation to be used, requires string"
             " such as int_flip",
             "\t--mutation_probability: \t\tSets the rate of mutation "
             "probability for linear genomes",
             "\t--mutation_events: \t\tSets the number of mutation events "
             "based on probability",
             "\t--random_seed: \t\tSets the seed to be used, requires int "
             "value",
             "\t--bnf_grammar: \t\tSets the grammar to be used, requires "
             "string",
             "\t--problem: \t\tSets the problem to be used, requires string "
             "such as regression",
             "\t--problem_suite: \t\tFor use with regression problems, "
             "requires string such as Dow",
             "\t--target_string: \t\tFor string match problem, requires "
             "target string",
             "\t--verbose: \t\tTurns on the verbose output of the program in"
             " terms of command line and extra files",
             "\t--elite_size: \t\tSets the number of elites to be used, "
             "requires int",
             "\t--save_all: \t\tSaves the best phenotypes at each generation",
             "\t--save_plots: \t\tSaves plots for best fitness",
             "\t--cache: \t\tTracks unique phenotypes.",
             "\t--lookup_fitness: \t\tUses the cache to lookup duplicate "
             "fitnesses. Automatically set to true with cache turned on.",
             "\t--lookup_bad_fitness: \t\tGives duplicate phenotypes a bad "
             "fitness when encountered, requires cache.",
             "\t--mutate_duplicates: \t\tReplaces duplicate idividuals with "
             "mutated versions. Requires cache.",
             "\t--complete_evals: \t\tAdvanced feature to reuse save "
             "computation from use of cache.",
             "----------------------------",
             "To try out ponyge simply run: python ponyge.py",
             " ",
             "Thanks for trying our product",
             " ",
             "PonyGE Team :D"]

    for line in lines:
        print(line)
