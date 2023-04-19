from enum import Enum
import Food
import Danger
import Organism
import random

#class Tile(Enum):
#        WATER = 1
#        GRASS = 2
#        # LAVA = 2

class MoveDirection(Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class Occupier(Enum):
    EMPTY = 0
    ORGANISM = 1
    FOOD = 2
    DANGER = 3 # This is poison ... it can be eaten just like food

class MapTile:

    def __init__(self, occupier):
        self.occupier = occupier

    def setOccupier(self, occupier):
        self.occupier = occupier

    def getOccupier(self):
        return self.occupier
    
    def getOccupierType(self):
        occType = type(self.occupier)

        if str(occType) == "<class 'Food.Food'>":
            return Occupier.FOOD
        elif str(occType) == "<class 'Danger.Danger'>":
            return Occupier.DANGER
        elif str(occType) == "<class 'Organism.Organism'>":
            return Occupier.ORGANISM
        else:
            return Occupier.EMPTY

class Biome:
    CHANCE_OF_SPAWNING_ORGANISM = 0.01
    CHANCE_OF_ORGANISM_IS_MALE = 0.5
    CHANCE_OF_FOOD_SPAWNING = 0.04 #0.02
    CHANCE_OF_DANGER_SPAWNING = 0.05

    def __init__(self, biome_width, biome_height):
        self.map = []
        self.organismsPos = []
        self.foodPos = []
        self.dangerPos = []

        self.BIOME_WIDTH = biome_width
        self.BIOME_HEIGHT = biome_height
        self.NUMBER_OF_FOOD = int(biome_width * biome_height * self.CHANCE_OF_FOOD_SPAWNING)
        self.NUMBER_OF_DANGER = int(biome_width * biome_height * self.CHANCE_OF_DANGER_SPAWNING)
     
        self.generateMap(biome_width, biome_height)

    def generateMap(self, biome_width, biome_height):
        self.map = [[MapTile(None) for j in range(biome_width)] for i in range(biome_height)]
    
    def populateWithOrganisms(self):
        self.populateWith(Organism.Organism(None), self.CHANCE_OF_SPAWNING_ORGANISM)

    def populateWithFood(self):
        self.populateWith(Food.Food(), self.CHANCE_OF_FOOD_SPAWNING)

    def populateWithDanger(self):
        self.populateWith(Danger.Danger(), self.CHANCE_OF_DANGER_SPAWNING)

    def populateWith(self, occupier, chanceOfSpawn):
        for y, row in enumerate(self.map):
            for x, h in enumerate(row):
                if h.getOccupierType() == Occupier.EMPTY and random.randint(0, 100) <= chanceOfSpawn * 100:
                    if str(type(occupier)) == "<class 'Organism.Organism'>":
                        if random.randint(0, 100) <= self.CHANCE_OF_ORGANISM_IS_MALE * 100:
                            h.setOccupier(Organism.Organism(Organism.Gender.MALE))
                        else:
                            h.setOccupier(Organism.Organism(Organism.Gender.FEMALE))
                    else: h.setOccupier(occupier)

                    if h.getOccupierType() == Occupier.FOOD:
                        self.foodPos.append((x, y))
                    elif h.getOccupierType() == Occupier.DANGER:
                        self.dangerPos.append((x, y))
                    elif h.getOccupierType() == Occupier.ORGANISM:
                        self.organismsPos.append((x, y))
    
    def addOccupier(self, occupier):
        
        added = False
        tries_count = 0
        while added == False and tries_count < 30:
            x = random.randint(0, len(self.map[0])-1)
            y = random.randint(0, len(self.map)-1)
            tile = self.map[y][x]

            if tile.getOccupierType() == Occupier.EMPTY:
                if str(type(occupier)) == "<class 'Organism.Organism'>" and occupier.GENDER == None:
                    if random.randint(0, 100) <= self.CHANCE_OF_ORGANISM_IS_MALE * 100:
                        occupier.GENDER = Organism.Gender.MALE
                    else:
                        occupier.GENDER = Organism.Gender.FEMALE
                
                tile.setOccupier(occupier)
                added = True

                if tile.getOccupierType() == Occupier.FOOD:
                    self.foodPos.append((x, y))
                elif tile.getOccupierType() == Occupier.DANGER:
                    self.dangerPos.append((x, y))
                elif tile.getOccupierType() == Occupier.ORGANISM:
                    self.organismsPos.append((x, y))
            
            tries_count += 1

    def getBiomeHight(self):
        return self.BIOME_HEIGHT

    def getBiomeWidth(self):
        return self.BIOME_WIDTH
    
    def tilesInteraction(self, sourcePos, targetPos):
        source = self.map[sourcePos[1]][sourcePos[0]]
        target = self.map[targetPos[1]][targetPos[0]]

        if source.getOccupierType() == Occupier.ORGANISM:
            if target.getOccupierType() == Occupier.FOOD:
                source.getOccupier().addFood(
                    target.getOccupier().getFoodPoints()
                )
                self.deleteOccupier(targetPos)
            elif target.getOccupierType() == Occupier.DANGER:
                source.getOccupier().addFood(
                    target.getOccupier().getFoodPoints()
                )
                self.deleteOccupier(targetPos)
            elif target.getOccupierType() == Occupier.ORGANISM:
                pass
    
    def makeTurn(self):
        # just take sure that there is allways the same number of food
        n_food = len(self.foodPos)
        for i in range(0, self.NUMBER_OF_FOOD - n_food):
            self.addOccupier(Food.Food())

        # just take sure that there is allways the same number of danger
        n_danger = len(self.dangerPos)
        for i in range(0, self.NUMBER_OF_DANGER - n_danger):
            self.addOccupier(Danger.Danger())

        # cicle through all organisms and ask them to take a turn
        for pos in self.organismsPos:
            if pos == None: continue
            occupier = self.map[pos[1]][pos[0]].getOccupier()
            if occupier: occupier.takeTurn(pos, self.moveOccupier, self.deleteOccupier, self.getSurrounding(pos, 5))

        # clean None values from organismsPos, foodPos and dangerPos arrays
        self.cleanPositionsArrays()


    def moveOccupier(self, occupierPosition, direction: MoveDirection):
        if direction == MoveDirection.RIGHT:
            newCoordinate = occupierPosition[0] + 1
            if newCoordinate >= self.BIOME_WIDTH: newCoordinate = 0
            newPosition = (newCoordinate, occupierPosition[1])
        elif direction == MoveDirection.LEFT:
            newCoordinate = occupierPosition[0] - 1
            if newCoordinate < 0: newCoordinate = self.BIOME_WIDTH - 1
            newPosition = (newCoordinate, occupierPosition[1])
        elif direction == MoveDirection.UP:
            newCoordinate = occupierPosition[1] - 1
            if newCoordinate < 0: newCoordinate = self.BIOME_HEIGHT - 1
            newPosition = (occupierPosition[0], newCoordinate)
        elif direction == MoveDirection.DOWN:
            newCoordinate = occupierPosition[1] + 1
            if newCoordinate >= self.BIOME_HEIGHT: newCoordinate = 0
            newPosition = (occupierPosition[0], newCoordinate)
        else: return occupierPosition

        self.tilesInteraction(occupierPosition, newPosition)

        sourceOccupierType = self.map[occupierPosition[1]][occupierPosition[0]].getOccupierType()
        targetOccupierType = self.map[newPosition[1]][newPosition[0]].getOccupierType()

        if targetOccupierType != Occupier.EMPTY: return occupierPosition

        if sourceOccupierType == Occupier.ORGANISM:
            self.organismsPos[self.organismsPos.index(occupierPosition)] = newPosition
        elif  sourceOccupierType == Occupier.FOOD:
            self.foodPos[self.foodPos.index(occupierPosition)] = newPosition
        elif  sourceOccupierType == Occupier.DANGER:
            self.dangerPos[self.dangerPos.index(occupierPosition)] = newPosition
        else: return occupierPosition

        tile = self.map[occupierPosition[1]][occupierPosition[0]]
        self.map[newPosition[1]][newPosition[0]].setOccupier(tile.getOccupier())
        self.map[occupierPosition[1]][occupierPosition[0]].setOccupier(None)
        
        return newPosition

    # delete occupier from map (set it to None)
    def deleteOccupier(self, position):
        occupierType = self.map[position[1]][position[0]].getOccupierType()

        self.map[position[1]][position[0]].setOccupier(None)

        if occupierType == Occupier.ORGANISM:
            self.organismsPos[self.organismsPos.index(position)] = None
        elif  occupierType == Occupier.FOOD:
            self.foodPos[self.foodPos.index(position)] = None
        elif  occupierType == Occupier.DANGER:
            self.dangerPos[self.dangerPos.index(position)] = None

    # find elements with None value and remove them
    def cleanPositionsArrays(self):
        for i, o in enumerate(self.organismsPos):
            if o == None:
                self.organismsPos.pop(i)
        
        for i, o in enumerate(self.foodPos):
            if o == None:
                self.foodPos.pop(i)
        
        for i, o in enumerate(self.dangerPos):
            if o == None:
                self.dangerPos.pop(i)

    # get surrounding array
    # centerPos is tuple ... an organism position
    # size is an integer (must be even number!!!) ... and output array should be of size size*size-1
    def getSurrounding(self, centerPos, size):
        # if size is not even number raise exception
        if size%2 == 0: raise ValueError("Size parameter must be even number!")

        offset = int((size-1)/2)
        MaxX = len(self.map[0])
        MaxY = len(self.map)

        surrounding = []
        for x in range(centerPos[0] - offset, centerPos[0] + offset + 1):
            for y in range(centerPos[1] - offset, centerPos[1] + offset + 1):
                
                if x >= MaxX: xCoordinate = x - MaxX
                else: xCoordinate = x

                if y >= MaxY: yCoordinate = y - MaxY
                else: yCoordinate = y

                if x == centerPos[0] and y == centerPos[1]: continue
                else: surrounding.append(self.map[yCoordinate][xCoordinate])
        
        return surrounding

    # return number of live organisms in biome
    def getOrganismsCount(self):
        return len(self.organismsPos)


    
        