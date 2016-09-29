from algorithm.parameters import params
from algorithm import mapper
from copy import copy


def check_ind(ind):
    """Checks all aspects of an individual to ensure everything is correct."""

    g = copy(ind.genome)
    p = copy(ind.phenotype)
    d = copy(ind.depth)
    n = copy(ind.nodes)
    i = copy(ind.invalid)
    c = copy(ind.used_codons)

    if d > params['MAX_TREE_DEPTH']:
        print("Error: max tree depth exceeded")
        print("  ", d, "\t", params['MAX_TREE_DEPTH'])
        print(ind.tree)
        print(ind.phenotype)
        print(ind.invalid)
        print(ind.used_codons)
        print(ind.genome)
        check_mapping(ind.genome)
        quit()

    # Re-map individual using fast genome mapper to check everything is ok
    check_mapping(ind.genome)

    if not params['GENOME_OPERATIONS']:
        # Check components of tree are all correct
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


def check_mapping(genome):
    """
    Checks the mapping for a given genome to ensure everything matches up ok
    :param genome: the genome of an individual
    :return: nothing if everything goes ok
    """

    p1, g1, t1, n1, i1, d1, c1 = mapper.map_tree_from_genome(genome)
    p2, g2, t2, n2, i2, d2, c2 = mapper.map_ind_from_genome(genome)

    if not i1:
        if (i1 == i2):
            if p2 != p1:
                print("Error: phenotypes don't match")
                print("", p1, "\n", p2)
                print("", n1, "\n", n2)
                print("", d1, "\n", d2)
                print("", i1, "\n", i2)
                print(g1)
                quit()
            elif n2 != n1:
                print("Error: nodes don't match")
                print("", p1, "\n", p2)
                print("", n1, "\n", n2)
                print("", d1, "\n", d2)
                print("", i1, "\n", i2)
                print(g1)
                quit()
            elif d2 != d1:
                print("Error: tree depth doesn't match")
                print("", p1, "\n", p2)
                print("", n1, "\n", n2)
                print("", d1, "\n", d2)
                print("", i1, "\n", i2)
                print(g1)
                quit()
            elif c2 != c1:
                print("Error: used codons don't match")
                print("", p1, "\n", p2)
                print("", n1, "\n", n2)
                print("", d1, "\n", d2)
                print("", i1, "\n", i2)
                print(g1)
                quit()
            elif d2 > params['MAX_TREE_DEPTH']:
                print("Error: max tree depth limit exceeded")
                print("", p1, "\n", p2)
                print("", n1, "\n", n2)
                print("", d1, "\n", d2)
                print("", i1, "\n", i2)
                print(g1)
                quit()
        else:
            print("Error: invalid doesn't match")
            print("", p1, "\n", p2)
            print("", n1, "\n", n2)
            print("", d1, "\n", d2)
            print("", i1, "\n", i2)
            print(g1)
            quit()


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
        mapper.map_tree_from_genome(orig_gen)

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
