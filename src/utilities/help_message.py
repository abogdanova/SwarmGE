def help_message():
    """
    Prints a help message explaining the various parameter options
    accessible by the option parser in the
    algorithm.parameters.params dictionary.
    
    :return: Nothing.
    """
    
    lines_1 = ["Welcome to PonyGE - Help",
               "-------------------",
               "The following are the available command line args, "
               "please see src /algorithm/parameters.py",
               "for a more detailed explanation of each argument and possible "
               "values:"]

    lines_2 = [["\t--help:", "Shows this help message."],
               ["\t--debug:", "Disables saving of all ancillary files."],
               ["\t--search_loop:", "Sets the desired search loop function."],
               ["\t--step:", "Sets the desired search step function."],
               ["\t--population:", "Sets the population size, requires int "
                                   "value"],
               ["\t--generations:", "Sets the number of generations, requires"
                                    "int value"],
               ["\t--initialisation:", "Sets the initialisation strategy, "
                                       "requires a string such as 'rhh' or a "
                                       "direct path string such as "
                                       "'operators.initialisation.rhh'"],
               ["\t--max_init_tree_depth:", "Sets the max tree depth for "
                                            "initialisation"],
               ["\t--genome_init:", "Will initialise individuals by "
                                    "generating a random genome for each "
                                    "individual"],
               ["\t--max_tree_depth:", "Sets the max derivation tree depth "
                                       "for the algorithm, requires int "
                                       "value."],
               ["\t--max_tree_nodes:", "Sets the max derivation tree nodes "
                                       "for the algorithm, requires int "
                                       "value."],
               ["\t--codon_size:", "Sets the range from 0 to condon_size to "
                                   "be used in genome, requires int value"],
               ["\t--max_wraps:", "Sets the maximum number of times the "
                                  "genome mapping process can wrap over the "
                                  "length of the genome. Requires int value."],
               ["\t--max_genome_length:", "Sets the maximum chromosome length "
                                          "for the algorithm, requires int "
                                          "value"],
               ["\t--max_init_genome_length:", "Sets the maximum length for "
                                                "chromosomes to be initialised"
                                                " to, requires int value"],
               ["\t--selection:", "Sets the selection to be used, requires "
                                  "string such as 'tournament' or direct path "
                                  "string such as "
                                  "'operators.selection.tournament'"],
               ["\t--invalid_selection:", "Allow for the selection of invalid "
                                          "individuals during selection"],
               ["\t--selection_proportion:", "Sets the proportion for "
                                             "truncation selection, requires "
                                             "float, e.g. 0.5"],
               ["\t--tournament_size:", "Sets the number of indivs to contest "
                                        "tournament, requires int"],
               ["\t--crossover:", "Sets the type of crossover to be used, "
                                  "requires string such as 'subtree' or "
                                  "direct path string such as "
                                  "'operators.crossover.subtree'"],
               ["\t--crossover_probability:", "Sets the crossover "
                                              "probability, requires float, "
                                              "e.g. 0.9"],
               ["\t--replacement:", "Sets the replacement strategy, requires "
                                    "string such as 'generational' or direct"
                                    "path string such as "
                                    "'operators.replacement.generational'"],
               ["\t--mutation:", "Sets the type of mutation to be used, "
                                 "requires string such as 'int_flip' or "
                                 "direct path string such as "
                                 "'operators.mutation.int_flip'"],
               ["\t--mutation_probability:", "Sets the rate of mutation "
                                             "probability for linear genomes"],
               ["\t--mutation_events:", "Sets the number of mutation events "
                                        "based on probability"],
               ["\t--random_seed:", "Sets the seed to be used, requires int "
                                    "value"],
               ["\t--bnf_grammar:", "Sets the grammar to be used, requires "
                                    "string"],
               ["\t--fitness_function:", "Sets the fitness function to be "
                                         "used. Requires string such as "
                                         "'regression'"],
               ["\t--dataset:", "For use with problems that use a dataset. "
                                "Requires string such as 'Dow'."],
               ["\t--error_metric:", "Sets the error metric to be used with "
                                     "regression style problems. Requires "
                                     "string such as 'mse' or 'rmse'."],
               ["\t--experiment_name:", "Optional parameter to save results "
                                        "in /results/[EXPERIMENT_NAME] "
                                        "folder. If not specified then "
                                        "results are saved in default "
                                        "/results folder."],
               ["\t--target_string:", "For string match problem. Requires "
                                      "target string."],
               ["\t--verbose:", "Turns on the verbose output of the program in"
                                " terms of command line and extra files"],
               ["\t--silent:", "Prevents any output from being printed to "
                               "the command line."],
               ["\t--elite_size:", "Sets the number of elites to be used, "
                                   "requires int"],
               ["\t--save_all:", "Saves the best phenotypes at each "
                                 "generation"],
               ["\t--save_plots:", "Saves plots for best fitness"],
               ["\t--multicore:", "Turns on multicore evaluation"],
               ["\t--cores:", "Specify the number of cores to be used for "
                              "multicore evaluation. Requires int."],
               ["\t--cache:", "Tracks unique phenotypes."],
               ["\t--lookup_fitness:", "Uses the cache to lookup duplicate "
                                       "fitnesses. Automatically set to true "
                                       "with cache turned on."],
               ["\t--dont_lookup_fitness:", "Turns on the cache to track "
                                            "duplicate individuals, but does "
                                            "not use the cache to save "
                                            "fitness evaluations."],
               ["\t--lookup_bad_fitness:", "Gives duplicate phenotypes a bad "
                                           "fitness when encountered, requires"
                                           " cache."],
               ["\t--mutate_duplicates:", "Replaces duplicate individuals with"
                                          " mutated versions. Requires "
                                          "cache."]]

    lines_3 = [
             "----------------------------",
             "To try out ponyge simply run: python ponyge.py",
             " ",
             "Thanks for trying our product",
             " ",
             "PonyGE Team :D"]

    for line in lines_1:
        print(line)
    
    # This simply justifies the print statement such that it is visually
    # pleasing to look at. Items are printed in alphabetical order.
    col_width = max(len(line[0]) for line in lines_2)
    for line in sorted(lines_2):
        print(" ".join(words.ljust(col_width) for words in line))
    
    for line in lines_3:
        print(line)
