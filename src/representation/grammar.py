from math import floor
from re import finditer, DOTALL, MULTILINE
from sys import maxsize

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
        
        # Initialise dicts for terminals and non terminals, set params.
        self.non_terminals, self.terminals = {}, []
        self.start_rule, self.codon_size = None, params['CODON_SIZE']
        self.min_path, self.max_arity = None, None
        
        # Set regular expressions for parsing BNF grammar.
        self.ruleregex = '(?P<rulename><\S+>)\s*::=\s*(?P<production>(?:(?=\#)\#[^\r\n]*|(?!<\S+>\s*::=).+?)+)'
        self.productionregex = '(?=\#)(?:\#.*$)|(?!\#)\s*(?P<production>(?:[^\'\"\|\#]+|\'.*?\'|".*?")+)'
        self.productionpartsregex = '\ *([\r\n]+)\ *|([^\'"<\r\n]+)|\'(.*?)\'|"(.*?)"|(?P<subrule><[^>|\s]+>)|([<]+)'
        
        # Read in BNF grammar, set production rules, terminals and
        # non-terminals.
        self.read_bnf_file(file_name)
        
        # Check the minimum depths of all non-terminals in the grammar.
        self.check_depths()
        
        # Check which non-terminals are recursive.
        self.check_recursion(self.start_rule[0], [])
        
        # Set the minimum path and maximum arity of the grammar.
        self.set_arity()
        
        # Calculate the total number of derivation tree permutations and
        # combinations that can be created by a grammar at a range of depths.
        self.check_permutations()
        
        # Set the minimum depth at which ramping can start where we can have
        # unique solutions (no duplicates).
        self.get_min_ramp_depth()
    
    def read_bnf_file(self, file_name):
        """
        Read a grammar file in BNF format. Parses the grammar and saves a
        dict of all production rules and their possible choices.

        :param file_name: A specified BNF grammar file.
        :return: Nothing.
        """
        
        with open(file_name, 'r') as bnf:
            # Read the whole grammar file.
            content = bnf.read()
            
            for rule in finditer(self.ruleregex, content, DOTALL):
                # Find all rules in the grammar
                
                if self.start_rule is None:
                    # Set the first rule found as the start rule.
                    self.start_rule = (rule.group('rulename'), self.NT)
                
                # Create and add a new rule.
                self.non_terminals[rule.group('rulename')] = {
                    'id': rule.group('rulename'),
                    'min_steps': maxsize,
                    'expanded': False,
                    'recursive': True,
                    'b_factor': 0}
                
                # Initialise empty list of all production choices for this
                # rule.
                tmp_productions = []
                
                for p in finditer(self.productionregex,
                                  rule.group('production'), MULTILINE):
                    # Split production choices of a rule.
                    
                    if p.group('production') is None or p.group(
                            'production').isspace():
                        # Skip to the next iteration of the loop if the
                        # current "p" production is None or blank space.
                        continue
                    
                    tmp_production, terminalparts = [], ''
                    
                    for sub_p in finditer(self.productionpartsregex,
                                          p.group('production').strip()):
                        # Split production into terminal and non terminal
                        # symbols.
                        
                        if sub_p.group('subrule'):
                            if terminalparts:
                                # Terminal symbol is to be appended to the
                                # terminals dictionary.
                                symbol = [terminalparts, self.T, 0, False]
                                tmp_production.append(symbol)
                                self.terminals.append(terminalparts)
                                terminalparts = ''
                            
                            tmp_production.append(
                                [sub_p.group('subrule'), self.NT])
                        
                        else:
                            # Unescape special characters (\n, \t etc.)
                            terminalparts += ''.join(
                                [part.encode().decode('unicode-escape') for
                                 part in sub_p.groups() if part])
                    
                    if terminalparts:
                        # Terminal symbol is to be appended to the terminals
                        # dictionary.
                        symbol = [terminalparts, self.T, 0, False]
                        tmp_production.append(symbol)
                        self.terminals.append(terminalparts)
                    tmp_productions.append(tmp_production)
                
                if not rule.group('rulename') in self.rules:
                    # Add new production rule to the rules dictionary if not
                    # already there.
                    self.rules[rule.group('rulename')] = tmp_productions
                    
                    if len(tmp_productions) == 1:
                        # Unit productions.
                        print("Warning: Grammar contains unit production "
                              "for production rule", rule.group('rulename'))
                        print("       Unit productions consume GE codons.")
                else:
                    # Conflicting rules with the same name.
                    raise ValueError("lhs should be unique",
                                     rule.group('rulename'))
    
    def check_depths(self):
        """
        Run through a grammar and find out the minimum distance from each
        NT to the nearest T. Useful for initialisation methods where we
        need to know how far away we are from fully expanding a tree
        relative to where we are in the tree and what the depth limit is.
            
        :return: Nothing.
        """
        
        # Initialise graph and counter for checking minimum steps to Ts for
        # each NT.
        counter, graph = 1, []
        
        for rule in sorted(self.rules.keys()):
            # Iterate over all NTs.
            choices = self.rules[rule]
            
            # Set branching factor for each NT.
            self.non_terminals[rule]['b_factor'] = len(choices)
            
            for choice in choices:
                # Add a new edge to our graph list.
                graph.append([rule, choice])
        
        while graph:
            removeset = set()
            for edge in graph:
                # Find edges which either connect to terminals or nodes
                # which are fully expanded.
                if all([sy[1] == self.T or self.non_terminals[sy[0]][
                    'expanded'] for sy in edge[1]]):
                    removeset.add(edge[0])
            
            for s in removeset:
                # These NTs are now expanded and have their correct minimum
                # path set.
                self.non_terminals[s]['expanded'] = True
                self.non_terminals[s]['min_steps'] = counter
            
            # Create new graph list and increment counter.
            graph = [e for e in graph if e[0] not in removeset]
            counter += 1
    
    def check_recursion(self, cur_symbol, seen):
        """
        Traverses the grammar recursively and sets the properties of each rule.

        :param cur_symbol: symbol to check.
        :param seen: Contains already checked symbols in the current traversal.
        :return: Boolean stating whether or not cur_symbol is recursive.
        """
        
        if cur_symbol not in self.non_terminals.keys():
            # Current symbol is a T.
            return False
        
        if cur_symbol in seen:
            # Current symbol has already been seen, is recursive.
            return True

        # Append current symbol to seen list.
        seen.append(cur_symbol)
        
        # Get choices of current symbol.
        choices, nt = self.rules[cur_symbol], self.non_terminals[cur_symbol]
        
        recursive = False
        for choice in choices:
            for symbol in choice:
                # Recurse over choices.
                recursive_symbol = self.check_recursion(symbol[0], seen)
                recursive = recursive or recursive_symbol
        
        # Set recursive properties.
        nt['recursive'] = recursive
        seen.remove(cur_symbol)
        
        return nt['recursive']
    
    def set_arity(self):
        """
        Set the minimum path of the grammar, i.e. the smallest legal
        solution that can be generated.

        Set the maximum arity of the grammar, i.e. the longest path to a
        terminal from any non-terminal.

        :return: Nothing
        """
        
        # Set the minimum path of the grammar as the minimum steps to a
        # terminal from the start rule.
        self.min_path = self.non_terminals[self.start_rule[0]]['min_steps']
        
        # Initialise the maximum arity of the grammar to 0.
        self.max_arity = 0
        
        for NT in self.non_terminals:
            if self.non_terminals[NT]['min_steps'] > self.max_arity:
                # Set the maximum arity of the grammar as the longest path
                # to a T from any NT.
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
                                    if (i - 1) in depth_per_symbol_trees[
                                        str(child)].keys():
                                        symbol_arity_pos += \
                                        depth_per_symbol_trees[str(child)][
                                            i - 1]
                            sym_pos *= symbol_arity_pos
                    depth_per_symbol_trees[str(ntSymbol)][i] = sym_pos
            
            for sy in start_symbols:
                if str(sy) in depth_per_symbol_trees:
                    pos += depth_per_symbol_trees[str(sy)][depth] if depth in \
                                                                     depth_per_symbol_trees[
                                                                         str(
                                                                             sy)] else 0
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
