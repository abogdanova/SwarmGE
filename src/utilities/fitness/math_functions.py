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
    """aq is the analytic quotient, intended as a "better protected
    division", from: Ji Ni and Russ H. Drieberg and Peter I. Rockett,
    "The Use of an Analytic Quotient Operator in Genetic Programming",
    IEEE Transactions on Evolutionary Computation.

    :param a: np.array numerator
    :param b: np.array denominator
    :return: np.array analytic quotient, analogous to a / b.

    """
    return a / np.sqrt(1.0 + b**2.0)


def pdiv(x, y):
    """
    Koza's protected division is:

    if y == 0:
      return 1
    else:
      return x / y

    but we want an eval-able expression. The following is eval-able:

    return 1 if y == 0 else x / y

    but if x and y are Numpy arrays, this creates a new Boolean
    array with value (y == 0). if doesn't work on a Boolean array.

    The equivalent for Numpy is a where statement, as below. However
    this always evaluates x / y before running np.where, so that
    will raise a 'divide' error (in Numpy's terminology), which we
    ignore using a context manager.

    :param x: numerator np.array
    :param y: denominator np.array
    :return: np.array of x / y, or 1 where y is 0.
    """
    with np.errstate(divide='ignore'):
        return np.where(y == 0, np.ones_like(x), x / y)


def rlog(x):
    """
    Koza's protected log:
    if x == 0:
      return 1
    else:
      return log(abs(x))

    See pdiv above for explanation of this type of code.

    :param x: argument to log, np.array
    :return: np.array of log(x), or 1 where x is 0.
    """
    with np.errstate(divide='ignore'):
        return np.where(x == 0, np.ones_like(x), np.log(np.abs(x)))


def ppow(x, y):
    """pow(x, y) is undefined in the case where x negative and y
    non-integer. This takes abs(x) to avoid it.

    :param x: np.array, base
    :param y: np.array, exponent
    :return: np.array x**y, but protected

    """
    return np.abs(x)**y


def ppow2(x, y):
    """pow(x, y) is undefined in the case where x negative and y
    non-integer. This takes abs(x) to avoid it. But it preserves
    sign using sign(x).

    :param x: np.array, base
    :param y: np.array, exponent
    :return: np.array, x**y, but protected
    """
    return np.sign(x) * (np.abs(x) ** y)


def psqrt(x):
    """
    Protected square root operator

    :param x: np.array, argument to sqrt
    :return: np.array, sqrt(x) but protected.
    """
    return np.sqrt(np.abs(x))


def psqrt2(x):
    """
    Protected square root operator that preserves the sign of the original
    argument.

    :param x: np.array, argument to sqrt
    :return: np.array, sqrt(x) but protected, preserving sign.
    """
    return np.sign(x) * (np.sqrt(np.abs(x)))


def plog(x):
    """
    Protected log operator. Protects against the log of 0.

    :param x: np.array, argument to log
    :return: np.array of log(x), but protected
    """
    return np.log(1.0 + np.abs(x))


def ave(x):
    """
    Returns the average value of a list.

    :param x: a given list
    :return: the average of param x
    """

    return np.mean(x)
