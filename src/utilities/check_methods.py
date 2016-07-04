from operators.initialisers import genome_init
from algorithm.parameters import params
from copy import copy


def check_ind(ind):
    """Checks all aspects of an individual to ensure everything is correct."""

    g = copy(ind.genome)
    p = copy(ind.phenotype)
    d = copy(ind.depth)
    n = copy(ind.nodes)
    i = copy(ind.invalid)
    c = copy(ind.used_codons)

    depth, nodes = ind.tree.get_tree_info(ind.tree)

    if p != ind.tree.get_output():
        print("\nError: Phenotype doesn't match tree output\n")
        print(p, "\n", ind.tree.get_output())
        quit()
    elif g[:c] != ind.tree.build_genome([]):
        print("\nError: Genome doesn't match tree output\n")
        print(g[:c], "\n", ind.tree.build_genome([]))
        quit()
    elif d != depth + 1:
        print("\nError: Depth doesn't match tree depth\n")
        print(d, "\n", depth)
        quit()
    elif n != nodes:
        print("\nError: Nodes doesn't match tree nodes\n")
        print(n, "\n", nodes)
        quit()
    elif i != ind.tree.check_expansion():
        print("\nError: Invalid doesn't match tree invalid\n")
        quit()

    verify_tree(ind.tree)


def verify_tree(ind_tree):
    """ Checks the entire tree for discrepancies """

    check_genome_from_tree(ind_tree)

    if ind_tree.check_expansion():
        print("Invalid given tree")
        quit()

    def check_nodes(ind_tree, n=0):
        n += 1

        if ind_tree.id != n:
            print("Node ids do not match node numbers")
            print(ind_tree.id, n)
            quit()

        if ind_tree.root in params['BNF_GRAMMAR'].non_terminals:
            NT_kids = [kid for kid in ind_tree.children if kid.root in
                       params['BNF_GRAMMAR'].non_terminals]
            if not NT_kids:
                n += 1
            else:
                for child in NT_kids:
                    n = check_nodes(child, n)
        return n

    check_nodes(ind_tree)

    orig_out = copy(ind_tree.get_output())
    orig_gen = copy(ind_tree.build_genome([]))

    output, genome, ind_tree, nodes, invalid, depth, used_codons = \
        genome_init(orig_gen)

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


def check_genome_from_tree(ind_tree):
    """ Goes through a tree and checks each codon to ensure production
        choice is correct """

    if ind_tree.codon:
        productions = params['BNF_GRAMMAR'].rules[ind_tree.root]
        selection = ind_tree.codon % len(productions)
        chosen_prod = productions[selection]
        prods = [prod[0] for prod in chosen_prod]
        roots = []
        for kid in ind_tree.children:
            roots.append(kid.root)
        if roots != prods:
            print("\nGenome is incorrect")
            print("Codon productions:\t", prods)
            print("Actual children:  \t", roots)
            quit()
    for kid in ind_tree.children:
        check_genome_from_tree(kid)
