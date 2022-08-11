from Trait import Trait


class Comp_Trait(Trait):
    def __init__(self, name: str, milestones: list, bonus: list, innate: str = ""):
        super().__init__(name, bonus, innate)
        self.milestones = milestones
