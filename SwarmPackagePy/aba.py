import numpy as np
from random import randint, uniform

import helper


class aba(helper.sw):
    """
    Artificial Bee Algorithm
    """

    def __init__(self, n, function, lb, ub, dimension, iteration):
        """
        :param n: number of agents
        :param function: test function
        :param lb: lower limits for plot axes
        :param ub: upper limits for plot axes
        :param dimension: space dimension
        :param iteration: number of iterations
        """

        super(aba, self).__init__()

        self._function = function

        self._agents = np.random.uniform(lb, ub, (n, dimension))
        self._points(self._agents)

        Pbest = self._agents[np.array([function(x)
                                        for x in self._agents]).argmin()]
        Gbest = Pbest

        if n <= 10:
            count = n - n // 2, 1, 1, 1
        else:
            a = n // 10
            b = 5
            c = (n - a * b - a) // 2
            d = 2
            count = a, b, c, d

        for t in range(iteration):

            fitness = [function(x) for x in self._agents]
            sort_fitness = [function(x) for x in self._agents]
            sort_fitness.sort()

            best = [self._agents[i] for i in
                    [fitness.index(x) for x in sort_fitness[:count[0]]]]
            selected = [self._agents[i]
                        for i in [fitness.index(x)
                                  for x in sort_fitness[count[0]:count[2]]]]

            newbee = self._newbee(best, count[1], lb, ub) + self._newbee(selected,
                                                                   count[3],
                                                                   lb, ub)
            m = len(newbee)
            self._agents = newbee + list(np.random.uniform(lb, ub, (n - m,
                                                                   dimension)))

            self._agents = np.clip(self._agents, lb, ub)
            self._points(self._agents)

            Pbest = self._agents[
                np.array([function(x) for x in self._agents]).argmin()]
            if function(Pbest) < function(Gbest):
                Gbest = Pbest

        self._set_Gbest(Gbest)

    # def __new(self, l, c, lb, ub):

    #     bee = []
    #     for i in l:
    #         new = [self.__neighbor(i, lb, ub) for k in range(c)]
    #         bee += new
    #     bee += l

    #     return bee

    # def __neighbor(self, who, lb, ub):

    #     neighbor = np.array(who) + uniform(-1, 1) * (
    #         np.array(who) - np.array(
    #             self.__agents[randint(0, len(self.__agents) - 1)]))
    #     neighbor = np.clip(neighbor, lb, ub)

    #     return list(neighbor)
