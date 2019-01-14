import SwarmPackagePy
from SwarmPackagePy import testFunctions as tf
from SwarmPackagePy import animation, animation3D


alh = SwarmPackagePy.swarm(50, tf.ackley_function, -5, 5, 3, 30)
animation(alh.get_agents(), tf.ackley_function, -5, 5)
animation3D(alh.get_agents(), tf.ackley_function, -5, 5)

