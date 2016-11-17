

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
        if ". ." in regex_string:
            print("----- Interesting string: " + regex_string)
        try:
            if "5c" == regex_string:
                print("aha - " + regex_string)
                print("aha - " + regex_string)
            compiled_regex = re.compile(regex_string)
            eval_results = self.test_regex(compiled_regex)
            fitness = self.calculate_fitness(eval_results)
#            if "5c" in regex_string:
#                print(regex_string + ": {}".format(fitness))
            return fitness
        except:
#            print(Exception)
            return 100000

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
        result_error=0
        time_sum=0.0
        for a_result in eval_results:
            time_sum += a_result[0] /  a_result[2]
            if a_result[1] == None: # no match 
                result_error += 100 * (len(a_result[3].search_string) + len(a_result[3].matched_string))
#                print("No Match")
            else: # a match which may be the empty string                
                if a_result[1] in a_result[3].matched_string: # the found match is one of the desired extractions
                    match_error += len(a_result[1]) - a_result[3].matched_string # but it may not be the correct match location
                if a_result[1].group(0) not in a_result[3].matched_string:
                    match_error+=(len(a_result[3].search_string) + len(a_result[3].matched_string)) # encourage regex which match something
                elif not a_result[1].group(0):
                    match_error+=10*(len(a_result[3].search_string) + len(a_result[3].matched_string))
                else:
                    match_error+= 50*(abs(len(a_result[3].matched_string) - len(a_result[1].group(0))))
                # if match_lev < len(a_result[3].matched_string):
                # result_error += match_error #+ abs(len(a_result[3].matched_string) - len(a_result[1].group(0)))
                result_error += match_error 
#                if len(a_result[1].group(0)) > 1 and len(a_result[1].group(0)) < len(a_result[3].matched_string):
#                    print(a_result[3].matched_string + " " + a_result[1].group(0) + " {}".format(result_error))
        if result_error:
            fitness = result_error
        else:
            fitness = time_sum
        # if fitness == seed_fitness:
        # fitness = 100 * len(a_result) # identical result to seed penalised (plucking the centre from spiderweb)
        return fitness
    
    def test_regex(self,compiled_regex):
        results = list()
        # do a quick test to time the longest test case (which is also the last in the list)
        quick_test = self.time_regex_test_case(compiled_regex, self.test_cases[len(self.test_cases)-1], 10)
        # aim for entire test suite to take less than a second
        eval_time = .01 # seconds
        testing_iterations = int(( eval_time / (quick_test[0]/10))/len(self.test_cases)) # change to half second?
        for test_case in self.test_cases:
            results.append(self.time_regex_test_case(compiled_regex, test_case, testing_iterations))
        return results

    def time_regex_test_case(self, compiled_regex, test_case, iterations):
        search_string = test_case.get_search_string()
        def wrap():
            return compiled_regex.search(search_string)
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
        a_test_string = RegexTestString("Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 14")
        a_test_string.add_match(119,136) # 5c:0a:5b:63:4a:82

        #a_test_string = RegexTestString("Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 140.105.63.164(50:06:04:92:53:44):80 TCP flags: ****S* len:60 ttl:32)")
        #a_test_string.add_match(119,136) # 5c:0a:5b:63:4a:82
        #a_test_string.add_match(161,178) # 50:06:04:92:53:44

        self.test_cases.append(a_test_string)
        
class RegexTestString:
    def __init__(self,search_string):
        print("Added regex search string: "+search_string)
        self.search_string = search_string
        self.match = list()

    def add_match(start, end):
        self.match.append(start=start,end=end, matched_string=self.search_string[start:end])
        print("Added the following match: "+self.match.matched_string)
#         for i in range(start,end-1):
#             for j in range(start+1,end):
#                 self.match.append(start=i,end=j, matched_string=self.search_string[i:j])
        
    def calc_match_errors(match_candidates):
        start_errors=list()
        end_errors=list()
        match_error = 0
        # is it cheaper to make a copy and remove characters as they are matched, or create a set of all sub-snippets and what ones the candidate matches?
        for a_known_match in self.match:
            closest_start=list()
            closest_end==list()
            for a_match in match_candidates:
                closest_start.append(a_known_match.start - a_match.start)
                closest_end.append(a_known_match.end - a_match.end)
            start_errors.append(min(closest_start))
            end_errors.append(min(closest_end))
        return sum(start_errors,end_errors)
#             for a_match_candidate in match_candidates: # how much of our known match has gone unmatched?
#                 temp_match=0
#                 if a_matched_candidate.start < a_known_match.end or a_matched_candidate.end > a_known_match.start:
#                     unmatched_start = a_matched_candidate.start - a_known_match.start # should be positive, if negative then there is none unmatched
#                     unmatched_end = a_matched_candidate.end - a_known_match.start # should be positive
#                     temp_match = max(unmatched_end,0) + max(unmatched_start,0)


        
    def compare(self,attempt_string):
        error = distance(self.matched_string, attempt_string.group(0))
        attempti=0
        attempti += self.search_string.find(attempt_string.group(0))
        if attempti < self.starti:
            error+= self.starti-attempti
        elif attempti > self.endi:
            error+= attempti-self.endi
        return error

    def get_search_string(self,):
        return self.search_string

    
