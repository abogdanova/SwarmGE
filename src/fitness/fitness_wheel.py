from parameters.parameters import params


def set_fitness_params():
    """
    Sets the correct inputs required for the fitness function.
    
    :return: Nothing.
    """
    
    if params['FITNESS_FUNCTION'] in ("regression", "classification"):
        
        # FIXME: We shouldn't be doing a string match here, we should be checking the attributes of the fitness function itself. Unfortunately, we can't initialise the fitness function without the fitness function inputs. We can change this, but then there would be a problem with circular imports. What a quandry.
        
        # FITNESS_FUNC_INPUT is the problem suite.
        params['FITNESS_FUNC_INPUT'] = params['DATASET']

    elif params['FITNESS_FUNCTION'] == "string_match":
        # FITNESS_FUNC_INPUT is the string match target.
        params['FITNESS_FUNC_INPUT'] = params['STRING_MATCH_TARGET']

    else:
        print("Error: Problem not specified correctly in "
              "fitness.fitness_wheel.set_fitness_params.")
        exit(2)
