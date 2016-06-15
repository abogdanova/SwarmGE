from algorithm.parameters import params
from os import path, mkdir, getcwd
import matplotlib.pyplot as plt

def search_loop_save_plot(fitness_plot, fitness):
    file_path = getcwd()
    if not path.isdir(str(file_path) + "/Results"):
        mkdir(str(file_path) + "/Results")
    if not path.isdir(str(file_path) + "/Results/" + str(params['TIME_STAMP'])):
        mkdir(str(file_path) + "/Results/" + str(params['TIME_STAMP']))
    fitness_plot.append(fitness)
    fig = plt.figure()#figsize=[20,15])
    ax1 = fig.add_subplot(1,1,1)
    ax1.plot(fitness_plot)
    ax1.set_ylabel('fitness', fontsize=14)
    ax1.set_xlabel('Generation', fontsize=14)
    plt.savefig(getcwd()+'/Results/'+str(params['TIME_STAMP'])+'/fitness.pdf')
    plt.close()