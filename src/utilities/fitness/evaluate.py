def eval_or_exec(phenotype, dictionary):
    """
    Use eval or exec to interpret a given phenotype string. A limitation in
    Python is the distinction between eval and exec. The former can only be
    used to return the value of a simple expression (not a statement) and the
    latter does not return anything.

    :param phenotype: A phenotype string.
    :return: The output of the evaluated phenotype string.
    """

    try:
        locals().update(dictionary)
        retval = eval(phenotype)

    except SyntaxError:
        # SyntaxError will be thrown by eval() if s is compound,
        # ie not a simple expression, eg if it contains function
        # definitions, multiple lines, etc. Then we must use
        # exec(). Then we assume that s will define a variable
        # called "XXXeval_or_exec_outputXXX", and we'll use that.
        exec(phenotype, dictionary)
        retval = dictionary["XXXeval_or_exec_outputXXX"]

    return retval

