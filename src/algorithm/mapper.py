from operators.initialisation import generate_ind_tree
from algorithm.parameters import params
from representation.tree import Tree
from collections import deque
from random import randint


def mapper(genome, tree):
    """
    Wheel for mapping. Calls the correct mapper for a given input. Checks
    the params dict to ensure the correct type of individual is being created.

    If a genome is passed in with no tree, all tree-related information is
    generated. If a tree is passed in with no genome, the genome is
    sequenced from the tree. If neither is passed in, a new randomly
    generated individaul is generated.

    :param genome: Genome of an individual.
    :param tree: Tree of an individual.
    :return: All components necessary for a fully mapped individual.
    """

    phenotype, nodes, invalid, depth, used_codons = None, None, None, None, \
        None

    if genome:
        # We have a genome and need to map an individual from that genome.
        
        genome = list(genome)
        # This is a fast way of creating a new unique copy of the genome
        # (prevents cross-contamination of information between individuals).

        if not tree:
            # We have a genome but no tree. We need to map an individual
            # from the genome and generate all tree-related info.
            
            if params['GENOME_OPERATIONS']:
                # Can generate tree information faster using
                # algorithm.mapper.map_ind_from_genome() if we don't need to
                # store the whole tree.
                phenotype, genome, tree, nodes, invalid, depth, \
                    used_codons = map_ind_from_genome(genome)
            
            else:
                # Build the tree using algorithm.mapper.map_tree_from_genome().
                phenotype, genome, tree, nodes, invalid, depth, \
                    used_codons = map_tree_from_genome(genome)

    else:
        # We do not have a genome.

        if tree:
            # We have a tree but need to generate a genome from the
            # fully mapped tree.
            genome = tree.build_genome([])

            # Generate genome tail.
            used_codons = len(genome)
            genome = genome + [randint(0, params['CODON_SIZE']) for _ in
                               range(int(used_codons / 2))]

        else:
            # We have neither a genome nor a tree. We need to generate a new
            # random individual.

            if params['GENOME_INIT']:
                # We need to initialise a new individual from a randomly
                # generated genome.

                # Generate a random genome
                genome = [randint(0, params['CODON_SIZE']) for _ in
                          range(params['GENOME_LENGTH'])]

                if params['GENOME_OPERATIONS']:
                    # Initialise a new individual from a randomly generated
                    # genome without generating a tree. Faster.
                                        
                    # Map the genome to all parameters needed for an
                    # individual.
                    phenotype, genome, tree, nodes, invalid, \
                        depth, used_codons = map_ind_from_genome(list(genome))

                else:
                    # Initialise a new individual from a randomly generated
                    # genome by mapping using the tree class.
                    
                    # Map the genome to all parameters needed for an
                    # individual.
                    phenotype, genome, tree, nodes, invalid, \
                        depth, used_codons = map_tree_from_genome(list(genome))

            else:
                # We need to initialise a new individual from a randomly
                # generated tree.
                ind = generate_ind_tree(params['MAX_TREE_DEPTH'], "random")

                # Extract all parameters needed for an individual.
                phenotype, genome, tree, nodes, invalid, depth, \
                    used_codons = ind.phenotype, ind.genome, ind.tree, \
                    ind.nodes, ind.invalid, ind.depth, ind.used_codons

    if not phenotype and not invalid:
        # If we have no phenotype we need to ensure that the solution is not
        # invalid, as invalid solutions have a "None" phenotype.
        phenotype = tree.get_output()

    if not used_codons:
        # The number of used codons is the length of the genome.
        used_codons = len(genome)

    if invalid == None:
        # Need to ensure that invalid is None and not False. Can't say "if
        # not invalid" as that will catch when invalid is False.
        invalid = tree.check_expansion()

    if not depth and not nodes:
        # Need to get the depth of the tree and and its number of nodes.
        depth, nodes = tree.get_tree_info(tree)
        depth += 1

    return phenotype, genome, tree, nodes, invalid, depth, used_codons


def map_ind_from_genome(genome):
    """
    The genotype to phenotype mapping process. Map input via rules to
    output. Returns output and used_input.
    
    :param genome:
    :param max_wraps:
    :return:
    """

    from utilities.helper_methods import python_filter
    
    # Create local variables to avoide multiple dictionary lookups
    MAX_TREE_DEPTH, max_wraps = params['MAX_TREE_DEPTH'], params['MAX_WRAPS']
    NT_SYMBOL, BNF_GRAMMAR = params['BNF_GRAMMAR'].NT, params['BNF_GRAMMAR']

    n_input = len(genome)

    # Depth, max_depth, and nodes start from 1 to account for starting root
    # Initialise number of wraps at -1 (since
    used_input, current_depth, max_depth, nodes, wraps = 0, 1, 1, 1, -1
    
    output = deque()
    
    # Initialise the list of unexpanded non-terminals with the start rule.
    unexpanded_symbols = deque([(BNF_GRAMMAR.start_rule, 1)])
    
    while (wraps < max_wraps) and \
            (unexpanded_symbols) and \
            (max_depth <= MAX_TREE_DEPTH):
        # Wrap
        if used_input % n_input == 0 and \
                        used_input > 0 and \
                any([i[0][1] == NT_SYMBOL for i in unexpanded_symbols]):
            wraps += 1

        # Expand a production
        current_item = unexpanded_symbols.popleft()
        current_symbol, current_depth = current_item[0], current_item[1]
        if max_depth < current_depth:
            max_depth = current_depth

        # Set output if it is a terminal
        if current_symbol[1] != NT_SYMBOL:
            output.append(current_symbol[0])
        else:
            production_choices = BNF_GRAMMAR.rules[current_symbol[0]]
            # Select a production
            # TODO store the length of production choices to avoid len call?
            current_production = genome[used_input % n_input] % \
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

    # Generate phenotype string.
    output = "".join(output)

    if len(unexpanded_symbols) > 0:
        # All non-terminals have not been completely expanded, invalid
        # solution.
        
        return None, genome, None, nodes, True, max_depth, used_input

    if BNF_GRAMMAR.python_mode:
        # Grammar contains python code

        output = python_filter(output)

    return output, genome, None, nodes, False, max_depth, used_input


def map_tree_from_genome(genome):
    """
    Maps a full tree from a given genome.
    
    :param genome: A genome to be mapped.
    :return: All components necessary for a fully mapped individual.
    """

    # Initialise an instance of the tree class
    tree = Tree((str(params['BNF_GRAMMAR'].start_rule[0]),),
                None, depth_limit=params['MAX_TREE_DEPTH'])
    
    # Map tree from the given genome
    used_codons, nodes, depth, max_depth, invalid = \
        genome_tree_derivation(tree, genome, 0, 0, 0, 0)
    
    if invalid:
        # Return "None" phenotype if invalid
        return None, genome, tree, nodes, invalid, max_depth, \
           used_codons
    else:
        # Build phenotype and return
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
