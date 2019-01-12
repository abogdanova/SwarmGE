import numpy as np

import helper


class pso(helper.sw):
    """
    Particle Swarm Optimization
    """

    def __init__(self, n, function, lb, ub, dimension, iteration, w=0.5, c1=1,
                 c2=1):
        """
        :param n: number of agents
        :param function: test function
        :param lb: lower limits for plot axes
        :param ub: upper limits for plot azes
        :param dimension: space dimension
        :param iteration: the number of iterations
        :param w: balance between the range of research and consideration for
        suboptimal decisions found (default value is 0.5):
        w>1 the particle velocity increases, they fly apart and inspect
         the space more carefully;
        w<1 particle velocity decreases, convergence speed depends
        on parameters c1 and c2 ;
        :param c1: ratio between "cognitive" and "social" component
        (default value is 1)
        :param c2: ratio between "cognitive" and "social" component
        (default value is 1)
        """

        super(pso, self).__init__()

        self._agents = np.random.uniform(lb, ub, (n, dimension))
        velocity = np.zeros((n, dimension))
        self._points(self._agents)

        Pbest = self._agents[np.array([function(x)
                                        for x in self._agents]).argmin()]
        Gbest = Pbest

        for t in range(iteration):

            # r1 = np.random.random((n, dimension))
            # r2 = np.random.random((n, dimension))
            # velocity = w * velocity + c1 * r1 * (
            #     Pbest - self._agents) + c2 * r2 * (
            #     Gbest - self._agents)
            self._velocity(Pbest, Gbest, n, dimension, velocity)
            self._agents = np.clip(self._agents, lb, ub)
            self._points(self._agents)

            Pbest = self._agents[
                np.array([function(x) for x in self._agents]).argmin()]
            if function(Pbest) < function(Gbest):
                Gbest = Pbest

        self._set_Gbest(Gbest)
