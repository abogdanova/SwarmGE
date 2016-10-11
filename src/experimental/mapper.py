from random import randint, choice, randrange

from algorithm.parameters import params
from representation.tree import Tree


def pi_random_derivation(tree, index, max_depth=20):
    """ Randomly builds a tree from a given root node up to a maximum
        given depth. Uses position independent stuff.
    """

    queue = [[tree,
              params['BNF_GRAMMAR'].non_terminals[tree.root]['recursive']]]

    while queue:
        num = len(queue)
        chosen = randint(0, num-1)
        all_node = queue.pop(chosen)
        node = all_node[0]

        n, depth = tree.get_tree_info(tree)
        depth += 1

        if depth < max_depth:
            productions = params['BNF_GRAMMAR'].rules[node.root]
            available = []
            remaining_depth = max_depth - depth

            if remaining_depth > params['BNF_GRAMMAR'].max_arity:
                available = productions
            else:
                for prod in productions:
                    depth = 0
                    for item in prod:
                        if (item[1] == params['BNF_GRAMMAR'].NT) and \
                                (item[2] > depth):
                            depth = item[2]
                    if depth < remaining_depth:
                        available.append(prod)
            chosen_prod = choice(available)
            if len(productions) > 1:
                prod_choice = productions.index(chosen_prod)
                codon = randrange(0, params['BNF_GRAMMAR'].codon_size,
                                  len(productions)) + prod_choice
                node.codon = codon
                node.id = index
                index += 1
            node.children = []

            for i in range(len(chosen_prod)):
                symbol = chosen_prod[i]
                child = Tree(symbol[0], node)
                node.children.append(child)
                if symbol[1] == params['BNF_GRAMMAR'].NT:
                    # if the right hand side is a non-terminal
                    queue.insert(chosen+i,
                                 [child,
                                  params['BNF_GRAMMAR'].non_terminals
                                  [child.root]['recursive']])
    genome = tree.build_genome([])
    return genome


def pi_grow(tree, index, max_depth=20):
    """ Grows a tree until a single branch reaches a specified depth. Does
        this by only using recursive production choices until a single
        branch of the tree has reached the specified maximum depth. After
        that any choices are allowed
    """

    queue = [[tree, params['BNF_GRAMMAR'].non_terminals[tree.root]['recursive']]]

    while queue:
        num = len(queue)
        chosen = randint(0, num-1)
        all_node = queue.pop(chosen)
        node = all_node[0]
        n, depth = tree.get_tree_info(tree)
        depth += 1

        if depth < max_depth:
            productions = params['BNF_GRAMMAR'].rules[node.root]
            available = []
            remaining_depth = max_depth - depth

            if (tree.get_max_tree_depth(tree) < max_depth - 1) or \
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
                            if not all(sym[3] for sym in production):
                                available.append(production)
                else:
                    for prod in productions:
                        depth = 0
                        for item in prod:
                            if (item[1] == params['BNF_GRAMMAR'].NT) and \
                                    (item[2] > depth):
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
                            if (item[1] == params['BNF_GRAMMAR'].NT) and \
                                    (item[2] > depth):
                                depth = item[2]
                        if depth < remaining_depth:
                            available.append(prod)
            chosen_prod = choice(available)
            if len(productions) > 1:
                prod_choice = productions.index(chosen_prod)
                codon = randrange(0, params['BNF_GRAMMAR'].codon_size,
                                  len(productions)) + prod_choice
                node.codon = codon
                node.id = index
                index += 1
            node.children = []

            for i in range(len(chosen_prod)):
                symbol = chosen_prod[i]
                child = Tree(symbol[0], node)
                node.children.append(child)
                if symbol[1] == params['BNF_GRAMMAR'].NT:
                    # if the right hand side is a non-terminal
                    queue.insert(chosen+i, [child, params['BNF_GRAMMAR'].non_terminals[child.root]['recursive']])
    genome = tree.build_genome([])
    return genome
