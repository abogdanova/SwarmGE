
from Levenshtein import distance 
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
    Fitness function for checking regex matching which sums functionality and time.
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
#        regex_string="5"
        try:
            compiled_regex = re.compile(regex_string)
            eval_results = self.test_regex(compiled_regex)
            fitness = self.calculate_fitness(eval_results)
#            if "5" in regex_string:
#                print(regex_string + ": {}".format(fitness))
#                sys.exit()
            if fitness >= 0: # (we should use multi-objective/pareto front)
                return fitness + (len(regex_string)/10000000000) #fitness # error is first, length second
            else:
                self.time=True
                return fitness # + (len(regex_string)/10000000000)  # performance only 

        except:
#            print(traceback.format_exc())
#            sys.exit()
            return 100000

    def calculate_fitness(self,eval_results):
        result_error=0
        time_sum=0.0
        for a_result in eval_results:
            time_sum += a_result[0] /  a_result[2]
            if a_result[1] == None: # no match 
                result_error += 100 * (len(a_result[3].search_string)) #+ len(a_result[3].matched_string))
            else: # a match which may be the empty string
                result_error += a_result[3].calc_match_errors(a_result[1])
        if result_error >1:
            fitness = result_error
        else:
            fitness = time_sum
        #fitness = time_sum + result_error
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
    Given a test string and the desired match,
    Break the desired match into substrings,
    these substrings give us a gradient.
    Multiple search_strings should be used to guide toward generality. 
    """
    def generate_tests(self):
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
        start_errors=list()
        end_errors=list()
        match_candidates_length=-1
        # is it cheaper to make a copy and remove characters as they are matched, or create a set of all sub-snippets and what ones the candidate matches?
        match_error = 0
        for a_known_match in self.matches:
            match_ranges=list()
            for match in match_candidates:
                match_candidates_length+=1
                if match.end() != match.start():
                    # how mutch of the match we're looking for are we missing?
                    start_diff = match.start() - a_known_match.get("start") 
                    end_diff = (a_known_match.get("end")) - match.end()
                    if start_diff < 0: # missing the start or end costs a bit
                        match_error+= abs(start_diff)
                    if end_diff < 0:
                        match_error+= abs(end_diff)-1
                    if match.start() > a_known_match.get("end") or match.end() < a_known_match.get("start"): # we totally missed
                        match_error+= a_known_match.get("end")  - a_known_match.get("start")
                    else: # how much of this known match did we get?
                        match_ranges.append(match)
                    #start_errors.append(abs(start_diff))
                    #end_errors.append(abs(end_diff)) # add error if they're the same
                else:
                    match_error +=1
                
            # missing any of the desired extraction costs a lot
            missing_range = self.find_missing_range(a_known_match.get("start"), a_known_match.get("end"), match_ranges)
            range_length = (a_known_match.get("end") - a_known_match.get("start"))
            if missing_range == range_length: # we've missed the whole thing
                match_error += missing_range * (range_length * 10)
            else:
                match_error += missing_range * range_length
            
            #if len(start_errors) == 0:
            #    start_errors.append(len(self.search_string))
            #if len(end_errors) == 0:
            #    end_errors.append(len(self.search_string))
        if match_candidates_length < 0:
            match_candidates_length = match_error = 50*len(self.search_string)
        #print("Matches: {}".format(match_candidates_length))
        #if (sum(start_errors+end_errors) + match_error) == 0:
        #    print("aagh")
        return (match_error) + (match_candidates_length * 5) # sum(start_errors+end_errors) + 

    def find_missing_range(self,start, end, match_ranges):
        missing = end - start
        for i in range(start,end):
            found = False
            for m_range in match_ranges:
                if i >= m_range.start() and i < m_range.end():
                    found = True
            if found:
                missing -= 1
        return missing
                

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

    
