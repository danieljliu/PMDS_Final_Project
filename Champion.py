class Champion:
    def __init__(self, name: str, trait: dict, cost: int):
        self.name = name
        self.trait = trait
        self.cost = cost

    def __str__(self):
        return '{name} {trait} {cost}'.format(
            name=self.name,
            trait=self.trait,
            cost=self.cost
        )

    def __repr__(self):
        return self.__str__()