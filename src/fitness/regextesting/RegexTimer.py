import time, timeit

def time_regex_test_case(compiled_regex, test_case, iterations):
    """
    Execute and time a single regex on a single test case
    
    :param compiled_regex:
    :param test_case:
    :param iterations:
    :return:
    """
    
    repeats = 10
    search_string = test_case.get_search_string()
    
    def wrap():
        # Timing bug, lazy eval defers computation if we don't
        # force (convert to list evals result here)
        # https://swizec.com/blog/python-and-lazy-evaluation/swizec/5148
        return list(compiled_regex.finditer(search_string))
    
    t = timeit.Timer(wrap)
    repeat_iterations = t.repeat(repeat=repeats, number=iterations)
    best_run = list(repeat_iterations[0])
    
    for repeated_timeit in repeat_iterations:
        if best_run[0] > list(repeated_timeit)[0]:
            best_run = list(repeated_timeit)
    
    return_vals = list(best_run)
    return_vals.append(iterations)
    return_vals.append(test_case)
    
    return return_vals
