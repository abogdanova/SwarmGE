from regression import regression
from string_match import string_match

def set_fitness_function(problem, alternate=None):
    #Regression Problem
    if problem == "regression":
        return regression(alternate)
    #String Match Problem
    elif problem == "string_match":
        return string_match(alternate)
    elif problem == "new":
        print ("new pronlem goes here")
        #parameters.FITNESS_FUNCTION = whatever
    else:
        print ("Please specify a fitness function")
        exit()