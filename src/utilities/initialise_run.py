from stats.stats import generate_folders_and_files
from algorithm.parameters import params
from utilities import trackers
from datetime import datetime
from sys import version_info
import time


def check_python_version():
    """
    Check the python version to ensure it is correct. PonyGE uses Python 3.
    
    :return: Nothing
    """

    if version_info.major < 3:
        print("\nError: Python version not supported. Must use Python 3.x")
        quit()


def initialise_run_params():
    """
    Initialises all lists and trackers. Generates save folders and initial
    parameter files if debugging is not active.
    
    :return: Nothing
    """

    time1 = datetime.now()
    trackers.time_list.append(time.clock())
    
    # Generate a time stamp for use with folder and file names.
    hms = "%02d%02d%02d" % (time1.hour, time1.minute, time1.second)
    params['TIME_STAMP'] = (str(time1.year)[2:] + "_" + str(time1.month) +
                            "_" + str(time1.day) + "_" + hms +
                            "_" + str(time1.microsecond))
    if not params['SILENT']:
        print("\nStart:\t", time1, "\n")

    # Generate save folders and files
    if params['DEBUG']:
        print("Seed:\t", params['RANDOM_SEED'], "\n")
    else:
        generate_folders_and_files()


def make_import_str(fns):
    """
    Takes in a paired list of operators and the specified function from the
    option parser. Strings either represent the full dotted path to the
    function which we wish to access, eg operators.selection.tournament, or
    just the function name directly (in which case we default to the specified
    functions in the default location for each operators).
    
    :param fns: a paired list of operators and the specified function from the
    option parser. Strings either represent the full dotted path to the
    function which we wish to access, eg operators.selection.tournament, or
    just the function name directly (in which case we default to the specified
    functions in the default location for each operators).
    :return: a string of imports of correct modules,
    eg import operators.selection
    """

    imports = []
    for fn in fns:
        # Extract pairs of operators and functions
        operator, function = fn[0], fn[1]
        parts = function.split(".")
        # Split the function into its component parts
        if len(parts) == 1:
            # If the specified location is a single name, default to
            # operators.operator location
            imports.append("import operators." + operator.lower())
            params[operator] = "operators." + operator.lower() + "." + parts[0]
        else:
            # "operators.selection.tournament" -> "import operators.selection"
            imports.append("import " + ".".join(parts[:-1]))
    return "\n".join(imports)


def set_param_imports():
    """
    This function makes the command line experience easier for users. When
    specifying operators listed in the special_ops list below, users do not
    need to specify the full file path to the functions themselves. Users
    can simply specify a single word, e.g.
        
        "--mutation subtree"
    
    Using the special_ops dictionary, this will default to
    "operators.mutation.subtree. Executes the correct imports for specified
    modules and then saves the correct parameters in the params dictionary.
    Users can still specify the full direct path to the operators if they so
    desire, allowing them to create new operators and save them wherever
    they like.
    
    :return: Nothing.
    """
    
    # For these ops we let the param equal the function itself.
    special_ops = ['INITIALISATION', 'SELECTION', 'CROSSOVER', 'MUTATION',
                   'REPLACEMENT']
    if all([callable(params[op]) for op in special_ops]):
        # params are already functions
        pass
    else:
        # We need to do an appropriate import...
        import_str = make_import_str([[op, params[op]] for op in special_ops])
        exec(import_str)
        # ... and then eval the param.
        for op in special_ops:
            params[op] = eval(params[op])
