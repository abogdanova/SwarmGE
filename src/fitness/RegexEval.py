import re
import time, timeit
import traceback
import sys


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
    Fitness function for checking regex matching which sums functionality error.
    The regex is presented with a number of strings.
    The resulting matched values are checked against known correct answers
    """

    maximise = False
    
    def __init__(self):
        self.test_cases = list()
        self.generate_tests()
        self.time=False

    def __call__(self, individual):
        regex_string = individual.phenotype
        #regex_string = "\d.*\w.$|e"
        #        regex_string="!|\w.[6-l]\w\w[^!]\w\w[^!]\w\w[^!]\d\w[^P]\w\w"
        try:
            compiled_regex = re.compile(regex_string)
            eval_results = self.test_regex(compiled_regex)
            fitness = self.calculate_fitness(eval_results)
            #            if "5" in regex_string:
            # (we should use multi-objective/pareto front)
            #print(regex_string + ": {}".format(fitness))
            #sys.exit()

            return fitness + (len(individual.genome)/10000) #fitness # error is first, length second
            #if fitness >= 1: # If there is a functionality error, we don't really care about time 
            #    return fitness + (len(individual.genome)/10000) #fitness # error is first, length second
                #return fitness + (len(regex_string)/10000) #fitness # error is first, length second
            #else:
            #    self.time=True
            #    return fitness 

        except:
#            print(traceback.format_exc())
#            sys.exit()
            return 100000
            

    def calculate_fitness(self,eval_results):
        result_error=0
        time_sum=0.0
        for a_result in eval_results:
            time_sum += a_result[0] /  a_result[2]
            # if a_result[1] == None: # no match
            # result_error += 100 * (len(a_result[3].search_string)) #+ len(a_result[3].matched_string))
            # else: # a match which may be the empty string
            result_error += a_result[3].calc_match_errors(list(a_result[1]))
        #if result_error >1:
        #    fitness = result_error
        # else:
        #     fitness = time_sum
        fitness = time_sum + result_error
        # if fitness == seed_fitness:
        # fitness = 100 * len(a_result) # identical result to seed penalised (plucking the centre from spiderweb)
        return fitness

    def test_regex(self,compiled_regex):
        results = list()
        testing_iterations=1
        # do a quick test to time the longest test case (which is also the last in the list)
        quick_test = self.time_regex_test_case(compiled_regex, self.test_cases[len(self.test_cases)-1], testing_iterations)
        #        print("quick_test time: {}".format(quick_test[0]))
        # aim for entire test suite to take less than a second
        eval_time = .001 # seconds
        if self.time:
            testing_iterations = int(( eval_time / (quick_test[0]/10))/len(self.test_cases)) # change to half second?
        # print("Iterations {}".format(testing_iterations))
        for test_case in self.test_cases:
            results.append(self.time_regex_test_case(compiled_regex, test_case, testing_iterations))
        return results

    def time_regex_test_case(self, compiled_regex, test_case, iterations):
        search_string = test_case.get_search_string()
        def wrap():
            return compiled_regex.finditer(search_string)
        t = timeit.Timer(wrap) # does timeit do a number of iterations and pick the lowest? or does it do 100000 iterations and return time?
        return_tuple = t.timeit(number = iterations)
        #return_vals = t.timeit()
        return_vals = list(return_tuple)
        return_vals.append(iterations)
        return_vals.append(test_case)
        return return_vals

    """ 
    This is a 'booster' for test suite generation. We know a single good match, 
    and we can use that to find search strings which do not contain a match.
    Given a regex, generate/discoverB a test suite of examples which match, and those that don't.
    The test suite is used to define (or outline) the functionality boundaries of the regex.
    When we go to evolve new regexs, we can use the test suite to measure functionality equivalence 
    with the original test regex.
    """
    def generate_equivalence_test_suite(self, a_match, a_regex):
        # go through the whole known search string, changing letters until you find one which does not match.
        compiled_regex = re.compile(a_regex)
        if len(a_match.matches) > 0 :
            for i in range(0, len(a_match.search_string)):
                for char in [ a for a in range(ord('0'), ord('9'))] + [ord('a'), ord('Z') ]:
                    new_search_string = a_match.search_string[:i] + chr(char) + a_match.search_string[i+1:]
                    a_test_case_string = RegexTestString(new_search_string)
                    vals = self.time_regex_test_case(compiled_regex, a_test_case_string, 1)
                    if len(list(vals[1])) == 0:
                        self.test_cases.append(a_test_case_string)

    
    """
    Multiple search_strings should be used to guide toward generality.
    """
    def generate_iso8601_datetime_tests(self):
        # target: ^\d{4,}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+(?:[+-][0-2]\d:[0-5]\d|Z)$
        a_test_string = RegexTestString("2016-12-09T08:21:15.9+00:00")
        a_test_string.add_match(0,27)
        self.test_cases.append(a_test_string)
        
        self.generate_equivalence_test_suite(a_test_string,"^\d{4,}-[01]\d-[0-3]\dT[0-2]\d:[0-5]\d:[0-5]\d\.\d+(?:[+-][0-2]\d:[0-5]\d|Z)$")

        a_test_string = RegexTestString("2016-12-09T08:21:15.9+00:0") # this does not match at all! (what will our fitness function throw?)
        self.test_cases.append(a_test_string) 

        a_test_string = RegexTestString("2016-22-09T08:21:15.9+00:0") # 
        self.test_cases.append(a_test_string)

        a_test_string = RegexTestString("2016-22-09T08:21:15.9+00:00") # no match, as 22 is not a valid month
        self.test_cases.append(a_test_string) 

        a_test_string = RegexTestString("1911-02-19T22:35:42.3+08:43")
        a_test_string.add_match(0,27)
        self.test_cases.append(a_test_string) 
        
    def generate_string_tests(self):
        #a_test_string = RegexTestString("Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 14")
        #a_test_string.add_match(119,136) # 5c:0a:5b:63:4a:82

        a_test_string = RegexTestString("Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 140.105.63.164(50:06:04:92:53:44):80 TCP flags: ****S* len:60 ttl:32)")
        a_test_string.add_match(119,136) # 5c:0a:5b:63:4a:82
        a_test_string.add_match(161,178) # 50:06:04:92:53:44
        self.test_cases.append(a_test_string)

        a_test_string = RegexTestString("26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: \"none\" (in: eth0 119.63.193.196(5c:0a:5b:63:4a:82):4399 -> 140.105.63.1")
        a_test_string.add_match(109,126) # 5c:0a:5b:63:4a:82
        self.test_cases.append(a_test_string)

        a_test_string = RegexTestString(" -> 140.105.63.164(50:06:04:92:53:44):80 TCP flags: ****S* len:60 ttl:32)")
        a_test_string.add_match(19,36) # 50:06:04:92:53:44
        self.test_cases.append(a_test_string)

        a_test_string = RegexTestString(" -> 140.105.63.16450:06:04:92:53:44:80 TCP flags: ****S* len:60 ttl:32)")
        a_test_string.add_match(18,35) # 50:06:04:92:53:44
        self.test_cases.append(a_test_string)

        a_test_string = RegexTestString("Jan 12 06:26:20: ACCEPT service dns from 140.105.48.16 to firewall(pub-nic-dns), prefix: \"none\" (in: eth0 140.105.48.16(00:21:dd:bc:95:44):4263 -> 140.105.63.158(00:14:31:83:c6:8d):53 UDP len:76 ttl:62)")
        a_test_string.add_match(120,137)
        a_test_string.add_match(162,179)
        self.test_cases.append(a_test_string)

        a_test_string = RegexTestString("Jan 12 06:27:09: DROP service 68->67(udp) from 216.34.211.83 to 216.34.253.94, prefix: \"spoof iana-0/8\" (in: eth0 213.92.153.78(00:1f:d6:19:0a:80):68 -> 69.43.177.110(00:30:fe:fd:d6:51):67 UDP len:576 ttl:64)")
        a_test_string.add_match(128,145)
        a_test_string.add_match(167,184)
        self.test_cases.append(a_test_string)
        
    def generate_tests(self):
        #generate_string_tests()
        self.generate_iso8601_datetime_tests()
        #
        
class RegexTestString:
    def __init__(self,search_string):
        print("Added regex search string: "+search_string)
        self.search_string = search_string
        self.matches = list()

    def add_match(self, start, end):
        self.matches.append({'start': start,'end': end, 'matched_string': self.search_string[start:end]}) # ew?
        print("Added the following match: "+self.matches[-1].get("matched_string"))
#         for i in range(start,end-1):
#             for j in range(start+1,end):
#                 self.match.append(start=i,end=j, matched_string=self.search_string[i:j])
        
    def calc_match_errors(self,match_candidates):
        match_ranges=list()
        undesired_range = missing_range = 0
#        for match in match_candidates:
 #           match_ranges.append(match)

        for a_known_match in self.matches:
            # missing any of the desired extraction costs a lot
            missing_range += self.find_missing_range(a_known_match, match_candidates)
        for match_candidate in  match_candidates:
            undesired_range += self.find_undesired_range(match_candidate, self.matches)

        match_error = missing_range + undesired_range
        match_error += abs(len(match_candidates) - len(self.matches))

        return (match_error) 

    def find_missing_range(self, a_known_match, match_ranges):
        start = a_known_match.get("start")
        end = a_known_match.get("end")
        missing = end - start
        for i in range(start,end):
            found = False
            for m_range in match_ranges:
                if i >= m_range.start() and i < m_range.end():
                    found = True
            if found:
                missing -= 1
        return missing

    def find_undesired_range(self,match_candidate, known_matches):
        undesired_matched = 0
        for i in range(match_candidate.start(), match_candidate.end()):
            in_range=False
            for a_known_match in known_matches:
                start = a_known_match.get("start")
                end = a_known_match.get("end")
                if i >= start and i <= end:
                    in_range = True
            if not in_range:
                undesired_matched += 1
        return undesired_matched


    #             for a_match_candidate in match_candidates: # how much of our known match has gone unmatched?
#                 temp_match=0
#                 if a_matched_candidate.start < a_known_match.end or a_matched_candidate.end > a_known_match.start:
#                     unmatched_start = a_matched_candidate.start - a_known_match.start # should be positive, if negative then there is none unmatched
#                     unmatched_end = a_matched_candidate.end - a_known_match.start # should be positive
#                     temp_match = max(unmatched_end,0) + max(unmatched_start,0)


        
#     def compare(self,attempt_string):
#         error = distance(self.matched_string, attempt_string.group(0))
#         attempti=0
#         attempti += self.search_string.find(attempt_string.group(0))
#         if attempti < self.starti:
#             error+= self.starti-attempti
#         elif attempti > self.endi:
#             error+= attempti-self.endi
#         return error

    def get_search_string(self):
        return self.search_string

    
