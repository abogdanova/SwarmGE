import sys
import ast
from antlr4 import InputStream, CommonTokenStream, ParseTreeWalker, tree
from antlr4_generated.PCRELexer import PCRELexer
from antlr4_generated.PCREParser import PCREParser
from antlr4_generated.PCREListener import PCREListener
from pprint import pprint
from random import randrange

from algorithm.parameters import set_params


class PCREPrinter(PCREListener):
    
    def __init__(self):
        from algorithm.parameters import params
        self.grammar = params['BNF_GRAMMAR']
        self.genome = []
    
    generated_grammar="<toprule>  ::=  <element>|<recurserule>\n<recurserule>  ::=  <toprule><element>\n<element>  ::=  "
    
    def enterEveryRule(self, ctx):
        if len(ctx.children) == 1 and type(ctx.children[0]) is tree.Tree.TerminalNodeImpl :
            print("Actual  ", repr(ctx.getText()))
            # prod = ctx.getText()
            #
            # for NT in sorted(self.grammar.non_terminals.keys()):
            #     choices = self.grammar.rules[NT]['choices']
            #     for choice in choices:
            #         # print(choice['choice'])
            #         symbols = [sym['symbol'] for sym in choice['choice']]
            #         # print("\t", symbols)
            #         if prod in symbols:
            #             print("we have found where it lives")
            #             prod_index = symbols.index(prod)
            #             codon = randrange(self.grammar.rules[NT]['no_choices'],
            #                               self.grammar.codon_size,
            #                               self.grammar.rules[NT]['no_choices']) + prod_index
            #             print("Codon:", codon)
            #             self.genome.insert(0, codon)
            #
            #             quit()
            # # quit()
            
            self.generated_grammar += "\"" + ctx.getText() + "\"|"
        print("Entering: " + ctx.getText() + " : ")
        pprint(ctx.children)
            
    def enterParse(self,ctx):
        print("Bentering: " + ctx.getText())
        
    def exitParse(self,ctx):
        print("Exiting")


def main():
    
    # input = FileStream("a_regex.txt") # "\d.[9-n](\d.).(\w.).(\w.).(\d.).\w\d|y|!|!|Q") #FileStream(argv[1])

    # Bytestring won't work, FileStream/InputStream are from antlr4 library!
#    input = InputStream("\d.[9-n](\d.).(\w.).(\w.).(\d.).\w\d|y|!|!|Q") #FileStream(argv[1])
    input = InputStream("\d.[9-n](\d.)")
    
    lexer = PCRELexer(input)
    stream = CommonTokenStream(lexer)
    parser = PCREParser(stream)
    tree = parser.parse()
    
    
    
    # quit()
    
    pony_tree = get_ponyGE2Tree_from_antlrTree(tree)

def get_ponyGE2Tree_from_antlrTree(antlr_tree):
    printer = PCREPrinter()
    walker = ParseTreeWalker()
    walker.walk(printer, antlr_tree)
    print("Done!")
    print(printer.generated_grammar[:-1])
    return "yea"
    
if __name__ == '__main__':
    set_params(sys.argv)
    main()
