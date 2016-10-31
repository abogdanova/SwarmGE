

from Levenshtein import distance 
import re
import timeit, time

def _template_func(setup, func):
    """Create a timer function. Used if the "statement" is a callable.
    http://stackoverflow.com/questions/24812253/how-can-i-capture-return-value-with-python-timeit-module
    """
    def inner(_it, _timer, _func=func):
        setup()
        _t0 = _timer()
        for _i in _it:
            retval = _func()
            _t1 = _timer()
            return _t1 - _t0, retval
        return inner
    
timeit._template_func = _template_func
    
class RegexEval:
    """
    Fitness function for checking regex matching which sums functionality and time.
    The regex is presented with a number of strings. 
    The resulting matched values are checked against known correct answers
    """
    
    def __init__(self):
        self.test_cases = list()
        generate_tests()

    def __call__(self, regex_string):
        compiled_regex = re.compile(regex_string)
        eval_results = test_regex(compiled_regex)
        return calculate_fitness(results)

    def test_regex(compiled_regex):
        results = list()
        # do a quick test to time the longest test case (which is also the last in the list)
        quick_test = time_regex_test_case(compiled_regex, test_cases[len(test_cases)], 10)
        # aim for a test to take a second
        testing_iterations = 1 / (quick_test[0]/10) # time for one iteration
        for test_case in test_cases:
            results.add(time_regex_test_case(compiled_regex, test_cases[len(test_cases)], testing_iterations)
        return results

    def time_regex_test_case(compiled_regex, test_case, iterations):
        search_string = test_case.get_search_string()
        def wrap():
            return compiled_reg.match(search_string)
        t = timeit.Timer(wrap) # does timeit do a number of iterations and pick the lowest? or does it do 100000 iterations and return time?
        return t.timeit(number = iterations), iterations

    """
    Given a test string and the desired match,
    Break the desired match into substrings,
    these substrings give us a gradient.
    Multiple search_strings should be used to guide toward generality. 
    """
    def generate_tests():
        search_string = "Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 140.105.63.164(50:06:04:92:53:44):80 TCP flags: ****S* len:60 ttl:32)"
        match_string = "5c:0a:5b:63:4a:82"
        for i in range(1, len(match_String)):
            for j in range(len(match_String)-i):
                self.test_cases.add(
                    RegexTestString(search_string, # does this duplicate the search_string? (keep it simple hi)
                                    match_string[j:j+i])
                )
        
class RegexTestString:
    def __init__(self,search_string,matched_string):
        self.search_string = search_string
        self.matched_string = matched_string
        
    def compare(attempt_string):
        return distance(self.matched_string, attempt_string)

    def get_search_string():
        return self.search_string

    
