from parameters.parameters import params


def set_fitness_params():
    """
    Sets the correct grammar file and any additional problem specifics
    required for the problem.
    
    :return: Nothing.
    """
    
    if params['FITNESS_FUNCTION'] in ("regression", "classification"):
        # FITNESS_FUNC_INPUT is the problem suite.
        if not params['GRAMMAR_FILE']:
            params['GRAMMAR_FILE'] = "grammars/" + \
                params['DATASET'] + ".bnf"
        params['FITNESS_FUNC_INPUT'] = params['DATASET']

    elif params['FITNESS_FUNCTION'] == "string_match":
        # FITNESS_FUNC_INPUT is the string match target.
        if not params['GRAMMAR_FILE']:
            params['GRAMMAR_FILE'] = "grammars/letter.bnf"
        params['FITNESS_FUNC_INPUT'] = params['STRING_MATCH_TARGET']

    else:
        print("Error: Problem not specified correctly in "
              "fitness.fitness_wheel.set_fitness_params.")
        exit(2)
