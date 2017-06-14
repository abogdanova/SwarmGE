from datetime import datetime
from os import getpid
from random import seed
from socket import gethostname
from time import time
import importlib

from algorithm.parameters import params
from utilities.stats import trackers
from utilities.stats.file_io import generate_folders_and_files


def initialise_run_params(create_files):
    """
    Initialises all lists and trackers. Generates save folders and initial
    parameter files if debugging is not active.

    :return: Nothing
    """

    start = datetime.now()
    trackers.time_list.append(time())

    # Set random seed
    if params['RANDOM_SEED'] is None:
        params['RANDOM_SEED'] = int(start.microsecond)
    seed(params['RANDOM_SEED'])

    # Generate a time stamp for use with folder and file names.
    hms = "%02d%02d%02d" % (start.hour, start.minute, start.second)
    params['TIME_STAMP'] = "_".join([gethostname(),
                                     str(params['RANDOM_SEED']),
                                     str(getpid()),
                                     str(start.year)[2:],
                                     str(start.month),
                                     str(start.day),
                                     hms,
                                     str(start.microsecond)])
    if not params['SILENT']:
        print("\nStart:\t", start, "\n")

    # Generate save folders and files
    if params['DEBUG']:
        print("Seed:\t", params['RANDOM_SEED'], "\n")
    elif create_files:
        generate_folders_and_files()


def set_param_imports():
    """
    This function makes the command line experience easier for users. When
    specifying operators listed in the lists below, users do not need to
    specify the full file path to the functions themselves. Users can simply
    specify a single word, e.g.

        "--mutation subtree"

    Using the special_ops dictionary for example, this will default to
    "operators.mutation.subtree. Executes the correct imports for specified
    modules and then saves the correct parameters in the params dictionary.
    Users can still specify the full direct path to the operators if they so
    desire, allowing them to create new operators and save them wherever
    they like.

    Sets the fitness function for a problem automatically. Fitness functions
    are stored in fitness. Fitness functions must be classes, where the
    class name matches the file name.

    Function is set up to automatically set imports for operators and error
    metrics.

    :return: Nothing.
    """

    # For these ops we let the param equal the function itself.
    ops = {'operators': ['INITIALISATION', 'SELECTION', 'CROSSOVER',
                         'MUTATION', 'REPLACEMENT'],
           'utilities.fitness': ['ERROR_METRIC'],
           'fitness': ['FITNESS_FUNCTION'],
           'algorithm': ['SEARCH_LOOP', 'STEP']}

    # We have to take 'algorithm' first as the functions from
    # algorithm need to be imported before any others to prevent
    # circular imports. We have to take 'utilities.fitness' before
    # 'fitness' because ERROR_METRIC has to be set in order to call
    # the fitness function constructor.

    for special_ops in ['algorithm', 'utilities.fitness',
                        'operators', 'fitness']:

        if all([callable(params[op]) for op in ops[special_ops]]):
            # params are already functions
            pass

        else:
            
            for op in ops[special_ops]:
                
                # Split import name based on "." to find nested modules.
                split_name = params[op].split(".")
                
                if split_name[0] == special_ops:
                    # Full path already specified.
                    
                    # Get module and attribute names.
                    module_name = ".".join(split_name[:-1])
                    attr_name = split_name[-1]

                    # Import module and attribute.
                    import_attr_from_module(module_name, attr_name, op)
                    
                elif special_ops == 'fitness':
                    # Fitness functions must be classes where the class has
                    # the same name as its containing file.
            
                    # Get module and attribute names.
                    module_name = ".".join([special_ops, params[op]])
                    attr_name = split_name[-1]

                    # Import module and attribute.
                    import_attr_from_module(module_name, attr_name, op)
                    
                    # Initialise fitness function.
                    params[op] = params[op]()

                else:
                    # Full path not specified
    
                    # Get module and attribute names.
                    module_name = ".".join([special_ops, op.lower()])
                    attr_name = split_name[-1]
    
                    # Import module and attribute.
                    import_attr_from_module(module_name, attr_name, op)
            

def import_attr_from_module(module_name, attr_name, op):
    """
    Given a module path and the name of an attribute that exists in that
    module, import the attribute from the module using the importlib package
    and store it in the params dictionary.
    
    :param module_name: The name/location of the desired module.
    :param attr_name: The name of the attribute.
    :param op: The relevant key from the parameters.parameters.params
               dictionary.
    :return: Nothing.
    """
    
    try:
        # Import module.
        module = importlib.import_module(module_name)
    
    except ModuleNotFoundError:
        s = "utilities.initialise_run.import_attr_from_module\n" \
            "Error: Specified module not found: %s" % (module_name)
        raise Exception(s)
    
    try:
        # Import specified attribute.
        params[op] = getattr(module, attr_name)
        
    except AttributeError:
        s = "utilities.initialise_run.import_attr_from_module\n" \
            "Error: Specified attribute '%s' not found in module '%s'." \
            % (attr_name, module_name)
        raise Exception(s)
