from algorithm.parameters import params
from representation.tree import Tree

def pi_random_init(depth):

    tree = Tree(str(params['BNF_GRAMMAR'].start_rule[0]),
                None, max_depth=depth, depth_limit=depth)
    genome = tree.pi_random_derivation(0, max_depth=depth)
    if tree.check_expansion(params['BNF_GRAMMAR'].non_terminals.keys()):
        print("tree.pi_random_init generated an Invalid")
        quit()
    return tree.get_output(), genome, tree, False


def pi_grow_init(depth):

    tree = Tree(str(params['BNF_GRAMMAR'].start_rule[0]), None,
                max_depth=depth, depth_limit=depth)
    genome = tree.pi_grow(0, max_depth=depth)
    if tree.check_expansion(params['BNF_GRAMMAR'].non_terminals.keys()):
        print("tree.pi_grow_init generated an Invalid")
        quit()
    return tree.get_output(), genome, tree, False
