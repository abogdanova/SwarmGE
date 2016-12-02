import sys
#from cStringIO import StringIO
from io import StringIO 
from antlr4 import *
from PCRELexer import PCRELexer
from PCREParser import PCREParser
from PCREListener import PCREListener
from pprint import pprint

class PCREPrinter(PCREListener):
    generated_grammar="<toprule>  ::=  <element>|<recurserule>\n<recurserule>  ::=  <toprule><element>\n<element>  ::=  "
    
    def enterEveryRule(self,ctx):
#        pp=pprint.PrettyPrinter(indent=4)
        if len(ctx.children) == 1 and type(ctx.children[0]) is tree.Tree.TerminalNodeImpl :
            self.generated_grammar += "\"" + ctx.getText() +"\"|"
        print( "Entering: " + ctx.getText() + " : ")
        pprint(ctx.children)
            
    def enterParse(self,ctx):
        print( "Entering: " + ctx.getText() )
        
    def exitParse(self,ctx):
        print("Exiting")


def main(argv):
    # input = FileStream("a_regex.txt") # "\d.[9-n](\d.).(\w.).(\w.).(\d.).\w\d|y|!|!|Q") #FileStream(argv[1])

    # Bytestring won't work, FileStream/InputStream are from antlr4 library!  
#    input = InputStream("\d.[9-n](\d.).(\w.).(\w.).(\d.).\w\d|y|!|!|Q") #FileStream(argv[1])
    input = InputStream("\d.[9-n](\d.)")
    
    lexer = PCRELexer(input)
    stream = CommonTokenStream(lexer)
    parser = PCREParser(stream)
    tree = parser.parse()
    pony_tree = get_ponyGE2Tree_from_antlrTree(tree)

def get_ponyGE2Tree_from_antlrTree(antlr_tree):
    printer = PCREPrinter()
    walker = ParseTreeWalker()
    walker.walk( printer, antlr_tree )
    print("Done!")
    print(printer.generated_grammar[:-1])
    return "yea"
    
if __name__ == '__main__':
    main(sys.argv)        
        
