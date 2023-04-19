import os
import Biome
import Display
import neat
import matplotlib
# matplotlib.use('QtAgg')
import matplotlib.pyplot as plt
import copy

GEN = 0

def eval_genomes(genomes, config):
    global stats
    global fig
    global ax
    global fitness_graph

    global GEN
    GEN += 1

    biome = Biome.Biome(100, 50)

    for _, genome in genomes:
        neuralNetwork = neat.nn.FeedForwardNetwork.create(genome, config)
        biome.addOccupier(Biome.Organism.Organism(None, genome, neuralNetwork))

    cycle = 0
    draw_every_n_cycle = 1

    if GEN <= 1: draw_every_n_cycle = 1
    elif(GEN < 1000 and GEN%20 == 0): draw_every_n_cycle = 1
    elif(GEN > 1000): draw_every_n_cycle = 1
    else: draw_every_n_cycle = 100

    dispaly = Display.Display(biome.getBiomeWidth(), biome.getBiomeHight(), 10)

    while True:
        biome.makeTurn()

        if cycle%draw_every_n_cycle == 0 and dispaly.draw(biome) == False: quit()
        if len(biome.organismsPos) <= 0:
            if GEN > 1:
                if GEN == 2: plt.show()
                mean_fitness = stats.get_fitness_mean()
                fitness_graph.set_xdata(range(0, len(mean_fitness)))
                fitness_graph.set_ydata(mean_fitness)
                ax.set_xlim((0, len(mean_fitness)))
                ax.set_ylim((min(mean_fitness), max(mean_fitness)))
                fig.canvas.draw()
                fig.canvas.flush_events()
            return

        cycle += 1

def eval_genomes_in_separate_biomes(genomes, config):
    MAX_ORGANISMS_PER_BIOME = 50

    global stats
    global fig
    global ax
    global fitness_graph

    global GEN
    GEN += 1

    biomes = [Biome.Biome(100, 50)]
    biome_organisms_counter = 0

    for _, genome in genomes:
        if biome_organisms_counter >= MAX_ORGANISMS_PER_BIOME:
            biome_organisms_counter = 0
            biomes.append(Biome.Biome(100, 50))

        neuralNetwork = neat.nn.FeedForwardNetwork.create(genome, config)
        biomes[len(biomes) - 1].addOccupier(Biome.Organism.Organism(None, genome, neuralNetwork))

        biome_organisms_counter += 1
    
    while True:
        for biome in biomes:
            biome.makeTurn()

        # check if all organisms are dead in all biomes
        allDead = True
        for biome in biomes:
            if biome.getOrganismsCount() > 0: 
                allDead = False
                break

        # If no organism is alive ... write fitnes to graph and exit the function
        if allDead:
            if GEN > 1:
                if GEN == 2: plt.show()
                mean_fitness = stats.get_fitness_mean()
                fitness_graph.set_xdata(range(0, len(mean_fitness)))
                fitness_graph.set_ydata(mean_fitness)
                ax.set_xlim((0, len(mean_fitness)))
                ax.set_ylim((min(mean_fitness), max(mean_fitness)))
                fig.canvas.draw()
                fig.canvas.flush_events()
            return

def test():
    print("Running test function...")
    biome = Biome.Biome(100, 50)

    biome.addOccupier(Biome.Organism.Organism(None))

    dispaly = Display.Display(biome.getBiomeWidth(), biome.getBiomeHight(), 10)

    cycle = 0
    draw_every_n_cycle = 1
    while True:
        biome.makeTurn()

        if cycle%draw_every_n_cycle == 0 and dispaly.draw(biome) == False: quit()

        cycle += 1

def runWinner(best_genome, config):
    biome = Biome.Biome(100, 50)

    neuralNetwork = neat.nn.FeedForwardNetwork.create(best_genome, config)

    for i in range(100):
        biome.addOccupier(Biome.Organism.Organism(None, copy.deepcopy(best_genome), neuralNetwork))
    
    dispaly = Display.Display(biome.getBiomeWidth(), biome.getBiomeHight(), 10)

    while True:
        biome.makeTurn()
        if dispaly.draw(biome) == False: return


def run(config_path):
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    
    # create population
    p = neat.Population(config)

    p.add_reporter(neat.StdOutReporter(True))
    global stats
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    # configure plot
    global fig
    global ax
    global fitness_graph
    fig, ax = plt.subplots()
    plt.ion()
    fitness_graph, = ax.plot([], [])
    #plt.show()

    #winner = p.run(eval_genomes, 2000)

    while True:
        winner = p.run(eval_genomes_in_separate_biomes, 50)

        while True:
            user_input = input("1 ... run winner, 2 ... new training loop, 3 ... exit\n")

            if user_input == "1": runWinner(winner, config)
            elif user_input == "2": break
            elif user_input == "3": quit()

    
    #input("Run the biome with best genome. Press ENTER.")
    #runWinner(winner, config)
    #input("Finnished. Press ENTER.")
    #quit()

if __name__ == "__main__":
    # local_dir = os.path.dirname(__file__)
    config_path = os.path.join("conf", "config-feedforward.txt")   

    run(config_path)
    #test()