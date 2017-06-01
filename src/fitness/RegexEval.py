import re
import time, timeit
import traceback
import sys
from algorithm.parameters import params
from representation.individual import Individual
from multiprocessing import Process, Queue
# from experimental.database import Session, Snippets, TestCase, Relation

# Author: Brendan Cody-Kenny - codykenny at gmail

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

"""
TODO
Apache log file
([0-9a-f.:]+)\s+(-|.+?)\s+(-|.+?)\s+\[([0-9]{2}\/[a-z]{3}\/[0-9]{4}\:[0-9]{2}:[0-9]{2}:[0-9]{2}[^\]]*)\] \"(\S+?)\s(\S*?)\s{0,1}(\S+?)\" ([0-9|\-]+) ([0-9|\-]+)
"""


class RegexEval:
    """
    Fitness function for regex (lower fitness value is better)
    Fitness = functionality error + time
    The regex is presented with a number of strings, resulting matches are
    checked for correctness against known correct answers.
    Sum of wall-clock time taken to execute the test strings.
    """
    
    maximise = False  # lower fitness value is better
    default_fitness = 100000

    def __init__(self):
        """
        The seed program is needed by the fitness function to generate test
        data but individual needs the fitness function! :/
        This could be done as part of the parameters setup,
        but keeping it here for the moment as it's regex specific

        :param self:
        :return:
        """
        self.test_cases = []
        self.seed_regex = None
        self.time = True
        self.q = Queue()
        self.pstartup = Process(target=self.call_fitness,
                                name="self.call_fitness")
        self.prunner = None
        
    def call_fitness(self, individual):
        """
        This method is called when this class is instantiated with an
        individual (a regex)
        
        :param individual:
        :param q:
        :return:
        """
        
        regex_string = individual.phenotype
        try:
            compiled_regex = re.compile(regex_string)
            eval_results = self.test_regex(compiled_regex)
            result_error, time_sum = self.calculate_fitness(eval_results)
            fitness = result_error + time_sum

            # check how similar the mutated regex is to the seed regex, character by character. Use Levenshtein distance either?
            #if 'SEED_GENOME' in params and params['SEED_GENOME']:
            #   similarity_score = self.calculate_similarity_score(regex_string)
            #   if(similarity_score > 1):
            #        fitness += (similarity_score)
               #else:
               #     fitness += time_sum


            # phenotype or genome length?
            # return fitness + (len(individual.phenotype)/10000) #fitness # error is first, length second
            # if fitness >= 1: # If there is a functionality error, we don't really care about time
            #     return fitness + (len(individual.genome)/10000) #fitness # error is first, length second
            #     #return fitness + (len(regex_string)/10000) #fitness # error is first, length second
            # else:
            #     self.time=True
            #     return fitness

            # We are running this code in a thread so put the fitness on the
            # queue so it can be read back by the first
            self.q.put(fitness + (len(individual.phenotype)/100))

        except:
            # if the regex is broken, or the thread is timedout, return a
            # really bad fitness
            self.q.put(self.default_fitness)

    def calculate_similarity_score(self, regex_string):
        """
        Check how similar a mutated regex is to the seed regex. It is an
        alternative measure to Levenshtein distance (experimental)
        
        :param regex_string:
        :return:
        """
        
        char_same_count = 0
        if 'SEED_GENOME' in params and params['SEED_GENOME']:
            seed_ind = individual.Individual(params['SEED_GENOME'], None)
            seed_string = seed_ind.phenotype
            if regex_string == seed_string:
                return len(seed_string)
            for i in range(len(regex_string)):
                for j in range(i,len(seed_string)):
                    if regex_string[i] == seed_string[j]:
                        char_same_count += 1
                        break
        return char_same_count
    
    def calculate_fitness(self, eval_results):
        """
        Sum the functionality error with time (and any other fitness penalties
        you want to add, e.g. length of regex)
        
        :param eval_results:
        :return:
        """
        
        result_error = 0
        time_sum = 0.0
        for a_result in eval_results:
            time_sum += a_result[0]
            result_error += a_result[3].calc_match_errors(list(a_result[1]))

        # if fitness == seed_fitness:
        #     fitness = 100 * len(a_result)  # identical result to seed
        # penalised
        
        return result_error, time_sum

    def test_regex(self, compiled_regex):
        """
        Iterate through test cases
        
        :param compiled_regex:
        :return:
        """
        
        results = list()
        testing_iterations = 1
        # do a quick test to time the longest test case (which is also the last in the list)
        # quick_test = self.time_regex_test_case(compiled_regex, self.test_cases[len(self.test_cases)-1], testing_iterations)
        #if quick_test[3].calc_match_errors(list(quick_test[1])) < 0 : # Ideally we only time a program if it is funtionally correct
        #    testing_iterations = 10000000
        for test_case in self.test_cases:
            results.append(self.time_regex_test_case(compiled_regex, test_case,
                                                     testing_iterations))
        return results

    def time_regex_test_case(self, compiled_regex, test_case, iterations):
        """
        Execute and time a single regex on a single test case
        
        :param compiled_regex:
        :param test_case:
        :param iterations:
        :return:
        """
        
        repeats = 3
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

    def generate_equivalence_test_suite_replacement(self, a_match, compiled_regex):
        """
        This is a 'booster' for test suite generation. We know a single good
        match, and we can use that to find search strings which do not
        contain a match. Given a regex, generate/discoverB a test suite of
        examples which match, and those that don't. The test suite is used to
        define (or outline) the functionality boundaries of the regex. When we
        go to evolve new regexs, we can use the test suite to measure
        functionality equivalence with the original test regex.
            
        :param a_match:
        :param compiled_regex:
        :return:
        """
        
        # go through the whole known search string, changing letters until you find one which does not match.
        # compiled_regex = re.compile(a_regex)
        if len(a_match.matches) > 0:
            for i in range(0, len(a_match.search_string)):
                for char in [a for a in range(ord('0'), ord('9'))] + \
                        [ord('a'), ord('Z')]:
                    new_search_string = a_match.search_string[:i] + \
                                        chr(char) + \
                                        a_match.search_string[i+1:]
                    a_test_case_string = RegexTestString(new_search_string)
                    vals = self.time_regex_test_case(compiled_regex,
                                                     a_test_case_string, 1)
                    if len(list(vals[1])) == 0:
                        self.test_cases.append(a_test_case_string)

    def generate_equivalence_test_suite_length(self, a_match, compiled_regex):
        """
        Generate shorter or longer test cases, add those which do not match
        
        :param a_match:
        :param compiled_regex:
        :return:
        """
        
        # add and remove characters from the string until we find a regex which fails
        # compiled_regex = re.compile(a_regex)
        if len(a_match.matches) > 0:
    
            # check string with one character added at the front
            new_search_string = 'a' + a_match.search_string
            
            self.add_test_case_if_fails(new_search_string, compiled_regex)

            # check string with one character added at the end
            new_search_string = a_match.search_string+'a'
            self.add_test_case_if_fails(new_search_string, compiled_regex)

            for i in range(len(a_match.search_string)-1):
                new_search_string = a_match.search_string[i:]  # TODO: refactor this
                self.add_test_case_if_fails(new_search_string, compiled_regex)
            
            for i in range(len(a_match.search_string)-1):
                new_search_string = a_match.search_string[:i]  # TODO: refactor this
                self.add_test_case_if_fails(new_search_string, compiled_regex)

    def add_test_case_if_fails(self, new_search_string, compiled_regex):
        """
        run a test case, if it fails, add it to the suite of tests
        
        :param new_search_string:
        :param compiled_regex:
        :return:
        """
        a_test_case_string = RegexTestString(new_search_string)
        vals = self.time_regex_test_case(compiled_regex, a_test_case_string, 1)
        if len(list(vals[1])) == 0:
            self.test_cases.append(a_test_case_string)

    def add_test(self, regex_string, match):
        """
        Add a test safely
        
        :param regex_string:
        :param match:
        :return:
        """
        a_test_string = RegexTestString(regex_string)
        if match and len(match) == 2:  # should be e.g. [0,27]
            a_test_string.add_match(match[0], match[1])
        self.test_cases.append(a_test_string)
        return a_test_string
            
    def generate_tests(self):
        """
        Generate generic tests
        
        :return:
        """

        test_gen_method = getattr(self, params['FITNESS_TEST_SUITE'])
        test_gen_method()
        # can be any of these:
        # self.generate_regex_mac_search_string_tests()
        # self.generate_catastrophic_csv()
        # self.generate_iso8601_datetime_tests()
        # self.generate_macaddress_validation_tests()
        # self.generate_email_validation_tests()
        # self.generate_scientific_number_tests()
        # self.generate_PonyGE2_Grammar_File_Rule_tests()
        # self.generate_catastrophic_QT3TS_tests()
        # self.generate_d3_interpolate_number()
        print("Number of test cases: {}".format(len(self.test_cases)))
        
    def __call__(self, individual):
        """
        When this class is instantiated with individual, evalute in a new
        process, timeout and kill process if it runs for 5 seconds.
        Generating new processes is expensive, rework the code to reuse a
        process.
            
        :param individual:
        :return:
        """
    
        # Start a session to allow us to talk to the databases.
        # session = Session()
        session = None
        
        if not self.seed_regex:
            # Need to have this like this until we figure out how to
            # generate an individual during initialisation of the fitness
            # function. Note that grammar class not initialised yet :(
            self.seed_regex = Individual(params['SEED_GENOME'],
                                         None).phenotype
            self.generate_test_suite(self.seed_regex, session)
        
        self.pstartup._args = (individual,)
        self.pstartup.start()
        self.prunner = self.pstartup
        self.pstartup = Process(target=self.call_fitness,
                                name="self.call_fitness")
        
        # Set one second time limit for running thread.
        self.prunner.join(1)
        
        # If thread is active
        if self.prunner.is_alive():
            # After one second, if prunner is still running, kill it.
            print("Regex evaluation timeout reached, "
                  "killing evaluation process")
            self.prunner.terminate()
            self.prunner.join()
            return self.default_fitness
        
        else:
            return self.q.get()
        
    def generate_test_suite(self, regex_string, session):
        # do some test generation
        # find a string which the regex is able to match against
        # find the minimal variant of this string which does not match
        # test strategies - length, values
        
        # collect strings which identify the different regex
        # cache and reuse these (read/write to a file before/after GP)
        known_test_strings=["5C0A5B634A82",
                            "Jan 12 06:26:20: ACCEPT service dns from 140.105.48.16 to firewall(pub-nic-dns), prefix: \"none\" (in: eth0 140.105.48.16(00:21:dd:bc:95:44):4263 -> 140.105.63.158(00:14:31:83:c6:8d):53 UDP len:76",
                            "Jan 12 06:27:09: DROP service 68->67(udp) from 216.34.211.83 to 216.34.253.94, prefix: \"spoof iana-0/8\" (in: eth0 213.92.153.78(00:1f:d6:19:0a:80):68 -> 69.43.177.110(00:30:fe:fd:d6:51):67 UDP le"
                            "Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: ",
                            "Jan 12 06:26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: ",
                            "26:19: ACCEPT service http from 119.63.193.196 to firewall(pub-nic), prefix: ",
                            " -> 140.105.63.164(50:j6:04:92:53:44):80 TCP flags: ****S* len:60 ttl:32)sdkfjhaklsjdhfglksjhdfgk",
                            " -> 140.105.63.16(50:06:04:9r:53:44):80 TCP flags: ****S* len:60 ttl:32)ssjdhfglksjhdfgk",
                            "Jan 12 06:26:20: ACCEPT service dns from 140.105.48.16 to firewall(pub-nic-dns), prefix: ",
                            "Jan 12 06:27:09: DROP service 68->67(udp) from 216.34.211.83 to 216.34.253.94, prefix: ",
                            "105.63.1650:06:04:92:53:44:80",
                            " -> 140.105.63.164(50:06:g4:92:53:44):80 TCP flags: ****S* len:60 ttl:32)",
                            " -> 140.105.63.164(50:06:54:92:r3:44):80 TCP flags: ****S* len:60 ttl:32)",
                            "1,2,3,4,5,6,7,8,9,10,11,12,13777,5P,5,5,6,5P",
                            "1,2,3,4,5,6,7,8,9,10,11,12,13777,24,5P",
                            "1,2,3,4,5,6,7,8,9,10,11,12,13777,243,3P",
                            "1,2,3,4,5,6,7,8,9,10,11,12,13777,P",
                            "1,2,3,4,5,6,7,8,9,10,11,12,P",
                            "1,2,3,4,5,6,7,8,9,10,11,P",
                            "1,2,3,4,5,6,7,8,9,10,11,3P",
                            "1,2,3,4,5,6,7,8,9,10,P",
                            "codykenny@gmailcom",
                            "2016-12-09T08:21:15.9+00:00",
                            "2016-12-09T08:21:15.9+00:0",
                            "2016-22-09T08:21:15.9+00:00000000000",
                            "2016-22-09T08:21:15.9+00:00",
                            "1911-02-19T22:35:42.3+08:43",
                            "2016-09-05T15:22:26.286Z",
                            "230.234E-10",
                            "971.829E+26",
                            "3566",
                            "4",
                            "-7",
                            "+94",
                            "            36",
                            "78      ",
                            "87465.345345",
                            "2346.533",
                            "0.045e-10",
                            "3566.",
                            ".3456",
                            "<string> ::= <letter>|<letter><string>",
                            "hryxioXcXXdornct",
                            "bbbbXcyXXaaa",
                            "230.234E-10",
                            "971.829E+26",
                            "3566",
                            "4",
                            "-7",
                            "+94",
                            "            36",
                            "78      ",
                            "87465.345345",
                            "2346.533",
                            "  3566.   ",
                            " .3456  ",
                            "a46b  ",
                            "0.045e-10",
                            "aXXXXas",
                            "<s_char>        ::= !|\"#\"|$|%|&|\(|\)|*|+|,|-|.|\/|:|;|\"<\"|=|\">\"|?|@|\[|\\|\]|^|_|\"`\"|{|}|~|\"|\"|'\"'|\"'\"|\" \""
                            "!|\"#\"|$|%|&|\(|\)|*|+|,|-|.|\/|:|;|\"<\"|=|\">\"|?|@|\[|\\|\]|^|_|\"`\"|{|}|~|\"|\"|'\"'|\"'\"|\" \"",
                            "<A_Z>           ::= A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z",
                            "A|B|C|D|E|F|G|H|I|J|K|L|M|N|O|P|Q|R|S|T|U|V|W|X|Y|Z",
        ]
        
        compiled_regex = re.compile(regex_string)
               
        for test_string in known_test_strings:
            self.generate_tests_if_string_match(compiled_regex, test_string)

        # if we don't have any known test strings, see if the regex matches
        # itself.
        self.generate_tests_if_string_match(compiled_regex, regex_string)
        
        print("Number of test cases in suite:", len(self.test_cases))
             
        if len(self.test_cases) == 0:
            raise ValueError("PonyGE2 couldn't find any passing test cases "
                             "for this regex!")
        
        # else:
        #     for i, case in enumerate(self.test_cases):
        #         if not case.matches:
        #             new_test_case = TestCase(input=case.search_string,
        #                                      output=None,
        #                                      start=None,
        #                                      end=None)
        #             session.add(new_test_case)
        #         else:
        #             for match in case.matches:
        #                 new_test_case = TestCase(input=case.search_string,
        #                                          output=match['matched_string'],
        #                                          start=match['start'],
        #                                          end=match['end'])
        #                 session.add(new_test_case)
                
    def add_re_match_to_test(self, vals, passing_test_string):
        """
        take matching values as found by the regex library, and add them to our
        RegexTestString object
        
        :param vals:
        :param passing_test_string:
        :return:
        """

        for a_match in vals[1]:  # this vals[1] business is not good
            passing_test_string.add_match(a_match.start(), a_match.end())

        return passing_test_string

    def generate_tests_if_string_match(self, compiled_regex, test_string):
        
        a_test_candidate = RegexTestString(test_string)
        vals = self.time_regex_test_case(compiled_regex, a_test_candidate, 1)
        
        if len(list(vals[1])) > 0:  # the regex found a match, add it
            a_positive_test = self.add_re_match_to_test(vals, a_test_candidate)

            self.test_cases.append(a_positive_test)
            
            # now find regex which negate
            self.generate_equivalence_test_suite_replacement(a_positive_test,
                                                             compiled_regex)
            self.generate_equivalence_test_suite_length(a_positive_test,
                                                        compiled_regex)
    

class RegexTestString:
    """
    Class which contains a test string and matches
    (We should probably just use the types which re library uses)
    """
        
    def __init__(self, search_string):
        
        # print("Added regex search string: "+search_string)
        self.search_string = search_string
        self.matches = []

    def add_match(self, start, end):
        
        self.matches.append({'start': start,
                             'end': end,
                             'matched_string': self.search_string[start:end]})
        
    def calc_match_errors(self, match_candidates):

        undesired_range = missing_range = 0

        for a_known_match in self.matches:
            # missing any of the desired extraction costs a lot
            missing_range += self.find_missing_range(a_known_match,
                                                     match_candidates)
        for match_candidate in match_candidates:
            undesired_range += self.find_undesired_range(match_candidate,
                                                         self.matches)

        match_error = missing_range + undesired_range
        match_error += (abs(len(match_candidates) - len(self.matches)))

        return match_error

    def find_missing_range(self, a_known_match, match_ranges):
        start = a_known_match.get("start")
        end = a_known_match.get("end")
        missing = end - start
        
        for i in range(start, end):
            found = False
            
            for m_range in match_ranges:
                
                if m_range.start() <= i < m_range.end():
                    found = True
            
            if found:
                missing -= 1
        
        return missing

    def find_undesired_range(self, match_candidate, known_matches):
        undesired_matched = 0
        
        for i in range(match_candidate.start(), match_candidate.end()):
            in_range = False
        
            for a_known_match in known_matches:
                start = a_known_match.get("start")
                end = a_known_match.get("end")
        
                if start <= i <= end:
                    in_range = True
            
            if not in_range:
                undesired_matched += 1
        
        return undesired_matched

    def get_search_string(self):
        
        return self.search_string
