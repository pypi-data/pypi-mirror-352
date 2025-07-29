
def attempts(prod, profession):
    if profession == "mining" or profession == "token mining":
        if prod:
            return 25
        else:
            return 1
    elif profession == "gardening":
        if prod:
            return 25
        else:
            return 1
    else:
        if prod:
            return 5
        else:
            return 1

class HeroQuestData:
    def __init__(self, prod, heroId, profession, quest_type, level, status):
        self.profession = profession
        self.heroId = heroId
        self.attempts = attempts(prod, profession)
        self.quest_type = quest_type
        self.level = level
        self.status = status

    def __str__(self):
        return str(self.__dict__)
    
    def comparation_string(self):
        return self.profession + str(self.level) + str(self.quest_type) + self.status

class QuestGroup:
    def __init__(self):
        self.heroes: list[HeroQuestData] = []
    
    def __str__(self):
        return str([str(hero) for hero in self.heroes])
    
    def addHeroToGroup(self, heroQuest: HeroQuestData):
        self.heroes.append(heroQuest)
