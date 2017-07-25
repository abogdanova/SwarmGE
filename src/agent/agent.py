from operators.initialisation import initialisation
from fitness.evaluation import evaluate_fitness
from stats.stats import stats, get_stats
from operators.crossover import crossover
from operators.mutation import mutation
from operators.replacement import replacement, steady_state
from operators.selection import selection

class Agent():
    """
    Class representing individual robots.
    """
    def __init__(self,ip):
        # This individual has all the genetic property of 
        #self.individual = individual
        self.interaction_probability = ip
        self.individual = initialisation(1)       
        self.individual = evaluate_fitness(self.individual)
        #get_stats(self.individual,end=True)
        self.AGENTS_FOUND = False

    def sense(self,agents):
        # Define the probability for interaction with other agents.
        # This part makes this GE algorithm useful for multi-agent systems
        import random
        if random.random() > self.interaction_probability:
            self.AGENTS_FOUND = True
            # Getting values to sample agents for interaction
            range_min = int((self.interaction_probability*len(agents))/3)
            range_max = int((self.interaction_probability*len(agents))/2)
            range_avg = int((range_min + range_max) / 2)
            no_agents_found = random.sample(range(len(agents)),random.choice([range_min,range_max,range_avg]))
            self.nearby_agents = [agents[i].individual[0] for i in no_agents_found]

    def act(self):
        if self.AGENTS_FOUND:
            # Select parents from the original individual and individuals gather from interaction.
            individuals = self.individual + self.nearby_agents
            #print (individuals)
            parents = selection(individuals)
            # Crossover parents and add to the new population.
            cross_pop = crossover(parents)

            # Mutate the new population.
            new_pop = mutation(cross_pop)

            # Evaluate the fitness of the new population.
            new_pop = evaluate_fitness(new_pop)

            # Replace the old population with the new population.
            individuals = replacement(new_pop, individuals)

            # Generate statistics for run so far
            get_stats(individuals)
            
            #self.new_individual = sort(individuals)[0]
            individuals.sort(reverse=True)
            self.new_individual = individuals[0]
    
    def update(self):
        if self.AGENTS_FOUND:
            self.individual = [self.new_individual]