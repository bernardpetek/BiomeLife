import pygame
import Biome

class Display:
    WIN_MIN_WIDTH = 300
    WIN_MIN_HEIGHT = 300
    REFRESH_RATE = 20
    GRID = 1

    def __init__(self, cells_x, cells_y, cell_size = 10):
        pygame.init()
        self.CELL_SIZE = cell_size
        win_width = cells_x * self.CELL_SIZE + cells_x * self.GRID
        win_height = cells_y * self.CELL_SIZE + cells_y * self.GRID
        if win_width < self.WIN_MIN_WIDTH: win_width = self.WIN_MIN_WIDTH
        if win_height < self.WIN_MIN_HEIGHT: win_height = self.WIN_MIN_HEIGHT

        # best organism score trace
        self.tracePositions = []

        self.win = pygame.display.set_mode((win_width, win_height))
        self.clock = pygame.time.Clock()

    def draw(self, biome):
        self.clock.tick(self.REFRESH_RATE)

        # handle input events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
            
        # track organism with best fitness
        max_fitness_score = 0
        max_fitness_score_organism_position = None

        # draw biome
        for y, row in enumerate(biome.map):
            for x, tile in enumerate(row):

                tileOccupierType = tile.getOccupierType()
                draw_x = x * self.CELL_SIZE + x * self.GRID
                draw_y = y * self.CELL_SIZE + y * self.GRID

                if tileOccupierType == Biome.Occupier.FOOD:
                    self.drawRectangle(self.win,
                                       (draw_x, draw_y),
                                       (self.CELL_SIZE, self.CELL_SIZE),
                                       (0, 255, 0))
                elif tileOccupierType == Biome.Occupier.DANGER:
                    self.drawRectangle(self.win,
                                       (draw_x, draw_y),
                                       (self.CELL_SIZE, self.CELL_SIZE),
                                       (255, 0, 0))
                elif tileOccupierType == Biome.Occupier.ORGANISM:

                    # track fitness
                    if tile.getOccupier().genome.fitness > max_fitness_score:
                        max_fitness_score = tile.getOccupier().genome.fitness
                        max_fitness_score_organism_position = (x, y)

                    color = (0, 0, 0)
                    if tile.getOccupier().GENDER == Biome.Organism.Gender.MALE: color = (0, 0, 255)
                    elif tile.getOccupier().GENDER == Biome.Organism.Gender.FEMALE: color = (160, 0, 255)
                    self.drawRectangle(self.win,
                                        (draw_x, draw_y),
                                        (self.CELL_SIZE, self.CELL_SIZE),
                                        color)
                else:
                    self.drawRectangle(self.win,
                                       (draw_x, draw_y),
                                       (self.CELL_SIZE, self.CELL_SIZE),
                                       (0, 100, 0))

        # draw best fitness score trace
        for trace in self.tracePositions:
            self.drawRectangle(self.win,
                                (trace[0] * self.CELL_SIZE + trace[0] * self.GRID + int(self.CELL_SIZE * 0.4), trace[1] * self.CELL_SIZE + trace[1] * self.GRID + int(self.CELL_SIZE * 0.4)),
                                (int(self.CELL_SIZE * 0.2), int(self.CELL_SIZE * 0.2)),
                                (255, 255, 0))


        # mark organism with best fitness score
        if max_fitness_score_organism_position:
            self.tracePositions.append((max_fitness_score_organism_position[0], max_fitness_score_organism_position[1]))
            self.drawRectangle(self.win,
                                    (max_fitness_score_organism_position[0] * self.CELL_SIZE + max_fitness_score_organism_position[0] * self.GRID + int(self.CELL_SIZE * 0.25), max_fitness_score_organism_position[1] * self.CELL_SIZE + max_fitness_score_organism_position[1] * self.GRID + int(self.CELL_SIZE * 0.25)),
                                    (int(self.CELL_SIZE * 0.5), int(self.CELL_SIZE * 0.5)),
                                    (255, 255, 0))

        pygame.display.update()
        return True
    
    def drawRectangle(self, win, position, size, color):
        rect = pygame.Rect(position, size)
        pygame.draw.rect(win, color, rect)