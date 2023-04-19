import I_Interactable

class Food(I_Interactable.I_Interactable):
    FOOD = 20
    #color

    def __init__(self):
        pass

    def getFoodPoints(self):
        return 10
    
    def addFood(self, food):
        pass

    def getPowerPoints(self):
        return 0

    def getInteligencePoints(self):
        return 0

    # function that contains logic needed to make a decisions about this turn
    def takeTurn(self, occupierPosition, moveCallback, dieCallback, surrounding):
        pass