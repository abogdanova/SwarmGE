import scipy

import re

from algorithm.parameters import params
from fitness.default_fitness import default_fitness
from utilities.fitness.math_functions import plog, rlog, pdiv, psqrt, aq, ppow, psqrt2, ppow2



def optimize_constants(x, y, ind):
    """Use gradient descent to search for values for the constants in
    ind.phenotype which minimise loss."""

    # let's save the old phenotype (has c[0] etc, but may not be
    # consecutive from zero)
    ind.phenotype_original = ind.phenotype

    s, n_consts = make_consts_consecutive(ind.phenotype)
    ind.phenotype_consec_consts = s

    f = eval("lambda x, c: " + s)

    loss = params['ERROR_METRIC']

    if n_consts == 0:
        # ind doesn't refer to c: no need to optimize
        c = []
        fitness = loss(y, f(x, c))
        ind.opt_consts = c
        return fitness

    obj = lambda c: loss(y, f(x, c)) # obj is now a function of c
    # only for L-BFGS-B, using 0 as the init seems a reasonable
    # choice. But for scipy.curve_fit we might use [1.0] *
    # n_consts. Maybe other minimizers do better with some other
    # choices? There are other methods to try out.
    init = [0.0] * n_consts
    res = scipy.optimize.minimize(obj, init, method="L-BFGS-B")
    # the result is accessed like a dict
    ind.opt_consts = res['x'] # the optimum values of the constants

    # the most useful form of the phenotype: c[0], c[1] etc replaced
    # with actual numbers, so can be eval'd directly
    ind.phenotype = replace_consts_with_values(s, ind.opt_consts)

    n_extra_evals = res['nfev']
    return res['fun'] # the value of the error metric at those values

def make_consts_consecutive(s):
    # the phenotype will have zero or more occurences of each
    # const c[0], c[1], etc. But eg it might have c[7], but no
    # c[0].  we need to remap eg 7->0, 9->1 so that we just have
    # c[0], c[1], etc.

    p = r"c\[(\d+)\]"
    # find the consts, extract idxs as ints, unique-ify and sort
    const_idxs = sorted(map(int, set(re.findall(p, s))))

    for i, j in enumerate(const_idxs):
        ci = "c[%d]" % i
        cj = "c[%d]" % j
        s = s.replace(cj, ci)

    return s, len(const_idxs)

def replace_consts_with_values(s, c):
    for i in range(len(c)):
        s = s.replace("c[%d]" % i, str(c[i]))
    return s
