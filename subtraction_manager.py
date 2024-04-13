import random

class SubtractionManager:
    @staticmethod
    def initialize_static_variables():
        SubtractionManager.varA = random.randint(0, 30)
        SubtractionManager.varB = random.randint(-20, 20)
        SubtractionManager.answer = SubtractionManager.varA - SubtractionManager.varB
        SubtractionManager.answerChoices = [random.randint(abs(SubtractionManager.varA) * -1, abs(SubtractionManager.varB)) for _ in range(4)]
        SubtractionManager.correctIndex = random.randint(0, 3)
        SubtractionManager.answerChoices[SubtractionManager.correctIndex] = SubtractionManager.answer

    @staticmethod
    def makeNewProblem():
        SubtractionManager.varA = random.randint(0, 30)
        SubtractionManager.varB = random.randint(-20, 20)
        SubtractionManager.answer = SubtractionManager.varA - SubtractionManager.varB
        SubtractionManager.correctIndex = random.randint(0, 3)

        SubtractionManager.answerChoices = []
        for i in range(4):
            if i == SubtractionManager.correctIndex:
                SubtractionManager.answerChoices.append(SubtractionManager.answer)
            else:
                if random.random() < 0.5:
                    randAnswer = SubtractionManager.answer + random.randint(-5, 5)
                else:
                    randAnswer = SubtractionManager.answer * -1
                SubtractionManager.answerChoices.append(randAnswer)
        
        SubtractionManager.answerChoices[SubtractionManager.correctIndex] = SubtractionManager.answer

    @staticmethod
    def getProblem():
        return f"What is {SubtractionManager.varA} - {SubtractionManager.varB}?"


    @staticmethod
    def getAnswerChoices():
        return SubtractionManager.answerChoices

    @staticmethod
    def getCorrectIndex():
        return SubtractionManager.correctIndex

# Initialize static variables
SubtractionManager.initialize_static_variables()
