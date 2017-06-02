import re
import time, timeit
import traceback
import sys
import fitness.regextesting.RegexTest
import fitness.regextesting.RegexTestGenerator as TestGen
from fitness.regextesting.RegexTimer import time_regex_test_case
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
            # length of the phenotype puts parsimony pressure toward shorter regex
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
        testing_iterations = 2
        # do a quick test to time the longest test case (which is also the last in the list)
        # quick_test = self.time_regex_test_case(compiled_regex, self.test_cases[len(self.test_cases)-1], testing_iterations)
        #if quick_test[3].calc_match_errors(list(quick_test[1])) < 0 : # Ideally we only time a program if it is funtionally correct
        #    testing_iterations = 10000000
        for test_case in self.test_cases:
            results.append(self.time_regex_test_case(compiled_regex, test_case,
                                                     testing_iterations))
        return results
        
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
            # TestGen.generate_test_suite(self.seed_regex, session)
            self.test_cases = TestGen.generate_test_suite(self.seed_regex)
        
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
        
  
