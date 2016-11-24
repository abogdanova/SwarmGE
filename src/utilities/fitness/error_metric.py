import numpy as np
from sklearn.metrics.classification import f1_score


def mae(y, yhat):
    """Calculate mean absolute error between inputs."""
    return np.mean(np.abs(y - yhat))


def rmse(y, yhat):
    """Calculate root mean square error between inputs."""
    return np.sqrt(np.mean(np.square(y - yhat)))


def mse(y, yhat):
    """Calculate mean square error between inputs."""
    return np.mean(np.square(y - yhat))


def hinge(y, yhat):
    """Hinge loss is a suitable loss function for classification.  Here y is
    the true values (-1 and 1) and yhat is the "raw" output of the individual,
    ie a real value. The classifier will use sign(yhat) as its prediction."""
    return np.max(0, 1 - y * yhat)


# TODO should we depend on scikit-learn? it's an extra dependency, but anyone doing anything like this in Python should have it. We would use its utils, error metrics, etc
def inverse_f1_score(y, yhat):
    """The F_1 score is a metric for classification which tries to balance
    precision and recall, ie both true positives and true negatives.
    For F_1 score higher is better, so we take inverse."""

    # convert real values to boolean with a zero threshold
    yhat = (yhat > 0)
    f = f1_score(y, yhat)
    # this can give a runtime warning of zero division because if we
    # predict the same value for all samples (trivial individuals will
    # do so), f-score is undefined (see sklearn implementation) but
    # it's a warning, we can ignore.
    with np.errstate(divide='raise'):
        try:
            return 1.0 / f
        except:
            return 10000.0
