from __future__ import division
# from deap import creator, base, tools, algorithms
from copy import copy
import numpy as np
import random

def pdiv(a, b):
    """ Protected division operator to prevent division by zero"""
    if type(b) is np.ndarray:
        # Then we have matrix division
        zeros = b == 0
        den = copy(b)
        den[zeros] = 1
        return a/den
    else:
        if b == 0:
            return a
        else:
            return a/b

def get_schedule(num_attached, instan_downlinks, SINR):
    random.seed(5)

    def get_fitness(individual):
        individual = np.array(individual)
        schedule = individual.reshape(8, num_attached)
        schedule[SINR <= 0.31622777] = 0
        lookup = np.sum(schedule, axis=0) == 0
        schedule[:, lookup] = 1
        schedule[SINR <= 0.31622777] = 0
        lookup = np.sum(schedule, axis=1) == 0
        schedule[lookup, :] = 1

        downlinks = copy(instan_downlinks)
        downlinks[schedule == 0] = 0

        bandwidth = 20000000.0
        num_sharing_sf = np.ones(shape=(8, num_attached)) * np.sum(schedule, axis=1)[:, None]
        downlinks = downlinks * pdiv(bandwidth, num_sharing_sf)
        average_downlinks = np.average(downlinks, axis=0)
        log_average_downlinks = np.log(average_downlinks[average_downlinks > 0])

        return np.sum(log_average_downlinks),

    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    def initIndividual(icls, content):
        return icls(content)

    def initPopulation(pcls, ind_init, filename):
        contents = json.load(open(filename, "r"))
        return pcls(ind_init(c) for c in contents)

    toolbox = base.Toolbox()

    toolbox.register("attr_bool", random.randint, 0, 1)
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_bool, n=8*num_attached)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", get_fitness)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutFlipBit, indpb=0.01)
    toolbox.register("select", tools.selTournament, tournsize=3)
    population = toolbox.population(n=500)

    # Seed one ind in the population as the baseline. This will ensure no
    # solution will perform worse than this.
    for i in range(len(population[0])):
        population[0][i] = 1

    NGEN = 250
    for gen in range(NGEN):
        offspring = algorithms.varAnd(population, toolbox, cxpb=1.0, mutpb=0.2)
        fits = list(map(toolbox.evaluate, offspring))
        for fit, ind in zip(fits, offspring):
            ind.fitness.values = fit
        population = toolbox.select(offspring, k=len(population))
    top = tools.selBest(population, k=10)

    individual = np.array(top[0])
    schedule = individual.reshape(8, num_attached)
    schedule[SINR <= 0.31622777] = 0
    lookup = np.sum(schedule, axis=0) == 0
    schedule[:, lookup] = 1
    schedule[SINR <=  0.31622777] = 0
    lookup = np.sum(schedule, axis=1) == 0
    schedule[lookup, :] = 1
    schedule = np.vstack((schedule, schedule, schedule, schedule, schedule))

    return schedule.astype(bool)
