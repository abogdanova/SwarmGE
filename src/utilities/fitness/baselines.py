#!/usr/bin/env python
import sys

import numpy as np
from sklearn.linear_model import LinearRegression, ElasticNet

from utilities.fitness.error_metric import rmse
from utilities.fitness.get_data import get_Xy_train_test, get_Xy_train_test_separate


def fit_const(train_X, train_y, test_X, test_y):
    """Use the mean of the y training values as a predictor."""
    mn = np.mean(train_y)
    # print("Predicting constant", mn)
    yhat = np.ones(len(train_y)) * mn
    # print("Train error =", error(train_y, yhat))
    yhat = np.ones(len(test_y)) * mn
    # print("Test error =", error(test_y, yhat))


def fit_lr(train_X, train_y, test_X, test_y):
    """Use linear regression to predict."""
    lr = LinearRegression()
    lr.fit(train_X, train_y)
    # print("LR predicting intercept", lr.intercept_, "and coefs", lr.coef_)
    yhat = lr.predict(train_X)
    # print("Train error =", error(train_y, yhat))
    yhat = lr.predict(test_X)
    # print("Test error =", error(test_y, yhat))


def fit_enet(train_X, train_y, test_X, test_y):
    """Use linear regression to predict -- elastic net is LR with L1
    and L2 regularisation."""
    enet = ElasticNet()
    enet.fit(train_X, train_y)
    # print("ElasticNet predicting intercept", enet.intercept_, "and coefs",
    #       enet.coef_)
    yhat = enet.predict(train_X)
    # print("Train error =", error(train_y, yhat))
    yhat = enet.predict(test_X)
    # print("Test error =", error(test_y, yhat))

if __name__ == "__main__":
    error = rmse
    # error = mae

    if len(sys.argv) == 3:
        train_filename = sys.argv[1]
        test_filename = sys.argv[2]
        train_X, train_y, test_X, test_y = \
            get_Xy_train_test_separate(train_filename, test_filename)
    else:
        filename = sys.argv[1]
        train_X, train_y, test_X, test_y = get_Xy_train_test(filename)
    fit_const(train_X, train_y, test_X, test_y)
    fit_lr(train_X, train_y, test_X, test_y)
    fit_enet(train_X, train_y, test_X, test_y)
