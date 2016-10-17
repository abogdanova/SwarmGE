from math import isnan
from sys import maxsize

import numpy as np

from algorithm.parameters import params
from utilities.fitness.error_metric import mse
from utilities.fitness.get_data import get_data


class regression:
    """Fitness function for supervised learning, ie regression and
    classification problems. Given a set of training or test data,
    returns the error between y (true labels) and yhat (estimated
    labels). changing stuff. asdf

    We can pass in the error metric to be used. MSE is suitable for
    regression, while F1-score, hinge-loss and others are suitable for
    classification."""

    maximise = False

    def __init__(self):
        self.training_in, self.training_exp, self.test_in, self.test_exp = \
            get_data(params['DATASET'])
        self.n_vars = np.shape(self.test_in)[1]
        if params['ERROR_METRIC'] is None:
            params['ERROR_METRIC'] = mse
        self.training_test = True

    def __call__(self, func, dist="training"):
        """
        We can call regression objects,
        ie r = regression(exp); r(f, "training").

        :param func:
        :param dist: An optional parameter for problems with training/test
        data. Specifies the distribution (i.e. training or test) upon which
        evaluation is to be performed.
        :return:
        """

        if dist == "test":
            x = self.test_in
            y = self.test_exp
        elif dist == "training":
            x = self.training_in
            y = self.training_exp

        try:
            yhat = eval(func)  # func will refer to "x", created above

            # if func is a constant, eg 0.001 (doesn't refer to x),
            # then yhat will be a constant. that can confuse the error
            # metric.  so convert to a constant array.
            if not isinstance(yhat, np.ndarray):
                yhat = np.ones_like(y) * yhat

            # let's always call the error function with the true values first,
            # the estimate second
            fitness = params['ERROR_METRIC'](y, yhat)
        
        except:
            fitness = maxsize

        # don't use "not fitness" here, because what if fitness = 0.0?!
        if isnan(fitness):
            fitness = maxsize

        return fitness
