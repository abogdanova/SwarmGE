from utilities.trackers import best_fitness_list
from algorithm.parameters import params
from os import getcwd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
plt.rc('font', family='Times New Roman')


def save_best_fitness_plot():

    fig = plt.figure()#figsize=[20,15])
    ax1 = fig.add_subplot(1,1,1)
    ax1.plot(best_fitness_list)
    ax1.set_ylabel('fitness', fontsize=14)
    ax1.set_xlabel('Generation', fontsize=14)
    plt.savefig(getcwd()+'/results/'+str(params['TIME_STAMP'])+'/fitness.pdf')
    plt.close()
