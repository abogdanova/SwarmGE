from algorithm.parameters import params
from random import choice, randrange


def genome_map(_input, max_wraps=0):
    """ The genotype to phenotype mapping process. Map input via rules to
    output. Returns output and used_input. """
    # TODO check tree depths to see if correct
    from utilities.helper_methods import python_filter
    used_input, current_depth, current_max_depth, nodes = 0, 0, 0, 1
    wraps, output, production_choices = -1, [], []
    unexpanded_symbols = [(params['BNF_GRAMMAR'].start_rule, 0)]

    while (wraps < max_wraps) and \
            (len(unexpanded_symbols) > 0) and \
            (current_max_depth <= params['MAX_TREE_DEPTH']):
        # Wrap
        if used_input % len(_input) == 0 and \
                        used_input > 0 and \
                any([i[0][1] == "NT" for i in unexpanded_symbols]):
            wraps += 1

        # Expand a production
        current_item = unexpanded_symbols.pop(0)
        current_symbol, current_depth = current_item[0], current_item[1]
        if current_max_depth < current_depth:
            current_max_depth = current_depth
        # Set output if it is a terminal
        if current_symbol[1] != params['BNF_GRAMMAR'].NT:
            output.append(current_symbol[0])

        else:
            production_choices = params['BNF_GRAMMAR'].rules[current_symbol[0]]
            # Select a production
            current_production = _input[used_input % len(_input)] % \
                                 len(production_choices)
            # Use an input
            used_input += 1
            # Derviation order is left to right(depth-first)
            children = []
            for prod in production_choices[current_production]:
                children.append([prod, current_depth+ 1])

            NT_kids = [child for child in children if child[0][1] == "NT"]
            if any(NT_kids):
                nodes += len(NT_kids)
            else:
                nodes += 1
            unexpanded_symbols = children + unexpanded_symbols

    if len(unexpanded_symbols) > 0:
        # Not completly expanded, invalid solution.
        return output, _input, None, nodes, True, current_max_depth + 1, \
               used_input

    output = "".join(output)
    if params['BNF_GRAMMAR'].python_mode:
        output = python_filter(output)
    return output, _input, None, nodes, False, current_max_depth + 1, \
           used_input


def tree_derivation(Tree, ind_tree, genome, method, nodes, depth, max_depth, depth_limit):
    """ Derive a tree using a given method """

    nodes += 1
    depth += 1
    ind_tree.id, ind_tree.depth = nodes, depth

    productions = params['BNF_GRAMMAR'].rules[ind_tree.root]
    available = ind_tree.legal_productions(method, depth_limit, productions)
    chosen_prod = choice(available)

    prod_choice = productions.index(chosen_prod)
    codon = randrange(len(productions),
                             params['BNF_GRAMMAR'].codon_size,
                             len(productions)) + prod_choice
    ind_tree.codon = codon
    genome.append(codon)
    ind_tree.children = []

    for symbol in chosen_prod:
        if symbol[1] == params['BNF_GRAMMAR'].T:
            # if the right hand side is a terminal
            ind_tree.children.append(Tree.Tree((symbol[0],), ind_tree))
        elif symbol[1] == params['BNF_GRAMMAR'].NT:
            # if the right hand side is a non-terminal
            ind_tree.children.append(Tree.Tree((symbol[0],), ind_tree))
            genome, nodes, d, max_depth = tree_derivation(Tree, ind_tree.children[-1], genome, method, nodes, depth, max_depth,
                                                                           depth_limit - 1)

    NT_kids = [kid for kid in ind_tree.children if kid.root in
               params['BNF_GRAMMAR'].non_terminals]

    if not NT_kids:
        # Then the branch terminates here
        depth += 1
        nodes += 1

    if depth > max_depth:
        max_depth = depth

    return genome, nodes, depth, max_depth


def genome_tree_derivation(Tree, ind_tree, genome, index, depth, max_depth, nodes):
    """ Builds a tree using production choices from a given genome. Not
        guaranteed to terminate.
    """
    if index != "Incomplete" and index < len(genome) and max_depth <= params['MAX_TREE_DEPTH']:
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
            if symbol[1] == params['BNF_GRAMMAR'].T:
                ind_tree.children.append(Tree.Tree((symbol[0],), ind_tree))

            elif symbol[1] == params['BNF_GRAMMAR'].NT:
                ind_tree.children.append(Tree.Tree((symbol[0],), ind_tree))
                index, nodes, d, max_depth = genome_tree_derivation(Tree, ind_tree.children[-1], genome, index, depth, max_depth, nodes)
    else:
        # Mapping incomplete
        return "Incomplete", "Incomplete", "Incomplete", "Incomplete"

    NT_kids = [kid for kid in ind_tree.children if kid.root in params['BNF_GRAMMAR'].non_terminals]
    if not NT_kids:
        # Then the branch terminates here
        depth += 1
        nodes += 1

    if max_depth != "Incomplete" and (depth > max_depth):
        max_depth = depth
    return index, nodes, depth, max_depth
