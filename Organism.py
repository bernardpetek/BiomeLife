from enum import Enum
import I_Interactable
import Biome

class Gender(Enum):
    MALE = 1
    FEMALE = 2

class Organism(I_Interactable.I_Interactable):

    def __init__(self, gender: Gender, genome = None, neuralNetwork = None):
        self.GENDER = gender
        self.POWER = 50
        self.INTELIGENCE = 50

        self.food = 30
        self.turns = 0 # number of game turns by this organism
        self.steps = 0
        self.vertical_moves = 0
        self.horizontal_moves = 0
        self.turns_counter = [0, 0, 0, 0] # [up, down, left, right]
        self.no_moves = 0
        self.lastPosition = None

        if genome and neuralNetwork:
            self.genome = genome
            self.genome.fitness = 0
            self.neural_network = neuralNetwork
        else:
            self.genome = None
            self.neural_network = None

    def getFoodPoints(self):
        return self.food

    def addFood(self, food):
        self.food += food

    def getPowerPoints(self):
        return self.POWER

    def getInteligencePoints(self):
        return self.INTELIGENCE

    # function that contains logic needed to make a decisions about this turn
    def takeTurn(self, occupierPosition, moveCallback, dieCallback, surrounding = None):

        # generate inputs array
        inputs = []
        for i, tile in enumerate(surrounding):
            if surrounding[i]:
                inputs.append(1 if surrounding[i] and surrounding[i].getOccupierType() == Biome.Occupier.ORGANISM else 0)
                inputs.append(1 if surrounding[i] == None or surrounding[i].getOccupierType() == Biome.Occupier.DANGER else 0)
                inputs.append(1 if surrounding[i] and surrounding[i].getOccupierType() == Biome.Occupier.FOOD else 0)
            else:
                inputs.append(0)
                inputs.append(0)
                inputs.append(0)
        # add direction from which organism is comming
        if self.lastPosition:
            directionMatrix = self.getLastPositionDirectionMatrix(self.lastPosition, occupierPosition)
        else: directionMatrix = [0, 0, 0, 0]
        # loop add all directional matrix items to inputs matrix
        for direction in directionMatrix:
            inputs.append(direction)

        # Add amount of food to inputs
        food_input = self.clamp(self.food/200, 0, 1)
        inputs.append(food_input)

        # Add organism gender to inputs
        #inputs.append(1 if self.GENDER == Gender.MALE else 0)

        # if there is neural network added to this organism than put those cells to good use
        # Activate neural network.
        if self.neural_network != None:
            output = self.neural_network.activate(tuple(inputs))
            direction = self.outputToMoveDirection(output)
        else: direction = Biome.MoveDirection.RIGHT

        # add to turns counter
        self.turns += 1

        prewFood = self.food
        lastLastPosition = self.lastPosition
        self.lastPosition = occupierPosition
        occupierPosition = self.move(occupierPosition, direction, moveCallback)

        # chack if organism is only movein in straight line
        if self.lastPosition[0] == occupierPosition[0]:
            self.vertical_moves += 1
        else:
            self.vertical_moves = 0

        if self.lastPosition[1] == occupierPosition[1]:
            self.horizontal_moves += 1
        else:
            self.horizontal_moves = 0

        if self.lastPosition == occupierPosition:
            self.no_moves += 1
        else:
            self.no_moves = 0

        # take care for counting turns
        self.countTurns((lastLastPosition, self.lastPosition, occupierPosition))

        # consume food on each turn
        if self.lastPosition == occupierPosition:
            self.food -= 1
        else:
            self.food -= 1
            self.steps += 1

        if self.genome != None:
            # punish straight line movement and no movement for long time
            if self.horizontal_moves > 20 or self.vertical_moves > 20 or self.no_moves > 5:
                self.genome.fitness -= 1
            else:
                self.genome.fitness += 0.01 * self.food
            #self.genome.fitness += 0.01 * self.food

            # eating food is rewarded and eating poison is degraded
            if prewFood < self.food: self.genome.fitness += 10
            elif prewFood - 1 > self.food:
                if (self.genome.fitness > 0): self.genome.fitness = self.genome.fitness * 0.8
                else: self.genome.fitness -= 10

            # moving is rewarded
            if self.lastPosition != occupierPosition: self.genome.fitness += 0.05

        if self.food <= 0:
            # punish turning only up or down in the entire life
            if (self.turns_counter[1] == 0 and self.turns_counter[0] > 0 or # self.genome.fitness = self.genome.fitness * 0.8 # only going up
               self.turns_counter[0] == 0 and self.turns_counter[1] > 0 or # self.genome.fitness = self.genome.fitness * 0.8 # only going down
               self.turns_counter[3] == 0 and self.turns_counter[2] > 0 or # self.genome.fitness = self.genome.fitness * 0.8 # only going left
               self.turns_counter[2] == 0 and self.turns_counter[3] > 0):   # self.genome.fitness = self.genome.fitness * 0.8 # only going right
                if (self.genome.fitness > 0): self.genome.fitness = self.genome.fitness * 0.8
                else: self.genome.fitness -= 10

            dieCallback(occupierPosition)

        # die by old age - just to try to encourage more complex behaviour and lower generation execution length
        if self.turns > 1500:
            print('--------- Died by old age! ---------')
            dieCallback(occupierPosition)

    def move(self, occupierPosition, direction, moveCallback):
        return moveCallback(occupierPosition, direction)

    def outputToMoveDirection(self, output):
        output = self.tupleToBinaryTuple(output)

        if   not output[0] and not output[1] and not output[2] : return Biome.MoveDirection.UP
        elif not output[0] and not output[1] and     output[2] : return Biome.MoveDirection.DOWN
        elif not output[0] and     output[1] and not output[2] : return Biome.MoveDirection.LEFT
        elif not output[0] and     output[1] and     output[2] : return Biome.MoveDirection.RIGHT
        else: return None

    def tupleToBinaryTuple(self, outputFloats):
        output = []
        for val in outputFloats:
            output.append(bool(int(round(val))))

        return tuple(output)
    
    # get an tuple (length of 4) that represent if last position was on the upper, lower, left or right tile
    # tuple structure ... (upper, lower, left, right)
    def getLastPositionDirectionMatrix(self, lastPosition, currentPosition):
        output = [0, 0, 0, 0]

        if currentPosition[0] == lastPosition[0]: pass
        elif currentPosition[0] > lastPosition[0] and lastPosition[0] + 1 == currentPosition[0]: output[2] = 1
        else: output[3] = 1

        if currentPosition[1] == lastPosition[1]: pass
        elif currentPosition[1] > lastPosition[1] and lastPosition[1] + 1 == currentPosition[1]: output[0] = 1
        else: output[1] = 1

        return output

    def clamp(self, value, min_value, max_value):
        return max(min(value, max_value), min_value)
    
    # count organims turns (in which side it turned (up, down, left or right ... based on sides of the biome))
    def countTurns(self, stepsHistory):
        if stepsHistory or not stepsHistory[0] or not stepsHistory[1] or not stepsHistory[2]: return

        directionVector = self.getDirectionVector(stepsHistory[2], stepsHistory[0])
        
        # Determine on which side (based on the board orientation) organism urned and add to counter
        if directionVector[0] == 1 and directionVector[1] == 1: # right and up OR up and right
            if stepsHistory[0][0] == stepsHistory[1][0]: self.turns_counter[0] += 1 # right and up
            else: self.turns_counter[3] += 1 # up and right
        elif directionVector[0] == -1 and directionVector[1] == 1: # left and up OR up and left
            if stepsHistory[0][0] == stepsHistory[1][0]: self.turns_counter[0] += 1 # left and up
            else: self.turns_counter[2] += 1 # up and left
        elif directionVector[0] == -1 and directionVector[1] == -1: # left and down OR down and left
            if stepsHistory[0][0] == stepsHistory[1][0]: self.turns_counter[1] += 1 # left and down
            else: self.turns_counter[2] += 1 # down and left
        elif directionVector[0] == -1 and directionVector[1] == -1: # right and down OR down and right
            if stepsHistory[0][0] == stepsHistory[1][0]: self.turns_counter[1] += 1 # right and down
            else: self.turns_counter[3] += 1 # down and right

    
    # get direction vector (this has to be used only to get vector within three steps)
    def getDirectionVector(self, start, end):
        x = end[0]-start[0]
        y = end[1]-start[1]

        # if the is more than two spaces in distance than there was a jump to the other side of the map/biome
        if abs(x) > 2: x = int((x * (-1)) / x)
        if abs(y) > 2: y = int((y * (-1)) / y)

        return (x, y)
"""
Inputs:
    - [tile.occupier.type] ... for 5x5(-1) squares around organism

Outputs:
    0.0-0.2 ... don't move
    0.2-0.4 ... up
    0.4-0.6 ... down
    0.6-0.8 ... left
    0.8-1.0 ... right
"""