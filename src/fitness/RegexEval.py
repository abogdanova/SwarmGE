

from Levenshtein import distance 
import re
import time, timeit

# http://stackoverflow.com/questions/24812253/how-can-i-capture-return-value-with-python-timeit-module/
timeit.template = """
def inner(_it, _timer{init}):
    {setup}
    _t0 = _timer()
    for _i in _it:
        retval = {stmt}
    _t1 = _timer()
    return _t1 - _t0, retval
"""
    
class RegexEval:
    """
    Fitness function for checking regex matching which sums functionality and time.
    The regex is presented with a number of strings. 
    The resulting matched values are checked against known correct answers
    """

    maximise = False
    
    def __init__(self):
        self.test_cases = list()
        self.generate_tests()

    def __call__(self, regex_string):
        compiled_regex = re.compile(regex_string)
        eval_results = self.test_regex(compiled_regex)
        return self.calculate_fitness(eval_results)

    def calculate_fitness(self,eval_results):
        """
        We have a list of ( time, match object/null, iterations )
        In order of most interesting first:
        Match all
        -Quicker than seed
        -Slower than seed (doing same thing, but different)
        Match some
        -quicker, same, slower
        Match all
        -Same time as seed (meh, not interesting)
        Match none
        -same, slower, quicker (empty regex?)
        Fitness = time + 100 * num_missed_matches (time will be in low seconds)
        """
        for a_result in eval_results:
            if a_result[1] == None:
                missed_match = 2
            else: # see how close it got to desired match (as error ratio)
                # if levenstein is 0 (the same), then error will be 0
                # if levenstein is most it can be, then error will 1
                missed_match = a_result[3].compare(a_result[1]) / len(a_result) 
        fitness = a_result[0] + 100 * missed_match
#        if fitness == seed_fitness:
 #           fitness = 100 * len(a_result) # identical result to seed penalised (plucking the centre from spiderweb)
        return fitness
    
    def test_regex(self,compiled_regex):
        results = list()
        # do a quick test to time the longest test case (which is also the last in the list)
        quick_test = self.time_regex_test_case(compiled_regex, self.test_cases[len(self.test_cases)-1], 10)
        # aim for longest test to take a second
        testing_iterations = int(1 / (quick_test[0]/10)) # change to half second?
        for test_case in self.test_cases:
            results.append(self.time_regex_test_case(compiled_regex, self.test_cases[len(self.test_cases)-1], testing_iterations))
        return results

    def time_regex_test_case(self, compiled_regex, test_case, iterations):
        search_string = test_case.get_search_string()
        def wrap():
            return compiled_regex.match(search_string)
        t = timeit.Timer(wrap) # does timeit do a number of iterations and pick the lowest? or does it do 100000 iterations and return time?
        return_tuple = t.timeit(number = iterations)
        #return_vals = t.timeit()
        return_vals = list(return_tuple)
        return_vals.append(iterations)
        return_vals.append(test_case)
        return return_vals

    """
    Given a test string and the desired match,
    Break the desired match into substrings,
    these substrings give us a gradient.
    Multiple search_strings should be used to guide toward generality. 
    """
    def generate_tests(self):
        search_string = "Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 140.105.63.164(50:06:04:92:53:44):80 TCP flags: ****S* len:60 ttl:32)"
        match_string = "5c:0a:5b:63:4a:82"
        for i in range(1, len(match_string)):
            for j in range(len(match_string)-i):
                self.test_cases.append(
                    RegexTestString(search_string, # does this duplicate the search_string? (keep it simple hi)
                                    match_string[j:j+i])
                )
        
class RegexTestString:
    def __init__(self,search_string,matched_string):
        self.search_string = search_string
        self.matched_string = matched_string
        
    def compare(self,attempt_string):
        return distance(self.matched_string, attempt_string.group(0))

    def get_search_string(self,):
        return self.search_string

    
