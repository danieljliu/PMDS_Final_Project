from Trait import Trait

class Champ_Trait(Trait):
    def __init__(self, value, name: str, bonus = "", innate: str = ""):
        super().__init__(name, bonus, innate)
        self.value = value