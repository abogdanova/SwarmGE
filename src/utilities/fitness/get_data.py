from os import listdir, getcwd, path

import numpy as np


def get_Xy_train_test(filename, randomise=True, test_proportion=0.5,
                      skip_header=0):
    """
    Read in a table of numbers and split it into X (all columns up
    to last) and y (last column), then split it into training and
    testing subsets according to test_proportion. Shuffle if
    required.
    
    :param filename: The file name of the dataset.
    :param randomise: Boolean argument for randomising the train/test split.
    :param test_proportion: The proportion of the dataset to be reserved for
    test data.
    :param skip_header: The number of header lines to skip.
    :return: Parsed numpy arrays of training and testing input (x) and
    output (y) data.
    """

    # Read in all data.
    Xy = np.genfromtxt(filename, skip_header=skip_header)
    
    if randomise:
        # Randomise the data so the train and test splits will be different
        # each time the data is read in.
        np.random.shuffle(Xy)

    # Separate out input (X) and output (y) data.
    X = Xy[:, :-1]  # all columns but last
    y = Xy[:, -1]  # last column
    
    # Pick a split point to split the total data for training and testing data.
    idx = int((1.0 - test_proportion) * len(y))
    
    # Split data into separate train and test datasets.
    train_X, train_y = X[:idx], y[:idx]
    test_X, test_y = X[idx:], y[idx:]
    
    return train_X, train_y, test_X, test_y


def get_Xy_train_test_separate(train_filename, test_filename, skip_header=0):
    """
    Read in training and testing data files, and split each into X
    (all columns up to last) and y (last column).
    
    :param train_filename: The file name of the training dataset.
    :param test_filename: The file name of the testing dataset.
    :param skip_header: The number of header lines to skip.
    :return: Parsed numpy arrays of training and testing input (x) and
    output (y) data.
    """

    # first try to auto-detect the field separator (i.e. delimiter).
    f = open(train_filename)
    for line in f:
        if line.startswith("#") or len(line) < 2:
            # Skip excessively short lines or commented out lines.
            continue
            
        else:
            # Set the delimiter.
            if "," in line:
                delimiter = ","; break
            elif "\t" in line:
                delimiter = "\t"; break
            elif ";" in line:
                delimiter = ";"; break
            elif ":" in line:
                delimiter = ":"; break
            else:
                delimiter = " "; break
    f.close()
    
    # Read in all training data.
    train_Xy = np.genfromtxt(train_filename, skip_header=skip_header,
                             delimiter=delimiter)
    # Read in all testing data.
    test_Xy = np.genfromtxt(test_filename, skip_header=skip_header,
                            delimiter=delimiter)
    
    # Separate out input (X) and output (y) data.
    train_X = train_Xy[:, :-1].transpose()  # all columns but last
    train_y = train_Xy[:, -1].transpose()  # last column
    test_X = test_Xy[:, :-1].transpose()  # all columns but last
    test_y = test_Xy[:, -1].transpose()  # last column

    return train_X, train_y, test_X, test_y


def get_data(experiment, file_type="txt"):
    """
    Return the training and test data for the current experiment.
    
    :param experiment: The name of the desired datasets.
    :param file_type: The file extension of the desired dataset.
    :return: The parsed data contained in the dataset files.
    """

    # Get the path to the datasets folder and list all datasets.
    datasets = listdir(path.join(getcwd(), "..", "datasets"))
    
    for dataset in datasets:
        # Find the names of the datasets
        exp = dataset.split('.')[0].split('-')[0]
        
        if exp == experiment:
            # We have found our desired dataset.
            
            # Get the file type.
            file_type = dataset.split('.')[1]
    
    # Get the path to the training dataset.
    train_set = path.join("..", "datasets",
                          (experiment + "-Train." + str(file_type)))
    
    # Get the path to the testing dataset.
    test_set = path.join("..", "datasets",
                         (experiment + "-Test." + str(file_type)))
    
    # Read in the training and testing datasets from the specified files.
    training_in, training_out, test_in, \
    test_out = get_Xy_train_test_separate(train_set, test_set, skip_header=1)
    
    return training_in, training_out, test_in, test_out
