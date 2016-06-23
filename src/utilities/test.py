import matplotlib

matplotlib.use('Agg')
from random import seed
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')
from re import search, findall
from datetime import datetime
from itertools import groupby
from math import floor
from representation import tree
from utilities import helper_methods

CODON_SIZE = 100000

now = datetime.now()
SEED = now.microsecond # 637553#
print ("Seed:\t", SEED)
seed(SEED)

SAVE = True
""" Turn on if you want to save graphs of the individuals"""

class Grammar(object):
    """ Context Free Grammar """
    NT = "NT" # Non Terminal
    T = "T" # Terminal

    def __init__(self, file_name):
        if file_name.endswith("pybnf"):
            self.python_mode = True
        else:
            self.python_mode = False
        self.rules = {}
        self.permutations = {}
        self.non_terminals, self.terminals = {}, []
        self.start_rule = None
        self.min_path = 0
        self.max_arity = 0
        self.codon_size = CODON_SIZE
        self.read_bnf_file(file_name)
        self.check_depths()
        self.check_permutations()

    def read_bnf_file(self, file_name):
        """Read a grammar file in BNF format"""
        # <.+?> Non greedy match of anything between brackets
        non_terminal_pattern = "(<.+?>)"
        rule_separator = "::="
        production_separator = "|"

        # Read the grammar file
        for line in open(file_name, 'r'):
            if not line.startswith("#") and line.strip() != "":
                # Split rules. Everything must be on one line
                if line.find(rule_separator):
                    lhs, productions = line.split(rule_separator)
                    lhs = lhs.strip()
                    if not search(non_terminal_pattern, lhs):
                        raise ValueError("lhs is not a NT:", lhs)
                    self.non_terminals[str(lhs)] = {"id":lhs, "min_steps":9999999999999, "expanded":False, 'recursive':True, 'permutations':None, 'b_factor':0}
                    if self.start_rule is None:
                        self.start_rule = (lhs, self.NT)
                    # Find terminals
                    tmp_productions = []
                    for production in [production.strip()
                                       for production in
                                       productions.split(production_separator)]:
                        tmp_production = []
                        if not search(non_terminal_pattern, production):
                            self.terminals.append(production)
                            tmp_production.append([production, self.T, 0, False])
                        else:
                            # Match non terminal or terminal pattern
                            # TODO does this handle quoted NT symbols?
                            for value in findall("<.+?>|[^<>]*", production):
                                if value != '':
                                    if not search(non_terminal_pattern,
                                                     value):
                                        symbol = [value, self.T, 0, False]
                                        self.terminals.append(value)
                                    else:
                                        symbol = [value, self.NT]
                                    tmp_production.append(symbol)
                        tmp_productions.append(tmp_production)
                    # Create a rule
                    if not lhs in self.rules:
                        self.rules[lhs] = tmp_productions
                    else:
                        raise ValueError("lhs should be unique", lhs)
                else:
                    raise ValueError("Each rule must be on one line")

    def check_depths(self):
        """ Run through a grammar and find out the minimum distance from each
            NT to the nearest T. Useful for initialisation methods where we
            need to know how far away we are from fully expanding a tree
            relative to where we are in the tree and what the depth limit is.

            For each NT in self.non_terminals we have:
             - 'id':        the NT itself
             - 'min_steps': its minimum distance to the nearest T (i.e. its
                            minimum distance to full expansion
             - 'expanded':  a boolean indicator for whether or not it is fully
                            expanded
             - 'b_factor':  the branching factor of the NT (now many choices
                            does  the rule have)
             - 'recursive': is the NT recursive
             - 'permutations':  the number of possible permutations and
                                combinations that this NT can produce
                                (excluding recursive rules)
        """

        for i in range(len(self.non_terminals)):
            for NT in self.non_terminals:
                vals = self.non_terminals[NT]
                vals['b_factor'] = len(self.rules[NT])
                if not vals['expanded']:
                    choices = self.rules[NT]
                    terms = 0
                    for choice in choices:
                        if not (all([sym[1] == self.T for sym in choice]) == False):
                            terms += 1
                    if terms:
                        # this NT can then map directly to a T
                        vals['min_steps'] = 1
                        vals['expanded'] = True
                    else:
                        # There are NTs remaining in the production choices
                        for choice in choices:
                            NT_s = [sym for sym in choice if sym[1] == self.NT]
                            NT_choices = list(NT_s for NT_s,_ in groupby(NT_s))
                            if len(NT_choices) > 1:
                                if all([self.non_terminals[item[0]]['expanded']
                                        for item in NT_choices]):
                                    if vals['expanded'] and (vals['min_steps'] > max([self.non_terminals[item[0]]['min_steps'] for item in NT_choices]) + 1):
                                        vals['min_steps'] = max([self.non_terminals[item[0]]['min_steps'] for item in NT_choices]) + 1
                                    elif not vals['expanded']:
                                        vals['expanded'] = True
                                        vals['min_steps'] = max([self.non_terminals[item[0]]['min_steps'] for item in NT_choices]) + 1
                            else:
                                child = self.non_terminals[NT_choices[0][0]]
                                if child['expanded']:
                                    if vals['expanded'] and (vals['min_steps'] > child['min_steps'] + 1):
                                        vals['min_steps'] = child['min_steps'] + 1
                                    else:
                                        vals['expanded'] = True
                                        vals['min_steps'] = child['min_steps'] + 1

        for i in range(len(self.non_terminals)):
            for NT in self.non_terminals:
                vals = self.non_terminals[NT]
                if vals['recursive']:
                    choices = self.rules[NT]
                    terms = 0
                    nonrecurs = 0
                    for choice in choices:
                        if not (all([sym[1] == self.T for sym in choice]) == False):
                            # This production choice is all terminals
                            terms += 1
                        temp = [bit for bit in choice if bit[1] == 'NT']
                        orary = 0
                        for bit in temp:
                            if not self.non_terminals[bit[0]]['recursive']:
                                orary += 1
                        if (orary == len(temp)) and temp:
                            # then all NTs in this production choice are not
                            # recursive
                            nonrecurs += 1
                    if terms == len(choices):
                        # this means all the production choices for this NT are
                        # terminals, it most definitely isn't recursive.
                        vals['recursive'] = False
                    elif (terms + nonrecurs) == len(choices):
                        # this means all the production choices for this NT are
                        # not recursive; it isn't recursive by proxy.
                        vals['recursive'] = False

        if self.start_rule[0] in self.non_terminals:
            self.min_path = self.non_terminals[self.start_rule[0]]['min_steps']
        else:
            print("Error: start rule not a non-terminal")
            quit()
        self.max_arity = 0
        for NT in self.non_terminals:
            if self.non_terminals[NT]['min_steps'] > self.max_arity:
                self.max_arity = self.non_terminals[NT]['min_steps']
        for rule in self.rules:
            for prod in self.rules[rule]:
                for sym in [i for i in prod if i[1] == self.NT]:
                    sym.append(self.non_terminals[sym[0]]['min_steps'])
        for rule in self.rules:
            for prod in self.rules[rule]:
                for sym in [i for i in prod if i[1] == self.NT]:
                    sym.append(self.non_terminals[sym[0]]['recursive'])

    def check_permutations(self, ramps=5):
        """ Calculates how many possible derivation tree combinations can be
            created from the given grammar at a specified depth. Only returns
            possible combinations at the specific given depth (if there are no
            possible permutations for a given depth, will return 0).
        """

        perms_list = []
        if self.max_arity > self.min_path:
            for i in max(range(self.max_arity+1 - self.min_path), range(ramps)):
                x = self.check_all_permutations(i + self.min_path)
                perms_list.append(x)
                if i > 0:
                    perms_list[i] -= sum(perms_list[:i])
                    self.permutations[i + self.min_path] -= sum(perms_list[:i])
        else:
            for i in range(ramps):
                x = self.check_all_permutations(i + self.min_path)
                perms_list.append(x)
                if i > 0:
                    perms_list[i] -= sum(perms_list[:i])
                    self.permutations[i + self.min_path] -= sum(perms_list[:i])

    def check_all_permutations(self, depth):
        """ Calculates how many possible derivation tree combinations can be
            created from the given grammar at a specified depth. Returns all
            possible combinations at the specific given depth including those
            depths below the given depth.
        """

        if depth < self.min_path:
            # There is a bug somewhere that is looking for a tree smaller than
            # any we can create
            print ("Error: cannot check permutations for tree smaller than the minimum size")
            quit()
        if depth in self.permutations.keys():
            return self.permutations[depth]
        else:
            pos = 0
            terminalSymbols = self.terminals
            depthPerSymbolTrees = {}
            productions = []
            for NT in self.non_terminals:
                a = self.non_terminals[NT]
                for rule in self.rules[a['id']]:
                    if any([prod[1] is self.NT for prod in rule]):
                        productions.append(rule)

            startSymbols = self.rules[self.start_rule[0]]

            for prod in productions:
                depthPerSymbolTrees[str(prod)] = {}

            for i in range(2, depth+1):
                # Find all the possible permutations from depth of min_path up
                # to a specified depth
                for ntSymbol in productions:
                    symPos = 1
                    for j in ntSymbol:
                        symbolArityPos = 0
                        if j[1] is self.NT:
                            for child in self.rules[j[0]]:
                                if len(child) == 1 and child[0][0] in self.terminals:
                                    symbolArityPos += 1
                                else:
                                    if (i - 1) in depthPerSymbolTrees[str(child)].keys():
                                        symbolArityPos += depthPerSymbolTrees[str(child)][i - 1]
                            symPos *= symbolArityPos
                    depthPerSymbolTrees[str(ntSymbol)][i] = symPos

            for sy in startSymbols:
                if str(sy) in depthPerSymbolTrees:
                    pos += depthPerSymbolTrees[str(sy)][depth] if depth in depthPerSymbolTrees[str(sy)] else 0
                else:
                    pos += 1
            self.permutations[depth] = pos
            return pos

    def __str__(self):
        return "%s %s %s %s" % (self.terminals, self.non_terminals,
                                self.rules, self.start_rule)

    def generate(self, _input, max_wraps=2):
        """Map input via rules to output. Returns output and used_input"""
        used_input = 0
        wraps = 0
        output = []
        production_choices = []

        unexpanded_symbols = [self.start_rule]
        while (wraps < max_wraps) and (len(unexpanded_symbols) > 0):
            # Wrap
            if used_input % len(_input) == 0 and \
                    used_input > 0 and \
                    len(production_choices) > 1:
                wraps += 1
            # Expand a production
            current_symbol = unexpanded_symbols.pop(0)
            # Set output if it is a terminal
            if current_symbol[1] != self.NT:
                output.append(current_symbol[0])
            else:
                production_choices = self.rules[current_symbol[0]]
                # Select a production
                current_production = _input[used_input % len(_input)] % len(production_choices)
                # Use an input if there was more then 1 choice
                if len(production_choices) > 1:
                    used_input += 1
                # Derviation order is left to right(depth-first)
                unexpanded_symbols = production_choices[current_production] + unexpanded_symbols

        #Not completly expanded
        if len(unexpanded_symbols) > 0:
            return None, used_input

        output = "".join(output)
        if self.python_mode:
            output = helper_methods.python_filter(output)
        return output, used_input

def get_min_ramp_depth(size, grammar):
    """ Find the minimum depth at which ramping can start where we can have
        unique solutions (no duplicates)."""

    depths = range(grammar.min_path, 11)

    if size % 2:
        # Population size is odd
        size += 1
    if size/2 < depths:
        depths = depths[:int(size/2)]

    unique_start = int(floor(size / len(depths)))
    ramp = None
    for i in sorted(grammar.permutations.keys()):
        if grammar.permutations[i] > unique_start:
            ramp = i
            break
    return ramp


bnf_grammar = Grammar("grammars/Keijzer6.bnf")

print (get_min_ramp_depth(100000, bnf_grammar))

genome = [71557, 78983, 6936, 94335, 11033, 25537, 38955, 98913, 15088, 37863, 63685, 18624, 31850, 95985, 2693, 83403, 22772, 5721, 68714, 89495, 86318, 12724, 417, 69911, 88845, 23565, 56800, 8611, 44617, 9866, 75489, 36, 56477, 83105, 40146, 91800, 23401, 57877, 19486, 19364, 66408, 88421, 89404, 92370, 10957, 32679, 65316, 90767, 7506, 47455, 74928, 91953, 96159, 8644, 22424, 88524, 93489, 93577, 86196, 1044, 45637, 18977, 3451, 99300, 95769, 33068, 40826, 93951, 79954, 14367, 77172, 98048, 11769, 45637, 78034]

#phenotype0, used_codons_0, orig_tree_0, array_0 = tree.genome_init(bnf_grammar, genome)

phenotype1, genome1, orig_tree_1, nodes_1, check_1 = tree.full_init(bnf_grammar, 10, SAVE)

phenotype2, genome2, orig_tree_2, nodes_2, check_2 = tree.random_init(bnf_grammar, 10, SAVE)

phenotype2_5, genome2_5, orig_tree_2_5, nodes_2_5, check2_5 = tree.pi_random_init(bnf_grammar, 10, SAVE)

phenotype3, genome3, orig_tree_3, nodes_3, check_3 = tree.grow_init(bnf_grammar, 10, SAVE)

phenotype4, genome4, orig_tree_4, nodes_4, check_4 = tree.pi_grow_init(bnf_grammar, 10, SAVE)

print ("\nPhenotype 1:\tFull init:\t", phenotype1)
print ("            \tIndex count\t\t", nodes_1)
print ("            \tNode count\t", orig_tree_1.get_nodes(0))
print ("            \tGenome length\t", len(genome1))

print ("\nPhenotype 2:\tRandom init:\t", phenotype2)
print ("            \tIndex count\t\t", nodes_2)
print ("            \tNode count\t", orig_tree_2.get_nodes(0))
print ("            \tGenome length\t", len(genome2))

#print ("\nPhenotype 2.5:\tPI random init:\t", phenotype2_5))
#print ("            \tNode Count\t\t", fitnesses_2_5[0])
#print ("            \tPhenotype length\t", fitnesses_2_5[1])
#print ("            \tRoot Bias\t\t", round(fitnesses_2_5[2], 2))
#print ("            \tSlope\t\t\t", fitnesses_2_5[3])
#print ("            \tMax Depth:\t", fitnesses_2_5[4])

#print ("\nPhenotype 3:\tGrow init:\t", phenotype3)
#print ("            \tNode Count\t\t", fitnesses_3[0])
#print ("            \tPhenotype length\t", fitnesses_3[1])
#print ("            \tRoot Bias\t\t", round(fitnesses_3[2], 2))
#print ("            \tSlope\t\t\t", fitnesses_3[3])
#print ("            \tMax Depth:\t", fitnesses_3[4])

#print ("\nPhenotype 4:\tPI Grow init:\t", phenotype4)
#print ("            \tNode Count\t\t", fitnesses_4[0])
#print ("            \tPhenotype length\t", fitnesses_4[1])
#print ("            \tRoot Bias\t\t", round(fitnesses_4[2], 2))
#print ("            \tSlope\t\t\t", fitnesses_4[3])
#print ("            \tMax Depth:\t", fitnesses_4[4])