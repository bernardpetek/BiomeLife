from abc import ABC, abstractmethod

class I_Interactable(ABC):
    @abstractmethod
    def getFoodPoints(self):
        pass

    @abstractmethod
    def addFood(self, food):
        pass

    @abstractmethod
    def getPowerPoints(self):
        pass

    @abstractmethod
    def getInteligencePoints(self):
        pass

    #@abstractmethod
    #def isWillingToReproduce():
    #    pass

    @abstractmethod
    def takeTurn(self, occupierPosition, moveCallback, dieCallback, surrounding):
        pass