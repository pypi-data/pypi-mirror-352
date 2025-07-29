class Hero:
    def __init__(
            self, 
            id: str,
            price: str,
            level: int,
            rarity: int,
            generation: int,
            summonsRemaining: int,
            summons: int,
            maxSummons: int,
            profession: str,
            mainClass: str,
            subClass: str,
            active1: int,
            active2: int,
            passive1: int,
            passive2: int,
):
        self.id: str = id
        self.price: str = price
        self.level: int = level
        self.rarity: int = rarity
        self.generation: int = generation
        self.summonsRemaining: int = summonsRemaining
        self.summons: int = summons
        self.maxSummons: int = maxSummons
        self.profession: str = profession
        self.mainClass: str = mainClass
        self.subClass: str = subClass
        self.active1: int = active1
        self.active2: int = active2
        self.passive1: int = passive1
        self.passive2: int = passive2


    def from_dfk_json(json: dict):
        return Hero(
            id=json["id"],
            price="0",
            level=json["level"],
            rarity=json["rarity"],
            generation=json["generation"],
            summonsRemaining=json["summonsRemaining"],
            summons=json["summons"],
            maxSummons=json["maxSummons"],
            profession=json["professionStr"],
            mainClass=json["mainClassStr"],
            subClass=json["subClassStr"],
            active1=json["active1"],
            active2=json["active2"],
            passive1=json["passive1"],
            passive2=json["passive2"],
        )

    def from_json(json: dict):
        return Hero(**json)
    
    def to_json(self):
        return self.__dict__

    
    def update_hero_price(self, price: str):
        self.price = price