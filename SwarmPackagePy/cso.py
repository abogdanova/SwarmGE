from math import gamma, pi, sin
import numpy as np
from random import normalvariate, randint, random

import helper


class cso(helper.sw):
    """
    Cuckoo Search Optimization
    """

    def __init__(self, n, function, lb, ub, dimension, iteration, pa=0.25,
                 nest=100):
        """
        :param n: number of agents
        :param function: test function
        :param lb: lower limits for plot axes
        :param ub: upper limits for plot axes
        :param dimension: space dimension
        :param iteration: number of iterations
        :param pa: probability of cuckoo's egg detection (default value is 0.25)
        :param nest: number of nests (default value is 100)
        """

        super(cso, self).__init__()

        self._Nests = []

        # beta = 3 / 2
        # sigma = (gamma(1 + beta) * sin(pi * beta / 2) / (
        #     gamma((1 + beta) / 2) * beta *
        #     2 ** ((beta - 1) / 2))) ** (1 / beta)
        # u = np.array([normalvariate(0, 1) for k in range(dimension)]) * sigma
        # v = np.array([normalvariate(0, 1) for k in range(dimension)])
        # step = u / abs(v) ** (1 / beta)

        self._agents = np.random.uniform(lb, ub, (n, dimension))
        self._nests = np.random.uniform(lb, ub, (nest, dimension))
        Pbest = self._nests[np.array([function(x)
                                       for x in self._nests]).argmin()]
        Gbest = Pbest
        self._points(self._agents)

        for t in range(iteration):

            self._Levyfly(Pbest, n, dimension)

            for i in self._agents:
                val = randint(0, nest - 1)
                if function(i) < function(self._nests[val]):
                    self._nests[val] = i

            fnests = [(function(self._nests[i]), i) for i in range(nest)]
            fnests.sort()
            fcuckoos = [(function(self._agents[i]), i) for i in range(n)]
            fcuckoos.sort(reverse=True)

            # nworst = nest // 2
            # worst_nests = [fnests[-i - 1][1] for i in range(nworst)]

            # for i in worst_nests:
            #     if random() < pa:
            #         self._nests[i] = np.random.uniform(lb, ub, (1, dimension))

            # if nest > n:
            #     mworst = n
            # else:
            #     mworst = nest

            # for i in range(mworst):

            #     if fnests[i][0] < fcuckoos[i][0]:
            #         self._agents[fcuckoos[i][1]] = self._nests[fnests[i][1]]

            self._drop_worst_chance(nest, lb, ub, dimension, function)
            
            self._ordered_swap(n, nest, function)
            self._nests = np.clip(self._nests, lb, ub)
            # self._Levyfly(Pbest, n, dimension)
            self._agents = np.clip(self._agents, lb, ub)
            self._points(self._agents)
            # self._nest()

            Pbest = self._nests[np.array([function(x)
                                        for x in self._nests]).argmin()]

            if function(Pbest) < function(Gbest):
                Gbest = Pbest

        self._set_Gbest(Gbest)

    # def __nest(self):
    #     self.__Nests.append([list(i) for i in self.__nests])

    # def __Levyfly(self, step, Pbest, n, dimension):

    #     for i in range(n):
    #         stepsize = 0.2 * step * (self.__agents[i] - Pbest)
    #         self.__agents[i] += stepsize * np.array([normalvariate(0, 1)
    #                                                 for k in range(dimension)])

    # def get_nests(self):
    #     """Return a history of cuckoos nests (return type: list)"""

    #     return self.__Nests
