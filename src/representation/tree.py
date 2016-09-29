from algorithm.parameters import params
from random import choice, randrange


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

    def get_current_depth(self):
        """Get the depth of the current node."""

        count = 1
        current_parent = self.parent
        while current_parent is not None:
            count += 1
            current_parent = current_parent.parent
        return count

    def get_max_tree_depth(self, current, max_d=1):
        """ Returns the maximum depth of the tree from the current node. """

        curr_depth = current.get_current_depth()
        if curr_depth > max_d:
            max_d = curr_depth
        for child in current.children:
            max_d = child.get_max_tree_depth(child, max_d)
        return max_d

    def get_tree_info(self, current, number=0, max_depth=0):
        """ Get the number of nodes and the max depth of the tree.
        """

        number += 1
        if current.root in params['BNF_GRAMMAR'].non_terminals:
            current.id = number
            if current.parent:
                current.depth = current.parent.depth + 1
            else:
                current.depth = 1
            if current.depth > max_depth:
                max_depth = current.depth
            NT_kids = [kid for kid in
                       self.children if kid.root in
                       params['BNF_GRAMMAR'].non_terminals]
            if not NT_kids:
                number += 1
            else:
                for child in NT_kids:
                    max_depth, number = child.get_tree_info(child,
                                                            number,
                                                            max_depth)

        return max_depth, number

    def get_target_nodes(self, array, target=None):
        """ Returns the ids of all NT nodes which match the target NT list in a
            given tree.
        """

        if self.root in params['BNF_GRAMMAR'].non_terminals:
            if self.root in target:
                array.append(self.id)
            NT_kids = [kid for kid in self.children if kid.root in
                       params['BNF_GRAMMAR'].non_terminals]
            if NT_kids:
                for child in NT_kids:
                    array = child.get_target_nodes(array, target=target)
        return array

    def get_output(self):
        output = []
        for child in self.children:
            if not child.children:
                output.append(child.root)
            else:
                output += child.get_output()
        return "".join(output)

    def return_node_from_id(self, node_id, return_tree=None):
        """ Returns a specific node given a node id. Can only return NT nodes.
        """

        if self.id == node_id:
            return_tree = self
        elif self.root in params['BNF_GRAMMAR'].non_terminals:
            NT_kids = [kid for kid in self.children if kid.root in
                       params['BNF_GRAMMAR'].non_terminals]
            # We only want to look at children who are NTs themselves. If the
            # kids are Ts then we don't need to look in their tree.
            if NT_kids:
                for child in NT_kids:
                    return_tree = \
                        child.return_node_from_id(node_id,
                                                  return_tree=return_tree)
        return return_tree

    def get_labels(self, labels):
        labels.add(self.root)

        for c in self.children:
            labels = c.get_labels(labels)
        return labels

    def print_tree(self):
        print(self)

    def build_genome(self, genome):
    # Goes through a tree and builds a genome from all codons in the subtree.

        if self.codon:
            genome.append(self.codon)
        for kid in self.children:
            genome = kid.build_genome(genome)
        return genome

    def fast_genome_derivation(self, genome, index=0):
        """ Builds a tree using production choices from a given genome. Not
            guaranteed to terminate.
        """

        if index != "Incomplete" and index < len(genome):

            productions = params['BNF_GRAMMAR'].rules[self.root]
            selection = genome[index % len(genome)] % len(productions)
            chosen_prod = productions[selection]
            self.codon = genome[index % len(genome)]
            index += 1
            self.children = []

            for i in range(len(chosen_prod)):
                symbol = chosen_prod[i]
                if symbol[1] == params['BNF_GRAMMAR'].T:
                    self.children.append(Tree((symbol[0],), self))

                elif symbol[1] == params['BNF_GRAMMAR'].NT:
                    self.children.append(Tree((symbol[0],), self))
                    index = self.children[-1].fast_genome_derivation(genome,
                                                                     index)
        else:
            # Mapping incomplete
            return "Incomplete"
        return index

    def legal_productions(self, method, remaining_depth, productions):
        """ Returns the available production choices for a node given a depth
            limit """

        available = []

        if method == "random":
            if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                available = productions
            elif remaining_depth <= 0:
                min_path = min([max([item[2] for item in prod]) for
                                prod in productions])
                shortest = [prod for prod in productions if
                            max([item[2] for item in prod]) == min_path]
                available = shortest
            else:
                for prod in productions:
                    prod_depth = max([item[2] for item in prod])
                    if prod_depth < remaining_depth:
                        available.append(prod)
                if not available:
                    min_path = min([max([item[2] for item in prod]) for
                                    prod in productions])
                    shortest = [prod for prod in productions if
                                max([item[2] for item in prod]) == min_path]
                    available = shortest

        elif method == "full":
            if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                for production in productions:
                    if any(sym[3] for sym in production):
                        available.append(production)
                if not available:
                    for production in productions:
                        if not all(sym[3] for sym in production):
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
                            if (item[1] == params['BNF_GRAMMAR'].NT) and \
                                    (item[2] > prod_depth):
                                prod_depth = item[2]
                        if prod_depth < remaining_depth:
                            available.append(prod)
        return available

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


def generate_tree(ind_tree, genome, method, nodes, depth, max_depth,
                  depth_limit):
    """ Derive a tree using a given method """

    nodes += 1
    depth += 1
    ind_tree.id, ind_tree.depth = nodes, depth

    productions = params['BNF_GRAMMAR'].rules[ind_tree.root]
    available = ind_tree.legal_productions(method, depth_limit, productions)
    chosen_prod = choice(available)

    prod_choice = productions.index(chosen_prod)
    codon = randrange(len(productions), params['BNF_GRAMMAR'].codon_size,
                      len(productions)) + prod_choice
    ind_tree.codon = codon
    genome.append(codon)
    ind_tree.children = []

    for symbol in chosen_prod:
        if symbol[1] == params['BNF_GRAMMAR'].T:
            # if the right hand side is a terminal
            ind_tree.children.append(Tree((symbol[0],), ind_tree))
        elif symbol[1] == params['BNF_GRAMMAR'].NT:
            # if the right hand side is a non-terminal
            ind_tree.children.append(Tree((symbol[0],), ind_tree))
            genome, nodes, d, max_depth = \
                generate_tree(ind_tree.children[-1], genome, method, nodes,
                              depth, max_depth, depth_limit - 1)

    NT_kids = [kid for kid in ind_tree.children if kid.root in
               params['BNF_GRAMMAR'].non_terminals]

    if not NT_kids:
        # Then the branch terminates here
        depth += 1
        nodes += 1

    if depth > max_depth:
        max_depth = depth

    return genome, nodes, depth, max_depth
