from algorithm.parameters import params
from utilities.representation.check_methods import output_with_nodes, \
    set_phenotypic_output_lr, set_phenotypic_output_rl
from utilities.stats import trackers
from fitness.default_fitness import default_fitness


class regex_string_match:
    """Fitness function for matching a string. Takes a string and returns
    fitness. Penalises output that is not the same length as the target."""

    maximise = False

    def __init__(self):
        # Set target string.
        self.target = params['TARGET']

    def __call__(self, ind):
        guess = ind.phenotype
        
        fitness = float(max(len(self.target), len(guess)))
        
        # Loops as long as the shorter of two strings.
        for (t_p, g_p) in zip(self.target, guess):
            if t_p == g_p:
                fitness -= 1
            else:
                fitness -= 1 / (1 + (abs(ord(t_p) - ord(g_p))))

        if len(guess) <= 2*len(self.target) and params['SEMANTIC_LOCK']:
            
            # Set phenotypic output for all nodes in the tree.
            set_phenotypic_output_lr(ind.tree, ind.phenotype, 0)
            set_phenotypic_output_rl(ind.tree, ind.phenotype, 0)

            # Recurse through the tree to find snippets that match the target.
            # Add to the snippets library if we find any.
            self.check_snippets(ind.tree)

            # Lock portions of the derivation tree to prevent mutation. The
            # idea is to focus remaining search on the areas that don't match
            # the target string.
            self.set_semantic_lock(ind)
        
        else:
            fitness = default_fitness(self.maximise)

        return fitness

    def set_semantic_lock(self, ind):
        """
        Get the semantic performance of all nodes in an individual's tree.
        Check all terminal nodes to see if they exactly match the
        corresponding location in the target string. If so, then lock the
        parent node of that terminal (but only if the parent has one child)
        so that it cannot be mutated again.
        
        :param ind: An individual.
        :return: Nothing.
        """
        
        # Get phenotypic output of all terminal nodes.
        output = output_with_nodes(ind.tree)

        # Read string forwards from the start.
        index = 0

        for out in output:

            symbols = out[0]
            len_s = len(symbols)
            
            # Get corresponding portion of target string.
            target_portion = self.target[index:index + len_s]
            # Check for match
            if target_portion == symbols:
                # We have a match, turn semantic lock on to prevent mutation
                # on this node.
                
                if len(out[1].children) == 1:
                    # Parent node leads directly to single terminal. Lock
                    # both down.
                    out[1].semantic_lock = True
                    out[1].children[0].semantic_lock = True

                else:
                    # Parent node has multiple children. Only lock down this
                    # child.
                    roots = [kid.root for kid in out[1].children]

                    # Find which child is the current symbol.
                    child = roots.index(target_portion)
                    
                    # Lock that shit down.
                    out[1].children[child].semantic_lock = True

            index += len_s

        # Read string backwards from the end.
        index = 0

        for out in reversed(output):

            symbols = out[0]
            len_s = len(symbols)

            # Get corresponding portion of target string.
            if not index:
                target_portion = self.target[- len_s:]
            else:
                target_portion = self.target[index - len_s:index]

            # Check for match
            if target_portion == symbols:
                # Check for match
                
                if len(out[1].children) == 1:
                    # Parent node leads directly to single terminal. Lock
                    # both down.
                    out[1].semantic_lock = True
                    out[1].children[0].semantic_lock = True
                        
                else:
                    # Parent node has multiple children. Only lock down this
                    # child.
                    roots = [kid.root for kid in out[1].children]
        
                    # Find which child is the current symbol.
                    child = roots.index(target_portion)
        
                    # Lock that shit down.
                    out[1].children[child].semantic_lock = True

            index -= len_s

        # Get list of all terminal nodes in the tree.
        output = output_with_nodes(ind.tree, lock=False)

        # Lock portions of the tree if all children of a node are locked.
        for out in output:
            tree = out[1]
            
            if tree.semantic_lock:
                
                # Check if node can be locked.
                if all([child.semantic_lock for child in tree.children]):
                    tree.semantic_lock = True
                    
                # Set new parent
                parent = tree.parent
                
                while parent is not None:
                    # Recurse back up the tree and set semantic lock as we go
                    # (as long as all children are also locked)
                    
                    if parent is None:
                        # Reached the root node of the entire tree.
                        break

                    # Check if parent can be locked.
                    if all([child.semantic_lock for child in parent.children]):
                        parent.semantic_lock = True

                    # Set new parent
                    parent = parent.parent

        # print(len(trackers.snippets))
        #
        # print("\n- - - - - - - - - - - - - - -\n")
        #
        # for snippet in trackers.snippets:
        #     print(snippet, get_output(trackers.snippets[snippet]))
        #
        # quit()

    def check_snippets(self, tree):
        """
        Check all nodes in a derivation tree to see if there are any
        portions which match portions of the target string. Matching
        portions do not need to line up. Generates snippets for the correct
        set of matching target locations.
        
        :param tree: A tree to be checked for snippets.
        :return: Nothing.
        """
        
        output, root = tree.output, tree.root
        
        # Find the indexes of matches of the current output on the target.
        # Read string from left to right
        LR_keys = [" ".join([str([n, n + len(output)]), "LR", root])
                   for n in range(len(self.target)) if
                   self.target.find(output, n) == n and tree.children]

        # Read string from right to left
        RL_keys = [" ".join([str([-(n + len(output)), -n]), "RL", root])
                   for n in range(len(self.target)) if
                   self.target[::-1].find(output[::-1], n) == n and
                   tree.children]
        
        keys = LR_keys + RL_keys
        
        for key in keys:
            # Add snippet to repository.
            if key not in trackers.snippets:
                trackers.snippets[key] = tree.__copy__()
        
        if tree.children:
            # If the current node is not a terminal, recurse.
            for child in tree.children:
                self.check_snippets(child)
