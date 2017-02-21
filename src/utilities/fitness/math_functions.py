import numpy as np
np.seterr(all="raise")


def return_one_percent(num, pop_size):
    """
    Returns either one percent of the population size or a given number,
    whichever is larger.
       
    :param num: A given number of individuals (NOT a desired percentage of
    the population).
    :param pop_size: A given population size.
    :return: either one percent of the population size or a given number,
    whichever is larger.
    """
    
    # Calculate one percent of the given population size.
    percent = int(round(pop_size/100))
    
    # Return the biggest number.
    if percent < num:
        return num
    else:
        return percent


def return_percent(num, pop_size):
    """
    Returns [num] percent of the population size.

    :param num: A desired percentage of the population.
    :param pop_size: A given population size.
    :return: [num] percent of the population size.
    """
    
    return int(round(num * pop_size / 100))


def aq(a, b):
    """
    The analytic quotient, intended as a "better protected division",
    from: Ji Ni and Russ H. Drieberg and Peter I. Rockett, "The Use of
    an Analytic Quotient Operator in Genetic Programming", IEEE
    Transactions on Evolutionary Computation.
    
    :param a: The numerator for division.
    :param b: The denominator for division.
    :return: The analytic quotient.
    """
    
    return a / np.sqrt(1.0 + b**2.0)


def pdiv(x, y):
    """
    Koza's protected division.

    we want this to work as an eval-able expression so we can't include
    if-statements. Have to use some intermediate-level Numpy trickery. This
    will raise a warning (depending on Numpy error settings) because it always
    evaluates x / y before running np.where.
    
    :param a: The numerator for division.
    :param b: The denominator for division.
    :return: 1 if y == 0, else x / y
    """
    return np.where(y == 0, np.ones_like(x), x / y)


def rlog(x):
    """
    Koza's protected log operator.
    
    something not quite right...
    
    :param x: The argument for protected log.
    :return: Protected log.
    """
    
    #TODO Implement Koza's protected log operator.
    # return np.where(x == 0, np.ones_like(x), np.log(np.abs(x)))
    raise NotImplementedError


def ppow(x, y):
    # for the case where x negative and y non-integer
    return np.abs(x)**y


def ppow2(x, y):
    # for the case where x negative and y non-integer
    # preserve sign
    return np.sign(x) * (np.abs(x) ** y)


def psqrt(x):
    """
    Protected square root operator. Protects against square root of negative
    numbers.
    
    :param x: The argument for protected square root.
    :return: The square root.
    """
    
    return np.sqrt(np.abs(x))


def psqrt2(x):
    """
    Protected square root operator that preserves the sign of the original
    argument.
    
    :param x: The argument for protected square root.
    :return: The square root with the preserved sign.
    """
    
    return np.sign(x) * (np.sqrt(np.abs(x)))


def plog(x):
    """
    Protected log operator. Protects against the log of 0.
    
    :param x: The argument for protected log.
    :return: Protected log.
    """
    
    return np.log(1.0 + np.abs(x))


def ave(x):
    """
    Returns the average value of a list.
    
    :param x: a given list
    :return: the average of param x
    """
    
    return np.mean(x)
