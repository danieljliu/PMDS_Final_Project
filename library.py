from Champion import Champion
from Trait import Trait
import csv

def convert_str(trait_str, delim):
    dic = {}
    for trait in trait_str.split(delim):
        dic[trait[:-1]] = int(trait[-1])

    return dic


def initialize_data(type):
    data_dict = {}
    file_path = 'data/champions.csv' if type == 'champion' else 'data/traits.csv'

    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        header = next(reader)

        for col in reader:
            if type == "champion":
                name = col[0]
                traits = convert_str(col[1], ' ')
                cost = int(col[2])

                champ = Champion(name, traits, cost)

                data_dict[name] = champ

            elif type == "trait":
                name = col[0]
                milestones = col[1].split(' ')
                bonus = col[2].split('/')
                innate = col[3]

                trait = Trait(name, milestones, bonus, innate)
                data_dict[name] = trait

    return data_dict