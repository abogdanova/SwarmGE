def mae(y, yhat):
    """Calculate mean absolute error between inputs."""
    return np.mean(np.abs(y - yhat))

def rmse(y, yhat):
    """Calculate root mean square error between inputs."""
    return np.sqrt(np.mean(np.square(y - yhat)))

def mse(y, yhat):
    """Calculate mean square error between inputs."""
    return np.mean(np.square(y - yhat))

