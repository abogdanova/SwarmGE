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
        while currentParent != None:
            count += 1
            currentParent = currentParent.parent
        return count

    def get_max_children(self, current, max_D=0):
        """ The distance from the current node to the furthest branched NT in
            the given tree (returns the maximum depth of the tree).
        """

        curr_depth = current.get_depth()
        if curr_depth > max_D:
            max_D = curr_depth
        for child in current.children:
            max_D = child.get_max_children(child, max_D)
        return max_D

    def get_target_nodes(self, array, number=0, target=None):
        """ Returns the indexes of all nodes which match the target NT in a
            given tree.
        """

        number += 1
        if self.root in params['BNF_GRAMMAR'].non_terminals:
            if self.root == target:
                array.append(number)
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if not NT_kids:
                # The child is a Terminal
                number += 1
            else:
                for child in NT_kids:
                    array, number = child.get_target_nodes(array, number=number, target=target)
        return array, number

    def get_nodes(self, number=0):
        """ Returns the total number of nodes in a given tree.
        """

        number += 1
        if self.root in params['BNF_GRAMMAR'].non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if not NT_kids:
                # The child is a Terminal
                number += 1
            else:
                for child in NT_kids:
                    number = child.get_nodes(number)
        return number

    def get_decision_nodes(self, number=0):
        """ Returns the total number of nodes which create
            production choices in a given tree.
        """

        if self.root in params['BNF_GRAMMAR'].non_terminals:
            if self.codon:
                number += 1
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if NT_kids:
                for child in NT_kids:
                    number = child.get_decision_nodes(number)
        return number

    def get_node_ids(self, n_list, number=0):
        """ Assigns every node in the tree a unique id. Returns a list
            including:
                node id
                node root
                node children
                node depth
                max node child depth
        """

        number += 1
        kids = []
        for child in self.children:
            if child.children == []:
                kids.append(child.root)
        depth = self.get_depth()
        n_list.append([number, self.root, self, kids, depth, self.get_max_children(self, 0)-depth])
        self.id = number
        if self.root in params['BNF_GRAMMAR'].non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if not NT_kids:
                # The child is a Terminal
                number += 1
                kids = []
                for child in self.children:
                    child.id = number
                    if child.children == []:
                        kids.append(child.root)
                depth = self.get_depth()
                n_list.append([number, self.root, self, kids, depth, self.get_max_children(self, 0)-depth])
            else:
                for child in NT_kids:
                    number, n_list = child.get_node_ids(n_list, number=number)
        return number, n_list

    def return_node_from_id(self, node_id, number=0, return_tree=None):
        """ Returns the total number of nodes in a given tree.
        """

        number += 1
        if number == node_id:
            return_tree = self
        elif self.root in params['BNF_GRAMMAR'].non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if not NT_kids:
                # The child is a Terminal
                for child in self.children:
                    number += 1
                    if number == node_id:
                        return_tree = child
            else:
                for child in NT_kids:
                    return_tree, number = child.return_node_from_id(node_id, number=number, return_tree=return_tree)
        return return_tree, number

    def get_output(self):
        output = []
        for child in self.children:
            if child.children == []:
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
                print ("\nGenome is incorrect")
                print ("Codon productions:\t", prods)
                print ("Actual children:  \t", roots)
                quit()
        for kid in self.children:
            kid.check_genome()

    def check_tree(self):
        """ Checks the entire tree for discrepancies """

        self.check_genome()
        invalid = self.check_expansion()
        if invalid:
            print ("Invalid given tree")
            quit()

        orig_out = deepcopy(self.get_output())
        orig_gen = deepcopy(self.build_genome([]))

        output, genome, tree, nodes, invalid, depth, \
        used_codons = genome_init(orig_gen)

        if invalid:
            print ("Invalid genome tree")
            print ("Original:\t", orig_out)
            print ("Genome:  \t", output)
            quit()

        if orig_out != output:
            print ("Tree output doesn't match genome tree output")
            print ("Original:\t", orig_out)
            print ("Genome:  \t", output)
            quit()

        elif orig_gen != genome:
            print ("Tree genome doesn't match genome tree genome")
            print ("Original:\t", orig_gen)
            print ("Genome:  \t", genome)
            quit()

    def build_genome(self, genome):
        """ Goes through a tree and builds a genome from all codons in the subtree.
        """

        if self.codon:
            genome.append(self.codon)
            # print len(genome), "\tCodon:\t", self.codon, "Root:\t", self.root
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

            productions = params['BNF_GRAMMAR'].rules[self.root]
            selection = genome[index % len(genome)] % len(productions)
            chosen_prod = productions[selection]
            if len(productions) > 1:
                # Codon consumed
                self.codon = genome[index % len(genome)]
                index += 1
            self.children = []

            # print ("\nCurrent root:   \t", self.root)
            # print ("  Choices:      \t", productions)
            # print ("  Chosen Product:\t", chosen_prod)
            # print ("  Current node: \t", nodes)
            # print ("  Current depth:\t", depth)
            # print ("  Current max d:\t", max_depth)

            # if not any([prod[1] == params['BNF_GRAMMAR'].NT for prod in chosen_prod]):
            #     # Branch is completely expanded
            #     depth += 1
            #     nodes += 1

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
        productions = params['BNF_GRAMMAR'].rules[self.root]
        remaining_depth = depth_limit

        available = self.legal_productions(method, remaining_depth, productions)
        chosen_prod = random.choice(available)

        if len(productions) > 1:
            choice = productions.index(chosen_prod)
            codon = random.randrange(len(productions), params['BNF_GRAMMAR'].codon_size, len(productions)) + choice
            self.codon = codon
            genome.append(codon)

        # print "\nCurrent root:   \t", self.root
        # print "  Choices:      \t", productions
        # print "  Chosen Product:\t", chosen_prod
        # print "  Current node: \t", nodes
        # print "  Current depth:\t", depth
        # print "  Current max d:\t", max_depth
        # print "  Remaining depth:\t", remaining_depth

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

            # print "\nCurrent root:   \t", chosen_prod
            # print "  Current node: \t", nodes
            # print "  Current depth:\t", depth

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

        queue = []
        queue.append([self, params['BNF_GRAMMAR'].non_terminals[self.root]['recursive']])

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

        queue = []
        queue.append([self, params['BNF_GRAMMAR'].non_terminals[self.root]['recursive']])

        while queue:
            num = len(queue)
            chosen = random.randint(0, num-1)
            all_node = queue.pop(chosen)
            node = all_node[0]

            if node.get_depth() < max_depth:
                productions = params['BNF_GRAMMAR'].rules[node.root]
                available = []
                remaining_depth = max_depth - node.get_depth()

                if (self.get_max_children(self) < max_depth - 1) or (node.parent == None) or ((all_node[1] and (not any([item[1] for item in queue])))):
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

    def subtree_mutate(self):
        """ Creates a list of all nodes and picks one node at random to mutate.
            Because we have a list of all nodes we can (but currently don't)
            choose what kind of nodes to mutate on. Handy. Should hopefully be
            faster and less error-prone to the previous subtree mutation.
        """

        n = self.get_nodes(0)
        number = random.randint(1, n)
        tree = self.return_node_from_id(number, number=0, return_tree=None)[0]

        while tree.root in params['BNF_GRAMMAR'].terminals:
            number = random.randint(1, n)
            tree = self.return_node_from_id(number, number=0, return_tree=None)[0]

        tree.max_depth = self.depth_limit - tree.get_depth()
        x, y, d, md = tree.derivation([], "random", 0, 0, 0, depth_limit=tree.max_depth)
        genome = self.build_genome([])

        return self.get_output(), genome, self

    def getLabels(self, labels):
        labels.add(self.root)

        for c in self.children:
            labels = c.getLabels(labels)
        return labels

    def print_tree(self):
        print (self)


def subtree_crossover(orig_tree1, orig_tree2):

    # Have to do a deepcopy of original trees as identical trees will give the
    # same class instances for their children.
    copy_tree1 = deepcopy(orig_tree1)
    copy_tree2 = deepcopy(orig_tree2)

    def do_crossover(tree1, tree2, intersection):

        crossover_choice = random.choice(intersection)

        indexes_1, n1 = tree1.get_target_nodes([], target=crossover_choice)
        indexes_1 = list(set(indexes_1))
        number1 = random.choice(indexes_1)
        t1 = tree1.return_node_from_id(number1, number=0, return_tree=None)[0]

        indexes_2, n2 = tree2.get_target_nodes([], target=crossover_choice)
        indexes_2 = list(set(indexes_2))
        number2 = random.choice(indexes_2)
        t2 = tree2.return_node_from_id(number2, number=0, return_tree=None)[0]

        d1 = t1.get_depth()
        d2 = t2.get_depth()

        # when the crossover is between the entire tree of both tree1 and tree2
        if d1 == 1 and d2 == 1:
            return t2, t1
        # when only t1 is the entire tree1
        elif d1 == 1:
            p2 = t2.parent
            tree1 = t2
            try:
                p2.children.index(t2)
            except ValueError:
                print("Error: child not in parent.")
                quit()
            i2 = p2.children.index(t2)
            p2.children[i2] = t1
            t1.parent = p2
            t2.parent = None

        # when only t2 is the entire tree2
        elif d2 == 1:
            p1 = t1.parent
            tree2 = t1
            try:
                p1.children.index(t1)
            except ValueError:
                print("Error: child not in parent")
                quit()
            i1 = p1.children.index(t1)
            p1.children[i1] = t2
            t2.parent = p1
            t1.parent = None

        # when the crossover node for both trees is not the entire tree
        else:
            p1 = t1.parent
            p2 = t2.parent

            i1 = p1.children.index(t1)
            i2 = p2.children.index(t2)

            p1.children[i1] = t2
            p2.children[i2] = t1

            t2.parent = p1
            t1.parent = p2

        return tree1, tree2

    def get_labels(t1, t2):
        return t1.getLabels(set()), t2.getLabels(set())

    labels1, labels2 = get_labels(orig_tree1, orig_tree2)

    def intersect(l1, l2):
        intersection = l1.intersection(l2)
        intersection = list(filter(lambda x: x in [i for i in params['BNF_GRAMMAR'].non_terminals if params['BNF_GRAMMAR'].non_terminals[i]['b_factor'] > 1], intersection))

        return sorted(intersection)

    intersection = intersect(labels1, labels2)

    if len(intersection) != 0:
        # Cross over parts of trees
        ret_tree1, ret_tree2 = do_crossover(copy_tree1, copy_tree2, intersection)
    else:
        # Cross over entire trees
        ret_tree1, ret_tree2 = copy_tree2, copy_tree1

    return ret_tree1, ret_tree1.build_genome([]), ret_tree2, ret_tree2.build_genome([])


def genome_init(genome, depth_limit=20):

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),), None, depth_limit=depth_limit)
    used_codons, nodes, depth, max_depth = tree.genome_derivation(genome, 0, 0, 0, 0)

    invalid = False
    if any([i == "Incomplete" for i in [used_codons, nodes, depth, max_depth]]) or tree.check_expansion():
        invalid = True
    return tree.get_output(), genome, tree, nodes, invalid, max_depth, used_codons


def pi_random_init(depth):

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),), None, max_depth=depth, depth_limit=depth)
    genome = tree.pi_random_derivation(0, max_depth=depth)
    if tree.check_expansion():
        print ("tree.pi_random_init generated an Invalid")
        quit()
    return tree.get_output(), genome, tree, False


def pi_grow_init(depth):

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),), None, max_depth=depth, depth_limit=depth)
    genome = tree.pi_grow(0, max_depth=depth)
    if tree.check_expansion():
        print ("tree.pi_grow_init generated an Invalid")
        quit()
    return tree.get_output(), genome, tree, False


def init(depth, method):

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),), None, max_depth=depth-1, depth_limit=depth-1)
    genome, nodes, d, max_depth = tree.derivation([], method, 0, 0, 0, depth_limit=depth-1)

    if tree.check_expansion():
        print ("tree.init generated an Invalid")
        quit()
    return tree.get_output(), genome, tree, nodes, False, max_depth, len(genome)
