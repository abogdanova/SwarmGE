import numpy as np


def return_percent(num, pop_size):
    """Returns either one percent of the population size or a given number,
       whichever is larger."""
    percent = int(round(pop_size/100))
    if percent < num:
        return num
    else:
        return percent


def pdiv(a, b):
    """The analytic quotient, intended as a "better protected division",
    from: Ji Ni and Russ H. Drieberg and Peter I. Rockett, "The Use of
    an Analytic Quotient Operator in Genetic Programming", IEEE
    Transactions on Evolutionary Computation."""
    return a / np.sqrt(1.0 + b * b)


def psqrt(x):
    """ Protected square root operator"""
    return np.sqrt(np.abs(x))


def plog(x):
    """ Protected log operator"""
    return np.log(1.0 + np.abs(x))


def ave(x):
    """
    :param x: a given list
    :return: the average of param x
    """

    return sum(x)/len(x)
