from re import finditer, DOTALL, MULTILINE
from algorithm.parameters import params
from operators import initialisation
from itertools import groupby


class Grammar(object):
    """ Context Free Grammar """
    NT = "NT"  # Non Terminal
    T = "T"  # Terminal
    
    def __init__(self, file_name):
        if file_name.endswith("pybnf"):
            self.python_mode = True
        else:
            self.python_mode = False
        self.rules = {}
        self.permutations = {}
        self.non_terminals, self.terminals = {}, []
        self.start_rule = None
        self.codon_size = params['CODON_SIZE']
        self.ruleregex = '(?P<rulename><\S+>)\s*::=\s*(?P<production>(?:(?=\#)\#[^\r\n]*|(?!<\S+>\s*::=).+?)+)'
        self.productionregex = '(?=\#)(?:\#.*$)|(?!\#)\s*(?P<production>(?:[^\'\"\|\#]+|\'.*?\'|".*?")+)'
        self.productionpartsregex = '\ *([\r\n]+)\ *|([^\'"<\r\n]+)|\'(.*?)\'|"(.*?)"|(?P<subrule><[^>|\s]+>)|([<]+)'
        self.read_bnf_file(file_name)
        self.check_depths()
        self.check_permutations()
        self.min_ramp = initialisation.get_min_ramp_depth(self)
        self.crossover_NTs = [i for i in self.non_terminals
                              if self.non_terminals[i]['b_factor'] > 1]

    def read_bnf_file(self, file_name):
        """Read a grammar file in BNF format"""

        # Read the grammar file
        with open(file_name, 'r') as bnf:
            content = bnf.read()
            for rule in finditer(self.ruleregex, content, DOTALL):
                if self.start_rule is None:
                    self.start_rule = (rule.group('rulename'), self.NT)
                self.non_terminals[rule.group('rulename')] = {
                    'id': rule.group('rulename'),
                    'min_steps': 9999999999999,
                    'expanded': False,
                    'recursive': True,
                    'permutations': None,
                    'b_factor': 0}
                tmp_productions = []
                for p in finditer(self.productionregex,
                                  rule.group('production'), MULTILINE):
                    if p.group('production') is None or p.group(
                            'production').isspace():
                        continue
                    tmp_production = []
                    terminalparts = ''
                    for sub_p in finditer(self.productionpartsregex,
                                          p.group('production').strip()):
                        if sub_p.group('subrule'):
                            if terminalparts:
                                symbol = [terminalparts, self.T, 0, False]
                                tmp_production.append(symbol)
                                self.terminals.append(terminalparts)
                                terminalparts = ''
                            tmp_production.append(
                                [sub_p.group('subrule'), self.NT])
                        else:
                            terminalparts += ''.join(
                                [part.encode().decode('unicode-escape') for
                                 part in sub_p.groups() if part])
                
                    if terminalparts:
                        symbol = [terminalparts, self.T, 0, False]
                        tmp_production.append(symbol)
                        self.terminals.append(terminalparts)
                    tmp_productions.append(tmp_production)
            
                if not rule.group('rulename') in self.rules:
                    self.rules[rule.group('rulename')] = tmp_productions
                    if len(tmp_productions) == 1:
                        print("Warning: Grammar contains unit production "
                              "for production rule", rule.group('rulename'))
                        print("       Unit productions consume GE codons.")
                else:
                    raise ValueError("lhs should be unique",
                                     rule.group('rulename'))

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
                        if all([sym[1] == self.T for sym in choice]):
                            terms += 1
                    if terms:
                        # this NT can then map directly to a T
                        vals['min_steps'] = 1
                        vals['expanded'] = True
                    else:
                        # There are NTs remaining in the production choices
                        for choice in choices:
                            NT_s = [sym for sym in choice if sym[1] == self.NT]
                            NT_choices = list(NT_s for NT_s,
                                                       _ in groupby(NT_s))
                            if len(NT_choices) > 1:
                                if all([self.non_terminals[item[0]]['expanded']
                                        for item in NT_choices]):
                                    if vals['expanded'] and \
                                            (vals['min_steps'] >
                                                     max([self.non_terminals
                                                          [item[0]]
                                                          ['min_steps']
                                                          for item in
                                                          NT_choices]) + 1):
                                        vals['min_steps'] = \
                                            max([self.non_terminals[item[0]]
                                                 ['min_steps'] for
                                                 item in NT_choices]) + 1
                                    elif not vals['expanded']:
                                        vals['expanded'] = True
                                        vals['min_steps'] = \
                                            max([self.non_terminals[item[0]]
                                                 ['min_steps']
                                                 for item in NT_choices]) + 1
                            else:
                                child = self.non_terminals[NT_choices[0][0]]
                                if child['expanded']:
                                    if vals['expanded'] and\
                                            (vals['min_steps'] >
                                                     child['min_steps'] + 1):
                                        vals['min_steps'] = \
                                            child['min_steps'] + 1
                                    else:
                                        vals['expanded'] = True
                                        vals['min_steps'] = \
                                            child['min_steps'] + 1

        for i in range(len(self.non_terminals)):
            for NT in self.non_terminals:
                vals = self.non_terminals[NT]
                if vals['recursive']:
                    choices = self.rules[NT]
                    terms = 0
                    nonrecurs = 0
                    for choice in choices:
                        if all([sym[1] == self.T for sym in choice]):
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
            for i in range(max((self.max_arity+1 - self.min_path), ramps)):
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
            print("Error: cannot check permutations for tree smaller than the "
                  "minimum size")
            quit()
        if depth in self.permutations.keys():
            return self.permutations[depth]
        else:
            pos = 0
            depth_per_symbol_trees = {}
            productions = []
            for NT in self.non_terminals:
                a = self.non_terminals[NT]
                for rule in self.rules[a['id']]:
                    if any([prod[1] is self.NT for prod in rule]):
                        productions.append(rule)

            start_symbols = self.rules[self.start_rule[0]]

            for prod in productions:
                depth_per_symbol_trees[str(prod)] = {}

            for i in range(2, depth+1):
                # Find all the possible permutations from depth of min_path up
                # to a specified depth
                for ntSymbol in productions:
                    sym_pos = 1
                    for j in ntSymbol:
                        symbol_arity_pos = 0
                        if j[1] is self.NT:
                            for child in self.rules[j[0]]:
                                if len(child) == 1 and child[0][0] in \
                                        self.terminals:
                                    symbol_arity_pos += 1
                                else:
                                    if (i - 1) in depth_per_symbol_trees[str(child)].keys():
                                        symbol_arity_pos += depth_per_symbol_trees[str(child)][i - 1]
                            sym_pos *= symbol_arity_pos
                    depth_per_symbol_trees[str(ntSymbol)][i] = sym_pos

            for sy in start_symbols:
                if str(sy) in depth_per_symbol_trees:
                    pos += depth_per_symbol_trees[str(sy)][depth] if depth in depth_per_symbol_trees[str(sy)] else 0
                else:
                    pos += 1
            self.permutations[depth] = pos
            return pos

    def __str__(self):
        return "%s %s %s %s" % (self.terminals, self.non_terminals,
                                self.rules, self.start_rule)
