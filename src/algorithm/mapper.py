from algorithm.parameters import params
from random import choice, randrange
from representation.tree import Tree
from collections import deque


def genome_map(_input, max_wraps=0):
    """ The genotype to phenotype mapping process. Map input via rules to
    output. Returns output and used_input. """

    from utilities.helper_methods import python_filter
    # Depth, max_depth, and nodes start from 1 to account for starting root
    MAX_TREE_DEPTH = params['MAX_TREE_DEPTH']
    NT_SYMBOL = params['BNF_GRAMMAR'].NT
    BNF_GRAMMAR = params['BNF_GRAMMAR']
    n_input = len(_input)
    used_input, current_depth, current_max_depth, nodes = 0, 1, 1, 1
    wraps, output = -1, deque()
    unexpanded_symbols = deque([(BNF_GRAMMAR.start_rule, 1)])
    while (wraps < max_wraps) and \
            (unexpanded_symbols) and \
            (current_max_depth <= MAX_TREE_DEPTH):
        # Wrap
        if used_input % n_input == 0 and \
                        used_input > 0 and \
                any([i[0][1] == NT_SYMBOL for i in unexpanded_symbols]):
            wraps += 1

        # Expand a production
        current_item = unexpanded_symbols.popleft()
        current_symbol, current_depth = current_item[0], current_item[1]
        if current_max_depth < current_depth:
            current_max_depth = current_depth

        # Set output if it is a terminal
        if current_symbol[1] != NT_SYMBOL:
            output.append(current_symbol[0])
        else:
            production_choices = BNF_GRAMMAR.rules[current_symbol[0]]
            # Select a production
            # TODO store the length of production choices to avoid len call?
            current_production = _input[used_input % n_input] % \
                                 len(production_choices)
            # Use an input
            used_input += 1
            # Derviation order is left to right(depth-first)
            # TODO is a list comprehension faster? (Only if the loop for
            # counting NT for each production can be avoided, by using a
            # lookup instead
            children = deque()
            NT_count = 0
            for prod in production_choices[current_production]:
                child = [prod, current_depth + 1]
                # Extendleft reverses the order, thus reverse adding
                # WARNING loss of readability and coupling of lines?
                children.appendleft(child)
                # TODO store number of NT to avoid counting and simply do
                # lookup instead?
                if child[0][1] == NT_SYMBOL:
                    NT_count += 1

            unexpanded_symbols.extendleft(children)

            if NT_count > 0:
                nodes += NT_count
            else:
                nodes += 1

    output = "".join(output)

    if len(unexpanded_symbols) > 0:
        # Not completly expanded, invalid solution.
        return None, _input, None, nodes, True, current_max_depth, \
               used_input

    if BNF_GRAMMAR.python_mode:
        output = python_filter(output)

    return output, _input, None, nodes, False, current_max_depth, \
           used_input


def tree_derivation(ind_tree, genome, method, nodes, depth, max_depth,
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
                tree_derivation(ind_tree.children[-1], genome, method, nodes,
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


def genome_tree_map(genome):

    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),),
                None, depth_limit=params['MAX_TREE_DEPTH'])
    used_codons, nodes, depth, max_depth, invalid = \
        genome_tree_derivation(tree, genome, 0, 0, 0, 0)
    if invalid:
        return None, genome, tree, nodes, invalid, max_depth, \
           used_codons
    else:
        return tree.get_output(), genome, tree, nodes, invalid, max_depth, \
           used_codons


def genome_tree_derivation(ind_tree, genome, index, depth, max_depth, nodes,
                           invalid=False):
    """ Builds a tree using production choices from a given genome. Not
        guaranteed to terminate.
    """
    if not invalid and index < len(genome) and\
                    max_depth <= params['MAX_TREE_DEPTH']:
        nodes += 1
        depth += 1
        ind_tree.id, ind_tree.depth = nodes, depth

        productions = params['BNF_GRAMMAR'].rules[ind_tree.root]
        ind_tree.codon = genome[index % len(genome)]
        selection = ind_tree.codon % len(productions)
        chosen_prod = productions[selection]

        index += 1
        ind_tree.children = []

        for i in range(len(chosen_prod)):
            symbol = chosen_prod[i]
            if symbol[1] == "T":
                ind_tree.children.append(Tree((symbol[0],), ind_tree))

            elif symbol[1] == "NT":
                ind_tree.children.append(Tree((symbol[0],), ind_tree))
                index, nodes, d, max_depth, invalid = \
                    genome_tree_derivation(ind_tree.children[-1], genome,
                                           index, depth, max_depth, nodes,
                                           invalid)
    else:
        # Mapping incomplete
        return index, nodes, depth, max_depth, True

    NT_kids = [kid for kid in ind_tree.children if kid.root in
               params['BNF_GRAMMAR'].non_terminals]
    if not NT_kids:
        # Then the branch terminates here
        depth += 1
        nodes += 1

    if not invalid:
        if (depth > max_depth):
            max_depth = depth
        if max_depth > params['MAX_TREE_DEPTH']:
            invalid = True
    return index, nodes, depth, max_depth, invalid
