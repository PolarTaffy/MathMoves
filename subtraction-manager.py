import random

class SubtractionManager:
    def __init__(self):

        self.varA = random.randint(0, 30)
        self.varB = random.randint(-20, 20)
        
        self.answer = self.varA - self.varB

        self.answerChoices = [random.randint(abs(self.varA) * -1, abs(self.varB)), random.randint(1, 4), random.randint(1, 4), random.randint(1, 4)]
        self.correctIndex = random.randint(0, 3)


    def makeNewProblem(self):
        self.varA = random.randint(0, 30)
        self.varB = random.randint(-20, 20)
        self.answer = self.varA - self.varB
        self.correctIndex = random.randint(0, 3)

        self.answerChoices = []
        for i in range(4):
            if i == self.correctIndex:
                self.answerChoices.append(self.answer)
            else:
                if random.random(0, 10) < 5:
                    randAnswer = self.answer + random.randint(-5, 5)
                else:
                    randAnswer = self.answer * -1



    def getProblem(self):
        return "What is " + str(self.varA) + " - " + str(self.varB) + "?"

    def getAnswerChoices(self):
        return self.answerChoices

    def getCorrectIndex(self):
        return self.correctIndex
