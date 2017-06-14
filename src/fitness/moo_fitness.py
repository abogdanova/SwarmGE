import abc
from math import isnan

import numpy as np

np.seterr(all="raise")


class moo_fitness:
    """
    Fitness function for multi-objective optimization problems.
    The objective functions are defined in implementation of this
    class. The control parameters regarding the problem, as number
    of input variables and their range are defined implicitly by
    the grammar.
    This is an abstract class which exists just to be subclassed:
    should not be instantiated.
    """
    
    default_fitness = np.NaN
    
    def __call__(self, ind):
        """
        Note that math functions used in the solutions are imported from either
        utilities.fitness.math_functions or called from numpy.
        
        :param ind: An individual to be evaluated.
        :return: The fitness of the evaluated individual.
        """
        
        phen = ind.phenotype

        try:
            # the multi-objective fitness is defined as a list of
            # values, each one representing the output of one
            # objective function. The computation is made by the
            # function multi_objc_eval, implemented by a subclass,
            # according to the problem.
            fitness = self.moo_eval(phen)
        
        except (FloatingPointError, ZeroDivisionError, OverflowError,
                MemoryError):
            # FP err can happen through eg overflow (lots of pow/exp calls)
            # ZeroDiv can happen when using unprotected operators
            fitness = [moo_fitness.default_fitness] * self.num_objectives()
            
        except Exception as err:
            # other errors should not usually happen (unless we have
            # an unprotected operator) so user would prefer to see them
            print(err)
            raise
        
        if any([isnan(i) for i in fitness]):
            # Check if any objective fitness value is NaN, if so set default
            # fitness.
            fitness = [moo_fitness.default_fitness] * self.num_objectives()

        return fitness
    
    @abc.abstractmethod
    def moo_eval(self, phen):
        """
        This method implements the fitness functions defined by the
        optimization problem being solved.

        :param phen: The phenotype defined by an individual
        :return: The resulting fitness
        """
        return
    
    @staticmethod
    def value(fitness_vector, objective_index):
        if not isinstance(fitness_vector, list):
            return float("inf")
        return fitness_vector[objective_index]
    
    @abc.abstractmethod
    def num_objectives(self):
        return
