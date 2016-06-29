from algorithm.parameters import params
from sys import maxsize


def default_fitness(maximise):
    """ Return default fitness given maximization of minimization"""
    if maximise:
        return -maxsize
    else:
        return maxsize


def eval_or_exec(expr):
    """ Use eval or exec to interpret expr.

    A limitation in Python is the distinction between eval and
    exec. The former can only be used to return the value of a simple
    expression (not a statement) and the latter does not return
    anything."""

    #print(s)
    try:
        try:
            retval = eval(expr)
        except SyntaxError:
            # SyntaxError will be thrown by eval() if s is compound,
            # ie not a simple expression, eg if it contains function
            # definitions, multiple lines, etc. Then we must use
            # exec(). Then we assume that s will define a variable
            # called "XXXeval_or_exec_outputXXX", and we'll use that.
            dictionary = {}
            exec(expr, dictionary)
            retval = dictionary["XXXeval_or_exec_outputXXX"]
    except MemoryError:
        # Will be thrown by eval(s) or exec(s) if s contains over-deep
        # nesting (see http://bugs.python.org/issue3971). The amount
        # of nesting allowed varies between versions, is quite low in
        # Python2.5. If we can't evaluate, award bad fitness.
        retval = default_fitness(params['FITNESS_FUNCTION'].maximise)
    return retval
