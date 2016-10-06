from algorithm.parameters import params


def set_fitness_params():
    """
    Sets the correct grammar file and any additional problem specifics
    required for the problem.
    
    :return: Nothing.
    """
    
    if params['PROBLEM'] in ("regression", "classification"):
        # FITNESS_FUNC_INPUT is the problem suite.
        params['GRAMMAR_FILE'] = "grammars/" + params['SUITE'] + ".bnf"
        params['FITNESS_FUNC_INPUT'] = params['SUITE']

    elif params['PROBLEM'] == "string_match":
        # FITNESS_FUNC_INPUT is the string match target.
        params['GRAMMAR_FILE'] = "grammars/letter.bnf"
        params['FITNESS_FUNC_INPUT'] = params['STRING_MATCH_TARGET']

    else:
        print("Error: Problem not specified correctly.")
        exit(2)


def set_fitness_function():
    """
    Sets the fitness function for a problem automatically. Fitness functions
    are stored in fitness. Fitness functions must be classes, where the
    class name matches the file name.
    
    :return: Nothing.
    """
    
    # Set the import for the required fitness function.
    import_func = "from fitness." + params['PROBLEM'] + " import " + params[
        'PROBLEM']
    
    # Import the required fitness function.
    exec(import_func)
    
    # Set the fitness function in the params dictionary.
    # params['FITNESS_FUNC_INPUT'] is the input required for initialisation
    # of the fitness function.
    params['FITNESS_FUNCTION'] = eval(
        params['PROBLEM'] + "(params['FITNESS_FUNC_INPUT'])")
