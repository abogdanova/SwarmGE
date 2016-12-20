import sys
# import ast
# from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker, tree
# from antlr4_generated.PCRELexer import PCRELexer
# from antlr4_generated.PCREParser import PCREParser
# # from antlr4_generated.PCREListener import PCREListener
from pprint import pprint
# from random import randrange

from algorithm.parameters import set_params
from operators.semantic_swap import semantic_subtree_swap
from representation.individual import Individual
from algorithm.parameters import params
import random
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

    
"""
Want to validate that these are in fact different runtimes
"""
def time_tester():

    
    # Matches the evolved regex: ([0-9eJFa-f]{2}[:sN-]){5}([0F0-9{2}a-f9!L\djy7Fa-f1]{2}); 6.752903573215008e-05
    evolved_genome = [80920, 44560, 43796, 37197, 59612, 95024, 43035, 79197, 48738, 27160, 83247, 14152, 15068, 23893, 91233, 98352, 34319, 3775, 81581, 99913, 14196, 75140, 29628, 46028, 34834, 14726, 14368, 74369, 99712, 96642, 99769, 21675, 99680, 25196, 96330, 39971, 75769, 84072, 74381, 36832, 75564, 75716, 65585, 17155, 83569, 7896, 61362, 63036, 56016, 26995, 11993, 20439, 98037, 95159, 77879, 86328, 45161, 63036, 56016, 26995, 3664, 47636, 71898, 45994, 89995, 65701, 74026, 13852, 37197, 59612, 95024, 5781, 93825, 1610, 30579, 19246, 29249, 98352, 34319, 34834, 82421, 14639, 15906, 15469, 51427, 26714, 35131, 8939, 63593, 12651, 72689, 10217, 21093, 10590, 44769, 61313, 7045, 99174, 55093, 44545, 22581, 68256, 55746, 2426, 99769, 21675, 95384, 79671, 23129, 34023, 67166, 62012]




    for i in range(100000):
        # original regex: ([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2}); 0.00014590489445254207
        original_genome = [80920, 44560, 43796, 37197, 59612, 95024, 43035, 79197, 48738, 38530, 83247, 14152, 15068, 23893, 91233, 98352, 34319, 3775, 81581, 99913, 89674, 75140, 29628, 46028, 34834, 14726, 14368, 74369, 99712, 57049, 99769, 21675, 99680, 25196, 96330, 39971, 75769, 84072, 74381, 36832, 75564, 75716, 65585, 17155, 83569, 7896, 61362, 63036, 56016, 26995, 11993, 20439, 98037, 95159, 77879, 86328, 45161, 75140, 29628, 46028, 3664, 47636, 71898, 45994, 89995, 65701, 74026, 13852, 37197, 59612, 95024, 43035, 79197, 48738, 38530, 83247, 14152, 15068, 23893, 91233, 98352, 34319, 3775, 81581, 99913, 89674, 75140, 29628, 46028, 34834, 14726, 14368, 74369, 99712, 57049, 99769, 21675, 99680, 25196, 96330, 39971, 75769, 79671, 23129, 34023, 67166, 62012]
        orig_ind = Individual(original_genome, None)

        # (\w*:){5}\w.
        shortened_regex = [95232, 10216, 13674, 13315, 12827, 98619, 49938, 14433, 1985, 83700, 58001, 44484, 70991, 47127, 47574, 3745, 14403, 6124, 16345, 68449, 16692]
        evo_ind = Individual(shortened_regex, None)

    
        if bool(random.getrandbits(1)):
            evo_ind.evaluate()
            orig_ind.evaluate()
        else:
            evo_ind.evaluate()
            orig_ind.evaluate()
        print("{0:.10f}".format(orig_ind.fitness - evo_ind.fitness))
            
            
if __name__ == '__main__':
    set_params(sys.argv)
    # test()
    time_tester()
