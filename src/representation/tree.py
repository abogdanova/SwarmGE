#! /usr/bin/env python

# Tree class
# Copyright (c) 2015 James McDermott and Michael Fenton
# Hereby licensed under the GNU GPL v3.

from algorithm.parameters import params
from copy import deepcopy
import random


class Tree:

    def __init__(self, expr, parent, max_depth=20, depth_limit=20):
        self.parent = parent
        self.max_depth = max_depth
        self.codon = None
        self.depth_limit = depth_limit
        self.id = None
        self.depth = 1
        if len(expr) == 1:
            self.root = expr[0]
            self.children = []
        else:
            self.root = expr[0]
            self.children = []
            for child in expr[1:]:
                if type(child) == tuple:
                    self.children.append(Tree(child, self))
                else:
                    self.children.append(Tree((child,), self))

    def __str__(self):
        result = "("
        result += str(self.root)
        for child in self.children:
            if len(child.children) > 0:
                result += " " + str(child)
            else:
                result += " " + str(child.root)
        result += ")"
        return result

    def get_depth(self):
        """Get the depth of the current node."""

        count = 1
        currentParent = self.parent
        while currentParent is not None:
            count += 1
            currentParent = currentParent.parent
        return count

    def get_max_children(self, current, max_D=0):
        #TODO Remove obsolete function

        curr_depth = current.get_depth()
        if curr_depth > max_D:
            max_D = curr_depth
        for child in current.children:
            max_D = child.get_max_children(child, max_D)
        return max_D

    def get_tree_info(self, current, number=0, max_D=0):
        """ Get the number of nodes and the max depth of the tree.
        """

        number += 1
        if self.root in params['BNF_GRAMMAR'].non_terminals:
            current.id = number
            if current.parent:
                current.depth = current.parent.depth + 1
            if current.depth > max_D:
                max_D = current.depth
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            if not NT_kids:
                number += 1
            else:
                for child in NT_kids:
                    max_D, number = child.get_tree_info(child, number, max_D)

        return max_D, number

    def get_target_nodes(self, array, target=None):
        """ Returns the ids of all NT nodes which match the target NT list in a
            given tree.
        """

        if self.root in params['BNF_GRAMMAR'].non_terminals:
            if self.root in target:
                array.append(self.id)
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            if NT_kids:
                for child in NT_kids:
                    array = child.get_target_nodes(array, target=target)
        return array

    def return_node_from_id(self, node_id, return_tree=None):
        """ Returns a specific node given a node id. Can only return NT nodes.
        """

        if self.id == node_id:
            return_tree = self
        elif self.root in params['BNF_GRAMMAR'].non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if NT_kids:
                for child in NT_kids:
                    return_tree = child.return_node_from_id(node_id, return_tree=return_tree)
        return return_tree

    def get_output(self):
        output = []
        for child in self.children:
            if not child.children:
                output.append(child.root)
            else:
                output += child.get_output()
        return "".join(output)

    def check_genome(self):
        """ Goes through a tree and checks each codon to ensure production
            choice is correct """

        if self.codon:
            productions = params['BNF_GRAMMAR'].rules[self.root]
            selection = self.codon % len(productions)
            chosen_prod = productions[selection]
            prods = [prod[0] for prod in chosen_prod]
            roots = []
            for kid in self.children:
                roots.append(kid.root)
            if roots != prods:
                print("\nGenome is incorrect")
                print("Codon productions:\t", prods)
                print("Actual children:  \t", roots)
                quit()
        for kid in self.children:
            kid.check_genome()

    def check_tree(self):
        """ Checks the entire tree for discrepancies """

        self.check_genome()
        invalid = self.check_expansion()
        if invalid:
            print("Invalid given tree")
            quit()

        def check_nodes(tree, n=0):
            n += 1
            if tree.id != n:
                print("Node ids do not match node numbers")
                quit()

            if tree.root in params['BNF_GRAMMAR'].non_terminals:
                NT_kids = [kid for kid in tree.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
                if not NT_kids:
                    n += 1
                else:
                    for child in NT_kids:
                        n = check_nodes(child, n)
            return n

        check_nodes(self)

        orig_out = deepcopy(self.get_output())
        orig_gen = deepcopy(self.build_genome([]))

        output, genome, tree, nodes, invalid, depth, \
        used_codons = genome_init(orig_gen)

        if invalid:
            print("Invalid genome tree")
            print("Original:\t", orig_out)
            print("Genome:  \t", output)
            quit()

        if orig_out != output:
            print("Tree output doesn't match genome tree output")
            print("Original:\t", orig_out)
            print("Genome:  \t", output)
            quit()

        elif orig_gen != genome:
            print("Tree genome doesn't match genome tree genome")
            print("Original:\t", orig_gen)
            print("Genome:  \t", genome)
            quit()

    def build_genome(self, genome):
        """ Goes through a tree and builds a genome from all codons in the subtree.
        """

        if self.codon:
            genome.append(self.codon)
        for kid in self.children:
            genome = kid.build_genome(genome)
        return genome

    def genome_derivation(self, genome, index, depth, max_depth, nodes):
        """ Builds a tree using production choices from a given genome. Not
            guaranteed to terminate.
        """

        if index != "Incomplete" and index < len(genome):
            nodes += 1
            depth += 1

            self.id, self.depth = nodes, depth

            productions = params['BNF_GRAMMAR'].rules[self.root]
            selection = genome[index % len(genome)] % len(productions)
            chosen_prod = productions[selection]
            if len(productions) > 1:
                # Codon consumed
                self.codon = genome[index % len(genome)]
                index += 1
            self.children = []

            # print("\nCurrent root:   \t", self.root)
            # print("  Choices:      \t", productions)
            # print("  Chosen Product:\t", chosen_prod)
            # print("  Current node: \t", nodes)
            # print("  Current depth:\t", depth)
            # print("  Current max d:\t", max_depth)

            for i in range(len(chosen_prod)):
                symbol = chosen_prod[i]
                if symbol[1] == params['BNF_GRAMMAR'].T:
                    self.children.append(Tree((symbol[0],), self))

                elif symbol[1] == params['BNF_GRAMMAR'].NT:
                    self.children.append(Tree((symbol[0],), self))
                    index, nodes, d, max_depth = self.children[-1].genome_derivation(genome,
                                     index, depth, max_depth, nodes)

        elif len(params['BNF_GRAMMAR'].rules[self.root]) == 1:
            #Unit production at end of genome

            nodes += 1
            depth += 1

            self.id, self.depth = nodes, depth

            productions = params['BNF_GRAMMAR'].rules[self.root]
            chosen_prod = productions[0]
            self.children = []

            for i in range(len(chosen_prod)):
                symbol = chosen_prod[i]
                if symbol[1] == params['BNF_GRAMMAR'].T:
                    self.children.append(Tree((symbol[0],), self))
                elif symbol[1] == params['BNF_GRAMMAR'].NT:
                    self.children.append(Tree((symbol[0],), self))
                    index, nodes, d, max_depth = self.children[-1].genome_derivation(genome,
                                     index, depth, max_depth, nodes)
        else:
            # Mapping incomplete
            return "Incomplete", "Incomplete", "Incomplete", "Incomplete"

        NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
        if not NT_kids:
            # Then the branch terminates here
            depth += 1
            nodes += 1

            # print "\nCurrent root:   \t", chosen_prod
            # print "  Current node: \t", nodes
            # print "  Current depth:\t", depth
            # print "  Current max d:\t", max_depth

        if max_depth != "Incomplete" and (depth > max_depth):
            max_depth = depth
        return index, nodes, depth, max_depth

    def legal_productions(self, method, remaining_depth, productions):
        """ Returns the available production choices for a node given a depth
            limit """

        available = []

        if method == "random":
            if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                available = productions
            elif remaining_depth <= 0:
                min_path = min([max([item[2] for item in prod]) for prod in productions])
                shortest = [prod for prod in productions if max([item[2] for item in prod]) == min_path]
                available = shortest
            else:
                for prod in productions:
                    prod_depth = max([item[2] for item in prod])
                    if prod_depth < remaining_depth:
                        available.append(prod)
                if not available:
                    min_path = min([max([item[2] for item in prod]) for prod in productions])
                    shortest = [prod for prod in productions if max([item[2] for item in prod]) == min_path]
                    available = shortest

        elif method == "full":
            if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                for production in productions:
                    if any(sym[3] for sym in production):
                        available.append(production)
                if not available:
                    for production in productions:
                        if all(sym[3] for sym in production) == False:
                            available.append(production)
            else:
                for prod in productions:
                    prod_depth = max([item[2] for item in prod])
                    if prod_depth == remaining_depth - 1:
                        available.append(prod)
                if not available:
                    # Then we don't have what we're looking for
                    for prod in productions:
                        prod_depth = 0
                        for item in prod:
                            if (item[1] == params['BNF_GRAMMAR'].NT) and (item[2] > prod_depth):
                                prod_depth = item[2]
                        if prod_depth < remaining_depth:
                            available.append(prod)
        return available

    def derivation(self, genome, method, nodes, depth, max_depth, depth_limit=20):
        """ Derive a tree using a given method """

        nodes += 1
        depth += 1
        self.id, self.depth = nodes, depth

        productions = params['BNF_GRAMMAR'].rules[self.root]
        remaining_depth = depth_limit

        available = self.legal_productions(method, remaining_depth, productions)
        chosen_prod = random.choice(available)

        choice = productions.index(chosen_prod)
        codon = random.randrange(len(productions), params['BNF_GRAMMAR'].codon_size, len(productions)) + choice
        self.codon = codon
        genome.append(codon)

        # print("\nCurrent root:   \t", self.root)
        # print("  Choices:      \t", productions)
        # print("  Chosen Product:\t", chosen_prod)
        # print("  Current node: \t", nodes)
        # print("  Current depth:\t", depth)
        # print("  Current max d:\t", max_depth)
        # print("  Remaining depth:\t", remaining_depth)

        self.children = []
        for symbol in chosen_prod:
            if symbol[1] == params['BNF_GRAMMAR'].T:
                #if the right hand side is a terminal
                self.children.append(Tree((symbol[0],),self))
            elif symbol[1] == params['BNF_GRAMMAR'].NT:
                # if the right hand side is a non-terminal
                self.children.append(Tree((symbol[0],),self))
                genome, nodes, d, max_depth = self.children[-1].derivation(genome, method, nodes, depth, max_depth, depth_limit=depth_limit-1)

        NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]

        if not NT_kids:
            # Then the branch terminates here
            depth += 1
            nodes += 1

            # print("\nCurrent root:   \t", chosen_prod)
            # print("  Current node: \t", nodes)
            # print("  Current depth:\t", depth)

        if depth > max_depth:
            max_depth = depth

        # if not NT_kids:
        #     print "  Current max d:\t", max_depth
        #     print "  Remaining depth:\t", remaining_depth - 1
        return genome, nodes, depth, max_depth

    def pi_random_derivation(self, index, max_depth=20):
        """ Randomly builds a tree from a given root node up to a maximum
            given depth. Uses position independent stuff.
        """

        queue = [[self, params['BNF_GRAMMAR'].non_terminals[self.root]['recursive']]]

        while queue:
            num = len(queue)
            chosen = random.randint(0, num-1)
            all_node = queue.pop(chosen)
            node = all_node[0]

            if node.get_depth() < max_depth:
                productions = params['BNF_GRAMMAR'].rules[node.root]
                available = []
                remaining_depth = max_depth - node.get_depth()

                if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                    available = productions
                else:
                    for prod in productions:
                        depth = 0
                        for item in prod:
                            if (item[1] == params['BNF_GRAMMAR'].NT) and (item[2] > depth):
                                depth = item[2]
                        if depth < remaining_depth:
                            available.append(prod)
                chosen_prod = random.choice(available)
                if len(productions) > 1:
                    prod_choice = productions.index(chosen_prod)
                    codon = random.randrange(0, params['BNF_GRAMMAR'].codon_size, len(productions)) + prod_choice
                    node.codon = codon
                    node.id = index
                    index += 1
                node.children = []

                for i in range(len(chosen_prod)):
                    symbol = chosen_prod[i]
                    child = Tree((symbol[0],),node)
                    node.children.append(child)
                    if symbol[1] == params['BNF_GRAMMAR'].NT:
                        # if the right hand side is a non-terminal
                        queue.insert(chosen+i, [child, params['BNF_GRAMMAR'].non_terminals[child.root]['recursive']])
        genome = self.build_genome([])
        return genome

    def pi_grow(self, index, max_depth=20):
        """ Grows a tree until a single branch reaches a specified depth. Does
            this by only using recursive production choices until a single
            branch of the tree has reached the specified maximum depth. After
            that any choices are allowed
        """

        queue = [[self, params['BNF_GRAMMAR'].non_terminals[self.root]['recursive']]]

        while queue:
            num = len(queue)
            chosen = random.randint(0, num-1)
            all_node = queue.pop(chosen)
            node = all_node[0]

            if node.get_depth() < max_depth:
                productions = params['BNF_GRAMMAR'].rules[node.root]
                available = []
                remaining_depth = max_depth - node.get_depth()

                if (self.get_max_children(self) < max_depth - 1) or \
                        (node.parent is None) or \
                        (all_node[1] and (not any([item[1] for item in queue]))):
                    # We want to prevent the tree from creating terminals
                    # until a single branch has reached the full depth

                    if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                        for production in productions:
                            if any(sym[3] for sym in production):
                                available.append(production)
                        if not available:
                            for production in productions:
                                if all(sym[3] for sym in production) == False:
                                    available.append(production)
                    else:
                        for prod in productions:
                            depth = 0
                            for item in prod:
                                if (item[1] == params['BNF_GRAMMAR'].NT) and (item[2] > depth):
                                    depth = item[2]
                            if depth < remaining_depth:
                                available.append(prod)
                else:
                    if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                        available = productions
                    else:
                        for prod in productions:
                            depth = 0
                            for item in prod:
                                if (item[1] == params['BNF_GRAMMAR'].NT) and (item[2] > depth):
                                    depth = item[2]
                            if depth < remaining_depth:
                                available.append(prod)
                chosen_prod = random.choice(available)
                if len(productions) > 1:
                    prod_choice = productions.index(chosen_prod)
                    codon = random.randrange(0, params['BNF_GRAMMAR'].codon_size, len(productions)) + prod_choice
                    node.codon = codon
                    node.id = index
                    index += 1
                node.children = []

                for i in range(len(chosen_prod)):
                    symbol = chosen_prod[i]
                    child = Tree((symbol[0],),node)
                    node.children.append(child)
                    if symbol[1] == params['BNF_GRAMMAR'].NT:
                        # if the right hand side is a non-terminal
                        queue.insert(chosen+i, [child, params['BNF_GRAMMAR'].non_terminals[child.root]['recursive']])
        genome = self.build_genome([])
        return genome

    def check_expansion(self):
        """ Check if a given tree is completely expanded or not. Return boolean
            True if the tree IS NOT completely expanded.
        """

        check = False
        if self.root in params['BNF_GRAMMAR'].non_terminals.keys():
            # Current node is a NT and should have children
            if self.children:
                # Everything is as expected
                for child in self.children:
                    check = child.check_expansion()
                    if check:
                        break
            else:
                # Current node is not completely expanded
                check = True
        return check

    def getLabels(self, labels):
        labels.add(self.root)

        for c in self.children:
            labels = c.getLabels(labels)
        return labels

    def print_tree(self):
        print(self)
