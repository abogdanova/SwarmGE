from sys import maxsize
from math import floor
from re import finditer, DOTALL, MULTILINE

from algorithm.parameters import params


class Grammar(object):
    """
    Parser for Backus-Naur Form (BNF) Context-Free Grammars.
    """
    
    NT = "NT"  # Non Terminal
    T = "T"  # Terminal

    def __init__(self, file_name):
        """
        Initialises an instance of the grammar class. This instance is used
        to parse a given file_name grammar.
        
        :param file_name: A specified BNF grammar file.
        """
        
        if file_name.endswith("pybnf"):
            # Use python filter for parsing grammar output as grammar output
            # contains indented python code.
            self.python_mode = True
        
        else:
            # No need to filter/interpret grammar output, individual
            # phenotypes can be evaluated as normal.
            self.python_mode = False
        
        # Initialise empty dict for all production rules in the grammar.
        # Initialise empty dict of permutations of solutions possible at
        # each derivation tree depth.
        self.rules, self.permutations = {}, {}
        
        # Initialise dicts for terminals and non terminals.
        self.non_terminals, self.terminals = {}, []
        self.start_rule = None
        self.codon_size = params['CODON_SIZE']
        
        # Set regular expressions for parsing BNF grammar.
        self.ruleregex = '(?P<rulename><\S+>)\s*::=\s*(?P<production>(?:(?=\#)\#[^\r\n]*|(?!<\S+>\s*::=).+?)+)'
        self.productionregex = '(?=\#)(?:\#.*$)|(?!\#)\s*(?P<production>(?:[^\'\"\|\#]+|\'.*?\'|".*?")+)'
        self.productionpartsregex = '\ *([\r\n]+)\ *|([^\'"<\r\n]+)|\'(.*?)\'|"(.*?)"|(?P<subrule><[^>|\s]+>)|([<]+)'
        
        # Read in BNF grammar, set production rules, terminals and
        # non-terminals.
        self.read_bnf_file(file_name)
        
        # Check
        self.check_depths()
        self.check_permutations()
        self.get_min_ramp_depth()
        
        # Find non-terminals that can be used for subtree crossover.
        # Crossover is not permitted on unit productions.
        # TODO: Check with James if we should allow crossover on unit
        # productions.
        self.crossover_NTs = [i for i in self.non_terminals
                              if self.non_terminals[i]['b_factor'] > 1]

    def read_bnf_file(self, file_name):
        """
        Read a grammar file in BNF format. Parses the grammar and saves a
        dict of all production rules and their possible choices.
        
        :param file_name: A specified BNF grammar file.
        :return: Nothing.
        """

        # Read the whole grammar file
        with open(file_name, 'r') as bnf:
            content = bnf.read()
            # Find all rules in the grammar
            for rule in finditer(self.ruleregex, content, DOTALL):
                # Set the first rule found as start rule
                if self.start_rule is None:
                    self.start_rule = (rule.group('rulename'), self.NT)
                # create and add new rule
                self.non_terminals[rule.group('rulename')] = {
                    'id': rule.group('rulename'),
                    'min_steps': maxsize,
                    'expanded': False,
                    'recursive': True,
                    'permutations': None,
                    'b_factor': 0}
                tmp_productions = []
                # Split production choices of a rule
                for p in finditer(self.productionregex, rule.group('production'), MULTILINE):
                    if p.group('production') is None or p.group('production').isspace():
                        continue
                    tmp_production = []
                    terminalparts = ''
                    # Split production into terminal and non terminal symbols
                    for sub_p in finditer(self.productionpartsregex, p.group('production').strip()):
                        if sub_p.group('subrule'):
                            if terminalparts:
                                symbol = [terminalparts, self.T, 0, False]
                                tmp_production.append(symbol)
                                self.terminals.append(terminalparts)
                                terminalparts = ''
                            tmp_production.append(
                                [sub_p.group('subrule'), self.NT])
                        else:
                            # Unescape special characters (\n, \t etc.)
                            terminalparts += ''.join(
                                [part.encode().decode('unicode-escape') for part in sub_p.groups() if part])

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
                    raise ValueError("lhs should be unique", rule.group('rulename'))

    def check_depths(self):
        """
        Check the properties of all rules and set the properties accordingly.
        """

        self.calc_nt_properties(self.start_rule[0], [])

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

    def calc_nt_properties(self, cur_symbol, seen):
        """
        Traverses the grammar recursively and sets the properties of each rule

        :param cur_symbol: symbol to check
        :param seen: Contains already checked symbols in the current traversal
        :return: tuple containing depth of the cur_symbol and if cur_symbol is recursive
        """
        if cur_symbol not in self.non_terminals.keys():
            return 0, False

        if cur_symbol in seen:
            return maxsize, True

        nt = self.non_terminals[cur_symbol]
        if nt['expanded']:
            return nt['min_steps'], nt['recursive']

        seen.append(cur_symbol)
        choices = self.rules[cur_symbol]
        recursive = False
        min_cur_symbol_depth = maxsize
        for choice in choices:
            max_choice_depth = 0
            for symbol in choice:
                symbol_depth, recursive_symbol = self.calc_nt_properties(symbol[0], seen)
                max_choice_depth = symbol_depth if symbol_depth > max_choice_depth else max_choice_depth
                recursive = recursive or recursive_symbol

            min_cur_symbol_depth = max_choice_depth if max_choice_depth < min_cur_symbol_depth else min_cur_symbol_depth

        if min_cur_symbol_depth >= maxsize:
            raise Exception('No depth could be calculated for symbol', cur_symbol)

        nt['b_factor'] = len(self.rules[cur_symbol])
        nt['expanded'] = True
        nt['min_steps'] = min_cur_symbol_depth + 1
        nt['recursive'] = recursive
        seen.remove(cur_symbol)
        return nt['min_steps'], nt['recursive']

    def check_permutations(self, ramps=5):
        """ Calculates how many possible derivation tree combinations can be
            created from the given grammar at a specified depth. Only returns
            possible combinations at the specific given depth (if there are no
            possible permutations for a given depth, will return 0).
        """

        perms_list = []
        if self.max_arity > self.min_path:
            for i in range(max((self.max_arity + 1 - self.min_path), ramps)):
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

            for i in range(2, depth + 1):
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

    def get_min_ramp_depth(self):
        """
        Find the minimum depth at which ramping can start where we can have
        unique solutions (no duplicates).

        :param self: An instance of the representation.grammar.grammar class.
        :return: The minimum depth at which unuique solutions can be generated
        """
    
        max_tree_deth = params['MAX_TREE_DEPTH']
        size = params['POPULATION_SIZE']
    
        # Specify the range of ramping depths
        depths = range(self.min_path, max_tree_deth + 1)
    
        if size % 2:
            # Population size is odd
            size += 1
    
        if size / 2 < len(depths):
            # The population size is too small to fully cover all ramping
            # depths. Only ramp to the number of depths we can reach.
            depths = depths[:int(size / 2)]
    
        # Find the minimum number of unique solutions required to generate
        # sufficient individuals at each depth.
        unique_start = int(floor(size / len(depths)))
        ramp = None
    
        for i in sorted(self.permutations.keys()):
            # Examine the number of permutations and combinations of unique
            # solutions capable of being generated by a grammar across each
            # depth i.
            if self.permutations[i] > unique_start:
                # If the number of permutations possible at a given depth i is
                # greater than the required number of unique solutions,
                # set the minimum ramp depth and break out of the loop.
                ramp = i
                break
        self.min_ramp = ramp

    def __str__(self):
        return "%s %s %s %s" % (self.terminals, self.non_terminals,
                                self.rules, self.start_rule)



