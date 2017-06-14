import sys
from algorithm.parameters import set_params
from representation.individual import Individual
import random
            
"""
Want to validate that these are in fact different runtimes
"""
def time_tester():
    if 'TEST_GENOME' in params and params['TEST_GENOME']:
        ind = Individual(params['TEST_GENOME'], None)
        print(ind.phenotype)
        for i in range(1000):
            ind.evaluate()
            print("{0:.20f} ".format(ind.fitness), flush=True, end="") # print all so we can bootstrap them in R
            print("")            
            
if __name__ == '__main__':
    set_params(sys.argv[1:])
    # test()
    time_tester()


def test():
    from utilities.representation.check_methods import print_semantic_lock
    
    genome1 = [12006, 4302, 77283, 6670, 24105, 46226, 94681, 61636, 50251, 61752, 85772, 2261, 60513, 55604, 96268, 79741, 89190, 51749, 88407, 46710, 416, 85163, 65133, 11657, 71721, 49944, 66223, 50387, 99691, 11624, 56639, 64872, 82572, 69767, 11624, 56639, 9950, 81660, 88479, 38172, 87707, 29673, 60473, 89036, 24436, 30523, 31016, 33995, 9950, 82572, 69767, 75297, 36154, 10299, 23302, 56687, 85479, 48651, 34858, 86147, 90437, 38664, 33995, 85985, 36916, 79229, 75448, 10701, 90437, 38664, 33995, 65301, 54699, 34514, 51586]
    
    genome2 = [36621, 95128, 37326, 34525, 1851, 2813, 63448, 90933, 68637, 25716, 5610, 63567, 67929, 91652, 30017, 77931, 45203, 33012, 11237, 10457, 35698, 24354, 46623, 30177, 55658, 73765, 3278, 64796, 92440, 94315, 72977, 937, 47324, 75948, 72324, 61606, 81398, 42648, 23445, 73765, 3278, 64796, 92440, 20811, 35424, 40471, 96837, 31331, 45311, 92440, 20811, 21329, 54924, 72967, 98870, 69180, 87435, 95742, 37959, 42581, 54376]
    
    genome3 = [98712, 31450, 38833, 87381, 31450, 38833, 81668, 16468, 71817, 38304, 73880, 49917, 84215, 60660, 50299, 54233, 23854, 81765, 42544, 15233, 14017, 93657, 11909, 205, 50229, 64706, 74868, 99563, 87986, 190, 61836, 78531, 2309, 64706, 74868, 99563, 98847, 50818, 25521, 10682, 190, 61836, 78531, 2309, 64706, 74868, 99563, 41772, 60331, 89889, 27500, 53308, 71258, 57865, 74665, 60335, 60874, 80970, 72771, 48275, 49853, 34419, 5404, 40661, 13208, 34081, 57227, 34921]
    
    ind1 = Individual(genome1, None)
    ind2 = Individual(genome2, None)
    ind3 = Individual(genome3, None)
    
    print("Target:     ", params['TARGET'])
    print("Phenotype 1:", ind1.phenotype)
    print("Phenotype 2:", ind2.phenotype)
    print("Phenotype 3:", ind3.phenotype)
    print("")
    
    ind1.evaluate()
    ind2.evaluate()
    ind3.evaluate()
    
    from utilities.stats.trackers import snippets
    
    print(len(snippets), "snippets")
    
    # for snippet in snippets:
    #     print(" ", snippet)
    
    print("")
    
    # print_semantic_lock(ind1.tree)
    # print("")
    # print_semantic_lock(ind2.tree)
    # print("")
    # print_semantic_lock(ind3.tree)
    # print("")

    print("Fitness 1:\t", ind1.fitness)
    print("Fitness 2:\t", ind2.fitness)
    print("Fitness 3:\t", ind3.fitness)
    print("")

    target = "\d.[9-n](\d.).(\w.).(\w.).(\d.).\w\d"
    phen_1 = "[(.\9[n](\d)*).]w.*((\w)(.)\d)(.\w\d)"
    phen_2 = "\d(\9-n\([(.)](\w)*)(\w)(.)\d.*.\w\d"
    phen_3 = "^d.[9-n](\d.).(\w.).++w.1.(\d.).\w\d"

    ind1 = semantic_subtree_swap(ind1)
    ind2 = semantic_subtree_swap(ind2)
    ind3 = semantic_subtree_swap(ind3)

    print("Phenotype 1:", ind1.phenotype)
    print("Phenotype 2:", ind2.phenotype)
    print("Phenotype 3:", ind3.phenotype)
    print("")

    ind1.evaluate()
    ind2.evaluate()
    ind3.evaluate()

    print("")

    print("Fitness 1:\t", ind1.fitness)
    print("Fitness 2:\t", ind2.fitness)
    print("Fitness 3:\t", ind3.fitness)


#
#
# class PCREPrinter(PCREListener):
#
#     def __init__(self):
#         from algorithm.parameters import params
#         self.grammar = params['BNF_GRAMMAR']
#         self.genome = []
#
#     generated_grammar="<toprule>  ::=  <element>|<recurserule>\n<recurserule>  ::=  <toprule><element>\n<element>  ::=  "
#
#     def enterEveryRule(self, ctx):
#         if len(ctx.children) == 1 and type(ctx.children[0]) is tree.Tree.TerminalNodeImpl :
#             print("Actual  ", repr(ctx.getText()))
#             # prod = ctx.getText()
#             #
#             # for NT in sorted(self.grammar.non_terminals.keys()):
#             #     choices = self.grammar.rules[NT]['choices']
#             #     for choice in choices:
#             #         # print(choice['choice'])
#             #         symbols = [sym['symbol'] for sym in choice['choice']]
#             #         # print("\t", symbols)
#             #         if prod in symbols:
#             #             print("we have found where it lives")
#             #             prod_index = symbols.index(prod)
#             #             codon = randrange(self.grammar.rules[NT]['no_choices'],
#             #                               self.grammar.codon_size,
#             #                               self.grammar.rules[NT]['no_choices']) + prod_index
#             #             print("Codon:", codon)
#             #             self.genome.insert(0, codon)
#             #
#             #             quit()
#             # # quit()
#
#             self.generated_grammar += "\"" + ctx.getText() + "\"|"
#         print("Entering: " + ctx.getText() + " : ")
#         pprint(ctx.children)
#
#     def enterParse(self,ctx):
#         print("Bentering: " + ctx.getText())
#
#     def exitParse(self,ctx):
#         print("Exiting")
#
#
# def main():
#
#     # input = FileStream("a_regex.txt") # "\d.[9-n](\d.).(\w.).(\w.).(\d.).\w\d|y|!|!|Q") #FileStream(argv[1])
#
#     # Bytestring won't work, FileStream/InputStream are from antlr4 library!
# #    input = InputStream("\d.[9-n](\d.).(\w.).(\w.).(\d.).\w\d|y|!|!|Q") #FileStream(argv[1])
#     input = InputStream("\d.[9-n](\d.)")
#
#     lexer = PCRELexer(input)
#     stream = CommonTokenStream(lexer)
#     parser = PCREParser(stream)
#     tree = parser.parse()
#
#
#
#     # quit()
#
#     pony_tree = get_ponyGE2Tree_from_antlrTree(tree)
#
#
# def get_ponyGE2Tree_from_antlrTree(antlr_tree):
#     printer = PCREPrinter()
#     walker = ParseTreeWalker()
#     walker.walk(printer, antlr_tree)
#     print("Done!")
#     print(printer.generated_grammar[:-1])
#     return "yea"
#

    

def time_tester_printer():
    """
    Want to validate that these are in fact different runtimes.
    
    :return: Nothing
    """
    
    for i in range(10000):

        # .X(.+)+XX;  & 0.0003474690020084381 \\
        individuals = list()
        genomes = [
            # .X(.+)XX;  & 0.00010399427264928818 \\
            [2, 12, 3, 4, 44, 2, 5, 4, 49, 2, 11, 3, 14, 11, 3, 15, 4, 44, 3, 12, 3, 5, 4, 49, 2, 5, 4, 49],
            # .X([0-c{76,}]?)\wXX;  & 0.00009754206985235214 \\
            [2, 12, 3, 4, 44, 2, 5, 4, 49, 2, 11, 3, 14, 13, 3, 10, 2, 13, 5, 3, 10, 5, 28, 3, 18, 4, 3, 17, 2, 16, 3, 12, 3, 4, 54, 3, 5, 5, 48, 3, 5, 4, 49, 2, 5, 4, 49],
            # .X([3-c{26,}]?)\wXX; 9.634345769882202e-05
            [2, 12, 3, 4, 44, 2, 5, 4, 49, 2, 11, 3, 14, 13, 3, 10, 2, 13, 5, 3, 13, 5, 28, 3, 18, 4, 3, 12, 2, 16, 3, 12, 3, 4, 54, 3, 5, 5, 48, 3, 5, 4, 49, 2, 5, 4, 49],
            # .X([9-c{70,}]?)\wXX; 9.745266288518906e-05
            [2, 12, 3, 4, 44, 2, 5, 4, 49, 2, 11, 3, 14, 13, 3, 10, 2, 13, 5, 3, 19, 5, 28, 3, 18, 4, 3, 17, 2, 10, 3, 12, 3, 4, 54, 3, 5, 5, 48, 3, 5, 4, 49, 2, 5, 4, 49],
            # stefans new regex: (?P<rulename><\S+>)\s*::=\s*(?P<production>(?:\#[^\r\n]*|(?!<\S+>\s*::=).+?)+)
            [2, 11, 3, 12, 3, 4, 51, 3, 5, 4, 41, 3, 4, 48, 3, 5, 5, 43, 3, 5, 5, 46, 3, 5, 5, 37, 3, 5, 5, 30, 3, 5, 5, 39, 3, 5, 5, 26, 3, 5, 5, 38, 3, 5, 5, 30, 3, 4, 50, 3, 4, 48, 3, 4, 54, 3, 5, 4, 44, 3, 4, 41, 2, 4, 50, 2, 14, 10, 3, 12, 3, 4, 54, 3, 5, 5, 44, 3, 4, 40, 3, 4, 46, 3, 4, 46, 3, 4, 49, 3, 4, 54, 2, 5, 5, 44, 3, 11, 2, 12, 3, 4, 51, 3, 5, 4, 41, 3, 4, 48, 3, 5, 5, 41, 3, 5, 5, 43, 3, 5, 5, 40, 3, 5, 5, 29, 3, 5, 5, 46, 3, 5, 5, 28, 3, 5, 5, 45, 3, 5, 5, 34, 3, 5, 5, 40, 3, 5, 5, 39, 2, 4, 50, 3, 14, 11, 3, 11, 2, 12, 3, 4, 51, 3, 4, 46, 3, 4, 54, 2, 4, 34, 3, 14, 13, 3, 14, 11, 3, 14, 9, 3, 14, 15, 3, 14, 10, 3, 10, 3, 12, 3, 4, 56, 3, 4, 54, 3, 5, 5, 43, 3, 4, 54, 2, 5, 5, 39, 3, 11, 3, 12, 3, 4, 51, 3, 4, 33, 3, 4, 48, 3, 4, 54, 3, 5, 4, 44, 3, 4, 41, 3, 4, 50, 3, 4, 54, 3, 5, 5, 44, 3, 4, 40, 3, 4, 46, 3, 4, 46, 2, 4, 49],
            # original PonyGE2 grammar rule extraction
            [2, 11, 3, 12, 3, 4, 51, 3, 5, 4, 41, 3, 4, 48, 3, 5, 5, 43, 3, 5, 5, 46, 3, 5, 5, 37, 3, 5, 5, 30, 3, 5, 5, 39, 3, 5, 5, 26, 3, 5, 5, 38, 3, 5, 5, 30, 3, 4, 50, 3, 4, 48, 3, 4, 54, 3, 5, 4, 44, 3, 4, 41, 2, 4, 50, 2, 14, 10, 3, 12, 3, 4, 54, 3, 5, 5, 44, 3, 4, 40, 3, 4, 46, 3, 4, 46, 3, 4, 49, 3, 4, 54, 2, 5, 5, 44, 3, 11, 2, 12, 3, 4, 51, 3, 5, 4, 41, 3, 4, 48, 3, 5, 5, 41, 3, 5, 5, 43, 3, 5, 5, 40, 3, 5, 5, 29, 3, 5, 5, 46, 3, 5, 5, 28, 3, 5, 5, 45, 3, 5, 5, 34, 3, 5, 5, 40, 3, 5, 5, 39, 2, 4, 50, 3, 14, 11, 3, 19, 10, 2, 11, 3, 12, 3, 4, 51, 3, 4, 49, 3, 4, 54, 2, 4, 34, 2, 12, 3, 4, 54, 2, 4, 34, 3, 14, 13, 3, 14, 11, 3, 14, 9, 3, 14, 15, 3, 14, 10, 3, 10, 3, 12, 3, 4, 56, 3, 4, 54, 3, 5, 5, 43, 3, 4, 54, 2, 5, 5, 39, 3, 11, 3, 12, 3, 4, 51, 3, 4, 33, 3, 4, 48, 3, 4, 54, 3, 5, 4, 44, 3, 4, 41, 3, 4, 50, 3, 4, 54, 3, 5, 5, 44, 3, 4, 40, 3, 4, 46, 3, 4, 46, 2, 4, 49],
        ]
     
        # individuals.append( Individual(genomes[0], None) )
        # individuals.append(  Individual(genomes[1], None) )
        # individuals.append(  Individual(genomes[2], None) )
        # individuals.append( Individual(genomes[3], None) )

        individuals.append( Individual(genomes[4], None) )
        individuals.append( Individual(genomes[5], None) )
        

        order = list(range(0,len(individuals))) # can we get rid of lazy eval already? :/

        random.shuffle(order)
        for i in order:
            individuals[i].evaluate()

        for ind in individuals:
            print("{0:.20f} ".format(ind.fitness), flush=True, end="") # print all so we can bootstrap them in R
        print("")
        # print("{0:.10f}".format(orig_ind.fitness - evo_ind.fitness))
            
            
if __name__ == '__main__':
    set_params(sys.argv)
    # test()
    time_tester()

