import numpy as np
from math import *
from helper import sw

class swarm(sw):
  def __init__(self, n, function, lb, ub, dimension, iterations):
    super(swarm, self).__init__()
    self._agents = np.random.uniform(lb, ub, (n, dimension))
    self._points(self._agents)
    Pbest = self._agents[np.array([function(x)for x in self._agents]).argmin()]
    Gbest = Pbest
    velocity = np.zeros((n, dimension))
    nest = 100
    self._nests = np.random.uniform(lb, ub, (nest, dimension))
    for t in range(iterations):
      self._velocity(Pbest, Gbest, n, dimension, velocity)
      swap = 1
      for i in self._agents: 
        val = np.random.randint(0, nest - 1)
        if function(i) < function(self._nests[val]):
          self._nests[val] = i
      self._ordered_swap(n, nest, function)
      self._agents = np.clip(self._agents, lb, ub)
      self._nests = np.clip(self._nests, lb, ub)
      self._points(self._agents)
      if swap:
        Pbest = self._nests[np.array([function(x) for x in self._nests]).argmin()]
      else:
        Pbest = self._agents[np.array([function(x) for x in self._agents]).argmin()]
      if function(Pbest) < function(Gbest):
        Gbest = Pbest
    self._set_Gbest(Gbest)