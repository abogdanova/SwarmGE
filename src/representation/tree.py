#! /usr/bin/env python

# Tree class
# Copyright (c) 2015 James McDermott and Michael Fenton
# Hereby licensed under the GNU GPL v3.

from os import getcwd, path, mkdir
import matplotlib.pyplot as plt
import random, copy
import numpy as np

#NEED TO TEST THAT THIS WORKS
#MIGHT NEED TO PASS RANDOM AROUND OR HAVE RANDOM SET IN PARAMETERS.PY
# FIXME delete this and check that RNG is working correctly throughout
random.seed(10)

class Tree:

    def __init__(self, expr, parent, max_depth=20, depth_limit=20):
        self.parent = parent
        self.max_depth = max_depth
        self.codon = None
        self.index = None
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
        self.grammar = None

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

        count = 0
        currentParent = self.parent
        while currentParent != None:
            count += 1
            currentParent = currentParent.parent
        return count

    def get_max_children(self, current, max_D=0):
        """ The distance from the current node to the furthest branched NT in
            the given tree (returns the maximum depth of the tree).
        """

        if current.get_depth() > max_D:
            max_D = current.get_depth()
        for child in current.children:
            max_D = current.get_max_children(child, max_D)
        return max_D

    def get_overall_tree_depth(self):
        """ Given a subtree, returns the overall max tree depth of the entire
            tree."""
        if not self.parent:
            return self.get_max_children(self, 0)
        else:
            currentParent = self.parent
            while currentParent != None:
                if currentParent.parent == None:
                    break
                else:
                    currentParent = currentParent.parent
            return currentParent.get_max_children(currentParent, 0)

    def get_nodes(self, number=0):
        """ Returns the total number of nodes in a given tree.
        """

        if self.codon:
            number += 1

        if self.root in self.grammar.non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in self.grammar.non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            for child in NT_kids:
                number = child.get_nodes(number)
        return number

    def get_node_ids(self, number=0, n_list=[]):
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
        if self.root in self.grammar.non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in self.grammar.non_terminals]
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
                    number, n_list = child.get_node_ids(number=number, n_list=n_list)
        return number, n_list

    def return_node_from_id(self, node_id, number=0, return_tree=None):
        """ Returns the total number of nodes in a given tree.
        """

        if self.codon:
            number += 1
        if (number == node_id) and (return_tree == None):
            return_tree = self
        elif self.root in self.grammar.non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in self.grammar.non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if not NT_kids:
                # The child is a Terminal
                for child in self.children:
                    if child.codon:
                        number += 1
                    if (number == node_id) and (return_tree == None):
                        return_tree = child
            else:
                for child in NT_kids:
                    return_tree, number = child.return_node_from_id(node_id, number, return_tree)
        return return_tree, number

    def get_random(self, prob):
        r = random.random()
        if r < prob or len(self.children) == 0:
            return self
        else:
            return random.choice(self.children).get_random(prob)

    def get_output(self):
        output = []
        for child in self.children:
            if child.children == []:
                output.append(child.root)
            else:
                output += child.get_output()
        return "".join(output)

    def build_genome(self, genome=[]):
        """ Goes through a tree and builds a genome from all codons in the subtree.
        """

        if self.children and self.codon:
            genome.append(self.codon)
        for kid in self.children:
            genome = kid.build_genome(genome)
        return genome

    def check_terminal_depths(self, depths):
        """ Check what depths all terminal children are at. Returns a list of
            said depths."""

        if self.root in self.grammar.non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in self.grammar.non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if not NT_kids:
                # The child is a Terminal
                for child in self.children:
                    depths.append(child.get_depth())
            else:
                for child in NT_kids:
                    depths = child.check_terminal_depths(depths)
        return depths

    def genome_derivation(self, genome, grammar, index):
        """ Builds a tree using production choices from a given genome. Not
            guaranteed to terminate.
        """

        if index < len(genome):
            self.grammar = grammar
            productions = grammar.rules[self.root]
            selection = genome[index % len(genome)] % len(productions)
            chosen_prod = productions[selection]
            self.codon = genome[index % len(genome)]
            if len(productions) > 1:
                index += 1
            self.children = []

            for i in range(len(chosen_prod)):
                symbol = chosen_prod[i]
                if symbol[1] == grammar.T:
                    #if the right hand side is a terminal
                    self.children.append(Tree((symbol[0],),self))
                elif symbol[1] == grammar.NT:
                    # if the right hand side is a non-terminal
                    self.children.append(Tree((symbol[0],),self))
                    index = self.children[-1].genome_derivation(genome, grammar, index)
        else:
            # Mapping incomplete
            return "Incomplete"
        return index

    def random_derivation(self, genome, grammar, index, max_depth=20):
        """ Randomly builds a tree from a given root node up to a given depth.
        """

        self.grammar = grammar
        productions = grammar.rules[self.root]
        available = []
        remaining_depth = max_depth

        if remaining_depth > grammar.max_arity:
            available = productions
        else:
            for prod in productions:
                depth = 0
                for item in prod:
                    if (item[1] == grammar.NT) and (item[2] > depth):
                        depth = item[2]
                if depth < remaining_depth:
                    available.append(prod)

        chosen_prod = random.choice(available)
        if len(productions) > 1:
            choice = productions.index(chosen_prod)
            codon = random.randrange(0, grammar.codon_size, len(productions)) + choice
            self.codon = codon
            self.index = index
            index += 1
            genome.append(codon)
        self.children = []
        for i in range(len(chosen_prod)):
            symbol = chosen_prod[i]
            if symbol[1] == grammar.T:
                #if the right hand side is a terminal
                self.children.append(Tree((symbol[0],),self))
            elif symbol[1] == grammar.NT:
                # if the right hand side is a non-terminal
                self.children.append(Tree((symbol[0],),self))
                genome, index = self.children[-1].random_derivation(genome, grammar, index, max_depth=max_depth-1)
        return genome, index

    def pi_random_derivation(self, grammar, index, max_depth=20):
        """ Randomly builds a tree from a given root node up to a maximum
            given depth. Uses position independent stuff.
        """

        queue = []
        queue.append([self, grammar.non_terminals[self.root]['recursive']])

        while queue:
            num = len(queue)
            chosen = random.randint(0, num-1)
            all_node = queue.pop(chosen)
            node = all_node[0]

            if node.get_depth() < max_depth:
                node.grammar = grammar
                productions = grammar.rules[node.root]
                available = []
                remaining_depth = max_depth - node.get_depth()

                if remaining_depth > grammar.max_arity:
                    available = productions
                else:
                    for prod in productions:
                        depth = 0
                        for item in prod:
                            if (item[1] == grammar.NT) and (item[2] > depth):
                                depth = item[2]
                        if depth < remaining_depth:
                            available.append(prod)
                chosen_prod = random.choice(available)
                if len(productions) > 1:
                    prod_choice = productions.index(chosen_prod)
                    codon = random.randrange(0, grammar.codon_size, len(productions)) + prod_choice
                    node.codon = codon
                    node.index = index
                    index += 1
                node.children = []

                for i in range(len(chosen_prod)):
                    symbol = chosen_prod[i]
                    child = Tree((symbol[0],),node)
                    node.children.append(child)
                    if symbol[1] == grammar.NT:
                        # if the right hand side is a non-terminal
                        queue.insert(chosen+i, [child, grammar.non_terminals[child.root]['recursive']])
        genome = self.build_genome([])
        return genome, index

    def grow(self, genome, grammar, index, max_depth=20):
        """ Grows a tree until a single branch reaches a specified depth. Does
            this by only using recursive production choices until a single
            branch of the tree has reached the specified maximum depth. After
            that any choices are allowed
        """

        allowable = self.get_overall_tree_depth()
        if allowable < max_depth - 1:
            # We want to prevent the tree from creating terminals until a
            # single branch has reached the full depth
            if self.get_depth() < max_depth:
                self.grammar = grammar
                productions = grammar.rules[self.root]
                available = []
                remaining_depth = max_depth - self.get_depth()
                if remaining_depth > grammar.max_arity:
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
                            if (item[1] == grammar.NT) and (item[2] > depth):
                                depth = item[2]
                        if depth < remaining_depth:
                            available.append(prod)
                chosen_prod = random.choice(available)
                if len(productions) > 1:
                    choice = productions.index(chosen_prod)
                    codon = random.randrange(0, grammar.codon_size, len(productions)) + choice
                    genome.append(codon)
                    self.codon = codon
                    self.index = index
                    index += 1
                self.children = []

                for i in range(len(chosen_prod)):
                    symbol = chosen_prod[i]
                    if symbol[1] == grammar.T:
                        #if the right hand side is a terminal
                        self.children.append(Tree((symbol[0],),self))
                    elif symbol[1] == grammar.NT:
                        # if the right hand side is a non-terminal
                        self.children.append(Tree((symbol[0],),self))
                        genome, index = self.children[-1].grow(genome, grammar, index, max_depth=max_depth)
        else:
            # A node in the tree has reached the depth limit, fill out the rest
            # of the tree as normal
            depth_limit = max_depth - self.get_depth()
            self.max_depth = depth_limit
            genome, index = self.random_derivation(genome, grammar, index, max_depth=depth_limit)
        return genome, index

    def pi_grow(self, grammar, index, max_depth=20):
        """ Grows a tree until a single branch reaches a specified depth. Does
            this by only using recursive production choices until a single
            branch of the tree has reached the specified maximum depth. After
            that any choices are allowed
        """

        queue = []
        queue.append([self, grammar.non_terminals[self.root]['recursive']])

        while queue:
            num = len(queue)
            chosen = random.randint(0, num-1)
            all_node = queue.pop(chosen)
            node = all_node[0]

            if node.get_depth() < max_depth:
                node.grammar = grammar
                productions = grammar.rules[node.root]
                available = []
                remaining_depth = max_depth - node.get_depth()

                if (self.get_max_children(self) < max_depth - 1) or (node.parent == None) or ((all_node[1] and (not any([item[1] for item in queue])))):
                    # We want to prevent the tree from creating terminals
                    # until a single branch has reached the full depth

                    if remaining_depth > grammar.max_arity:
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
                                if (item[1] == grammar.NT) and (item[2] > depth):
                                    depth = item[2]
                            if depth < remaining_depth:
                                available.append(prod)
                else:
                    if remaining_depth > grammar.max_arity:
                        available = productions
                    else:
                        for prod in productions:
                            depth = 0
                            for item in prod:
                                if (item[1] == grammar.NT) and (item[2] > depth):
                                    depth = item[2]
                            if depth < remaining_depth:
                                available.append(prod)
                chosen_prod = random.choice(available)
                if len(productions) > 1:
                    prod_choice = productions.index(chosen_prod)
                    codon = random.randrange(0, grammar.codon_size, len(productions)) + prod_choice
                    node.codon = codon
                    node.index = index
                    index += 1
                node.children = []

                for i in range(len(chosen_prod)):
                    symbol = chosen_prod[i]
                    child = Tree((symbol[0],),node)
                    node.children.append(child)
                    if symbol[1] == grammar.NT:
                        # if the right hand side is a non-terminal
                        queue.insert(chosen+i, [child, grammar.non_terminals[child.root]['recursive']])
        genome = self.build_genome([])
        return genome, index

    def full(self, genome, grammar, index, max_depth=20):
        """ Grows a tree until all branches have reached a specified depth. Does this by only using recursive production choices until all
            branches of the tree have reached the specified maximum depth.
            After that, any choices are allowed
        """

        if self.get_depth() < max_depth:
            self.grammar = grammar
            productions = grammar.rules[self.root]
            available = []
            remaining_depth = max_depth - self.get_depth()
            if remaining_depth > grammar.max_arity:
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
                        if (item[1] == grammar.NT) and (item[2] > depth):
                            depth = item[2]
                    if depth == remaining_depth - 1:
                        available.append(prod)
                if not available:
                    # Then we don't have what we're looking for
                    for prod in productions:
                        depth = 0
                        for item in prod:
                            if (item[1] == grammar.NT) and (item[2] > depth):
                                depth = item[2]
                        if depth < remaining_depth:
                            available.append(prod)
            chosen_prod = random.choice(available)

            if len(productions) > 1:
                choice = productions.index(chosen_prod)
                codon = random.randrange(0, grammar.codon_size, len(productions)) + choice
                self.codon = codon
                self.index = index
                index += 1
                genome.append(codon)
            self.children = []
            for i in range(len(chosen_prod)):
                symbol = chosen_prod[i]
                if symbol[1] == grammar.T:
                    #if the right hand side is a terminal
                    self.children.append(Tree((symbol[0],),self))
                elif symbol[1] == grammar.NT:
                    # if the right hand side is a non-terminal
                    self.children.append(Tree((symbol[0],),self))
                    genome, index = self.children[-1].full(genome, grammar, index, max_depth=max_depth)
        return genome, index

    def check_expansion(self, grammar):
        """ Check if a given tree is completely expanded or not. Return boolean
            True if the tree IS NOT completely expanded.
        """

        check = False
        if self.root in grammar.non_terminals.keys():
            # Current node is a NT and should have children
            if self.children:
                # Everything is as expected
                for child in self.children:
                    check = child.check_expansion(grammar)
                    if check:
                        break
            else:
                # Current node is not completely expanded
                check = True
        return check

    def slow_subtree_mutate(self):
        """ Creates a list of all nodes and picks one node at random to mutate.
            Because we have a list of all nodes we can (but currently don't)
            choose what kind of nodes to mutate on. Handy. Should hopefully be
            faster and less error-prone to the previous subtree mutation.
        """

        n, node_list = self.get_node_ids(number=0, n_list=[])

        node = random.choice(node_list)
        tree = node[2]
        while tree.root in self.grammar.terminals:
            node = random.choice(node_list)
            tree = node[2]
        tree.max_depth = self.depth_limit - node[4]

        #grow (based on grammar) from random node, with a given depth limit
        x, y = tree.random_derivation([], self.grammar, 0, max_depth=tree.max_depth)
        if tree.check_expansion(self.grammar):
            print "Invalid"
        genome = self.build_genome([])

        return self.get_output(), genome, self

    def subtree_mutate(self):
        """ Creates a list of all nodes and picks one node at random to mutate.
            Because we have a list of all nodes we can (but currently don't)
            choose what kind of nodes to mutate on. Handy. Should hopefully be
            faster and less error-prone to the previous subtree mutation.
        """

        n = self.get_nodes()
        number = random.randint(1, n)
        tree = self.return_node_from_id(number)[0]
        tree.max_depth = self.depth_limit - tree.get_depth()

        #grow (based on grammar) from random node, with a given depth limit
        x, y = tree.random_derivation([], self.grammar, 0, max_depth=tree.max_depth)
        if tree.check_expansion(self.grammar):
            print "Invalid"
        genome = self.build_genome([])

        return self.get_output(), genome, self

    def leaf_mutate(self):
        """ Mutates a random leaf node from a given tree.
        """
        # Choose a random NT from the tree which has all T children
        tree = self.get_random(0.1)
        check = [kid.root in tree.grammar.terminals for kid in tree.children]
        while not check or (all(check) != True):
            tree = self.get_random(0.1)
            check = [kid.root in tree.grammar.terminals for kid in tree.children]
        # New production choices are those productions which are terminals
        productions = tree.grammar.rules[tree.root]
        available = [i for i in productions if all([sym[1] == 'T' for sym in i]) == True]
        chosen_prod = random.choice(available)
        if len(productions) > 1:
            choice = productions.index(chosen_prod)
            codon = random.randrange(0, tree.grammar.codon_size, len(productions)) + choice
            tree.codon = codon
        tree.children = []
        for i in range(len(chosen_prod)):
            symbol = chosen_prod[i]
            tree.children.append(Tree((symbol[0],),tree))
        if tree.check_expansion(self.grammar):
            print "Invalid"
        genome = self.build_genome([])
        return self.get_output(), genome, self

    def getLabels(self):
        labels = [self.root]

        for c in self.children:
            labels.extend(c.getLabels())
        return set(labels)

    def get_imbalance(self, current, array, names):
        """ Calculate the imbalance of a given tree (i.e. is the tree left or
            right-biased)."""

        if self.root in self.grammar.non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in self.grammar.non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if not NT_kids:
                # The child is a Terminal
                for child in self.children:
                    array.append(-child.get_depth())
                    if child.root[-1] == "(":
                        names.append(child.root[:-1])
                    else:
                        names.append(child.root)
            else:
                for child in NT_kids:
                    array, names = child.get_imbalance(child, array, names)
        return array, names

    def print_tree(self, name):
        """ Print out the tree for all to see."""

        file_path = getcwd()
        if not path.isdir(str(file_path) + "/Tree_graphs"):
            mkdir(str(file_path) + "/Tree_graphs")

        arr, names = self.get_imbalance(self, [], [])
        x = range(len(arr))
        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1)
        ax1.axes.get_xaxis().set_visible(False)
        ax1.set_frame_on(False)
        ax1.plot(x, arr, "r.")

        slope, constant = get_best_fit(arr)
        ax1.plot(x, [i*slope+constant for i in x], "-")

        for label, a, b in zip(names, x, arr):
            ax1.annotate(
                label,
                xy = (a, b))
        plt.savefig(getcwd()+'/Tree_graphs/' + str(name) + '.pdf')
        plt.close()

    def get_tree_stats(self):
        """ Get the following statistics from a given tree:
                Node count
                Phenotype length
                Root bias
                Slope of line of best fit
        """

        node_count = self.get_nodes(0)
        arr, names = self.get_imbalance(self, [], [])
        phenotype_length = len(arr)
        max_depth = abs(min(arr))
        if phenotype_length == 1:
            slope = 0
        else:
            slope, constant = get_best_fit(arr)
        root = max(arr)
        position = arr.index(root)
        if position:
            position += 1
        root_bias = (position/float(len(arr)))*100

        return [node_count, phenotype_length, root_bias, slope, max_depth], arr

def get_best_fit(y):
    """ Get the line of best fit given a list of points"""

    x = range(len(y))
    slope, constant = np.polyfit(x, y, 1)
    return slope, constant

def original_subtree_crossover(tree1, tree2):
    tree1 = copy.deepcopy(tree1)
    tree2 = copy.deepcopy(tree2)

    labels1 = tree1.getLabels()
    labels2 = tree2.getLabels()
    intersection = labels1.intersection(labels2)

    intersection = filter(lambda x: x in tree1.grammar.non_terminals, intersection)
    #see if there is a label to do a crossover
    if len(intersection) != 0:
       # print "1\t", tree1.get_output()
       # print "2\t", tree2.get_output()
       # print "  intersection", intersection

        t1 = tree1.get_random(0.1)

        #finds the nodes to crossover at
        while t1.root not in intersection:
            t1 = tree1.get_random(0.1)
       # print "  t1\t", t1.root, "\t", t1.get_output(), "\t", t1
        t2 = tree2.get_random(0.1)
       # print "  t2\t",  t2.root, "\t", t2.get_output(), "\t", t2
        while t2.root != t1.root:
            t2 = tree2.get_random(0.1)
           # print t2.root

        d1 = t1.get_depth()
        d2 = t2.get_depth()

        # when the crossover is between the entire tree of both tree1 and tree2
        if d1 == 0 and d2 == 0:
            return t2, t2.build_genome([]), t1, t1.build_genome([])
        #when only t1 is the entire tree1
        elif d1 == 0:
            p2 = t2.parent
            tree1 = t2
            try:
                p2.children.index(t2)
            except ValueError:
                print "Error: child not in parent."
                quit()
            i2 = p2.children.index(t2)
            p2.children[i2] = t1
            t1.parent = p2
            t2.parent = None
        #when only t2 is the entire tree2
        elif d2 == 0:
            p1 = t1.parent
            tree2 = t1
            try:
                p1.children.index(t1)
            except ValueError:
                print "Error: child not in parent"
                quit()
            i1 = p1.children.index(t1)
            p1.children[i1] = t2
            t2.parent = p1
            t1.parent = None
        #when the crossover node for both trees is not the entire tree
        else:
            p1 = t1.parent
            p2 = t2.parent
            i1 = p1.children.index(t1)
            i2 = p2.children.index(t2)

            p1.children[i1] = t2
            p2.children[i2] = t1

            t2.parent = p1
            t1.parent = p2
    return tree1, tree1.build_genome([]), tree2, tree2.build_genome([])

def slow_subtree_crossover(orig_tree1, orig_tree2):

    def do_crossover(tree1, tree2, intersection):
        tree1 = copy.deepcopy(orig_tree1)
        tree2 = copy.deepcopy(orig_tree2)

        crossover_choice = random.choice(intersection)

        n1, node_list1 = tree1.get_node_ids(number=0, n_list=[])
        n2, node_list2 = tree2.get_node_ids(number=0, n_list=[])

       # print "-----"
       # print "  0  t1\t", node_list1[0][4], node_list1[0][5], node_list1[0][4]+ node_list1[0][5]
       # print "  0  t2\t", node_list2[0][4], node_list2[0][5], node_list2[0][4]+ node_list2[0][5]

        chosen_node1 = random.choice([i for i in node_list1 if (i[1] == crossover_choice)])
        t1 = chosen_node1[2]
        while (t1.root in tree1.grammar.terminals):
            chosen_node1 = random.choice([i for i in node_list1 if i[1] == crossover_choice])
            t1 = chosen_node1[2]

        chosen_node2 = random.choice([i for i in node_list2 if i[1] == crossover_choice])
        t2 = chosen_node2[2]
        while (t2.root in tree2.grammar.terminals):
            chosen_node2 = random.choice([i for i in node_list2 if i[1] == crossover_choice])
            t2 = chosen_node2[2]

        d1 = chosen_node1[4]
        d2 = chosen_node2[4]

       # print "  1  t1\t", d1, "\t", t1.get_max_children(t1, 0)
       # print "  1  t2\t", d2, "\t", t2.get_max_children(t2, 0)

        # when the crossover is between the entire tree of both tree1 and tree2
        if d1 == 0 and d2 == 0:
            return t2, t2.build_genome([]), t1, t1.build_genome([])
        #when only t1 is the entire tree1
        elif d1 == 0:
            p2 = t2.parent
            tree1 = t2
            try:
                p2.children.index(t2)
            except ValueError:
                print "Error: child not in parent."
                quit()
            i2 = p2.children.index(t2)
            p2.children[i2] = t1
            t1.parent = p2
            t2.parent = None
        #when only t2 is the entire tree2
        elif d2 == 0:
            p1 = t1.parent
            tree2 = t1
            try:
                p1.children.index(t1)
            except ValueError:
                print "Error: child not in parent"
                quit()
            i1 = p1.children.index(t1)
            p1.children[i1] = t2
            t2.parent = p1
            t1.parent = None
        #when the crossover node for both trees is not the entire tree
        else:
            p1 = t1.parent
            p2 = t2.parent
            i1 = p1.children.index(t1)
            i2 = p2.children.index(t2)

            p1.children[i1] = t2
            p2.children[i2] = t1

            t2.parent = p1
            t1.parent = p2

    tree1 = copy.deepcopy(orig_tree1)
    tree2 = copy.deepcopy(orig_tree2)

    labels1 = tree1.getLabels()
    labels2 = tree2.getLabels()
    intersection = labels1.intersection(labels2)

    intersection = filter(lambda x: x in tree1.grammar.non_terminals, intersection)

   # dt1 = tree1.get_max_children(tree1, 0)
   # dt2 = tree2.get_max_children(tree2, 0)

    #see if there is a label to do a crossover
    if len(intersection) != 0:

        do_crossover(tree1, tree2, intersection)
       # dt1 = tree1.get_max_children(tree1, 0)
       # dt2 = tree2.get_max_children(tree2, 0)
        while False:# (dt1 > tree1.depth_limit) or (dt2 > tree2.depth_limit):
            print "Repeating myself"
            do_crossover(intersection)
            dt1 = tree1.get_max_children(tree1, 0)
            dt2 = tree2.get_max_children(tree2, 0)
            quit()

       # print "  2  t1\t", tree1.get_output(), "\t", tree1
       # print "  2  t2\t", tree2.get_output(), "\t", tree2

       # print "  2  t1\t", dt1
       # print "  2  t2\t", dt2
   # if (dt1 > tree1.depth_limit) or (dt2 > tree2.depth_limit):
   #     print "Ass"
   #     quit()
    return tree1, tree2.build_genome([]), tree2, tree2.build_genome([])

def subtree_crossover(orig_tree1, orig_tree2):

    def do_crossover(tree1, tree2, intersection):
        tree1 = copy.deepcopy(orig_tree1)
        tree2 = copy.deepcopy(orig_tree2)

        crossover_choice = random.choice(intersection)

        n1 = tree1.get_nodes()
        number1 = random.randint(1, n1)
        t1 = tree1.return_node_from_id(number1)[0]

        while t1.root not in intersection:
            n1 = tree1.get_nodes()
            number1 = random.randint(1, n1)
            t1 = tree1.return_node_from_id(number1)[0]

        n2 = tree2.get_nodes()
        number2 = random.randint(1, n2)
        t2 = tree2.return_node_from_id(number2)[0]

        while t2.root not in intersection:
            n2 = tree2.get_nodes()
            number2 = random.randint(1, n2)
            t2 = tree2.return_node_from_id(number2)[0]

        d1 = t1.get_depth()
        d2 = t2.get_depth()

        # when the crossover is between the entire tree of both tree1 and tree2
        if d1 == 0 and d2 == 0:
            return t2, t2.build_genome(), t1, t1.build_genome()
        #when only t1 is the entire tree1
        elif d1 == 0:
            p2 = t2.parent
            tree1 = t2
            try:
                p2.children.index(t2)
            except ValueError:
                print "Error: child not in parent."
                quit()
            i2 = p2.children.index(t2)
            p2.children[i2] = t1
            t1.parent = p2
            t2.parent = None
        #when only t2 is the entire tree2
        elif d2 == 0:
            p1 = t1.parent
            tree2 = t1
            try:
                p1.children.index(t1)
            except ValueError:
                print "Error: child not in parent"
                quit()
            i1 = p1.children.index(t1)
            p1.children[i1] = t2
            t2.parent = p1
            t1.parent = None
        #when the crossover node for both trees is not the entire tree
        else:
            p1 = t1.parent
            p2 = t2.parent
            i1 = p1.children.index(t1)
            i2 = p2.children.index(t2)

            p1.children[i1] = t2
            p2.children[i2] = t1

            t2.parent = p1
            t1.parent = p2

    tree1 = copy.deepcopy(orig_tree1)
    tree2 = copy.deepcopy(orig_tree2)

    labels1 = tree1.getLabels()
    labels2 = tree2.getLabels()
    intersection = labels1.intersection(labels2)

    intersection = filter(lambda x: x in [i for i in tree1.grammar.non_terminals if tree1.grammar.non_terminals[i]['b_factor'] > 1], intersection)

    #see if there is a label to do a crossover
    if len(intersection) != 0:

        do_crossover(tree1, tree2, intersection)
       # dt1 = tree1.get_max_children(tree1, 0)
       # dt2 = tree2.get_max_children(tree2, 0)
        while False:# (dt1 > tree1.depth_limit) or (dt2 > tree2.depth_limit):
            do_crossover(intersection)
            dt1 = tree1.get_max_children(tree1, 0)
            dt2 = tree2.get_max_children(tree2, 0)
            quit()

   # if (dt1 > tree1.depth_limit) or (dt2 > tree2.depth_limit):
   #     print "Depth limit exceeded in crossover"
   #     quit()
    return tree1, tree2.build_genome([]), tree2, tree2.build_genome([])

def genome_init(grammar, genome, counter="test"):
    tree = Tree((str(grammar.start_rule[0]),), None)
    index = tree.genome_derivation(genome, grammar, 0)
    if tree.check_expansion(grammar):
        print "tree.genome_init generated an Invalid\n\nRandomly generating a new tree..."
        new_out, new_gen, new_tree, new_nodes, nothing = random_init(grammar, tree.max_depth)
        return new_out, [new_gen, len(new_gen)], new_tree, new_nodes, True
    else:
        return tree.get_output(), index, tree, index, False

def random_init(grammar, depth, counter="test"):
    tree = Tree((str(grammar.start_rule[0]),), None, max_depth=depth)
    genome, nodes = tree.random_derivation([], grammar, 0, max_depth=depth)
    if tree.check_expansion(grammar):
        print "tree.random_init generated an Invalid"
        quit()
    return tree.get_output(), genome, tree, nodes, False

def pi_random_init(grammar, depth, counter="test"):
    tree = Tree((str(grammar.start_rule[0]),), None, max_depth=depth)
    genome, nodes = tree.pi_random_derivation(grammar, 0, max_depth=depth)
    if tree.check_expansion(grammar):
        print "tree.pi_random_init generated an Invalid"
        quit()
    return tree.get_output(), genome, tree, nodes, False

def grow_init(grammar, depth, counter="test"):
    tree = Tree((str(grammar.start_rule[0]),), None, max_depth=depth)
    tree.depth_limit = depth
    genome, nodes = tree.grow([], grammar, 0, max_depth=depth)
    if tree.check_expansion(grammar):
        print "tree.grow_init generated an Invalid"
        quit()
    return tree.get_output(), genome, tree, nodes, False

def pi_grow_init(grammar, depth, counter="test"):
    tree = Tree((str(grammar.start_rule[0]),), None, max_depth=depth)
    genome, nodes = tree.pi_grow(grammar, 0, max_depth=depth)
    if tree.check_expansion(grammar):
        print "tree.pi_grow_init generated an Invalid"
        quit()
    return tree.get_output(), genome, tree, nodes, False

def full_init(grammar, depth, counter="test"):
    tree = Tree((str(grammar.start_rule[0]),), None, max_depth=depth)
    genome, nodes = tree.full([], grammar, 0, max_depth=depth)
    if tree.check_expansion(grammar):
        print "tree.full_init generated an Invalid"
        quit()
    return tree.get_output(), genome, tree, nodes, False
