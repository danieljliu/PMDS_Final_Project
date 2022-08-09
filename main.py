from library import initialize_data
import csv
import pandas
import streamlit as st


with open('data/tft_match_history.csv') as file:
    reader = csv.reader(file)
    header = next(reader)
    tst = next(reader)

    placement = tst[0]

# print(header[33:])
champs = header[33:]
champ_indices = {}
for i in range(len(champs)):
    if i % 4 == 0:
        champ_indices[champs[i]] = i

#print(champ_indices)
#print(len(champ_indices.keys()))

champ_dict = initialize_data('champion')
trait_dict = initialize_data('trait')

temp = pandas.read_csv('data/tft_match_history.csv',low_memory=False)

champs_df = temp[temp.columns[temp.columns.isin(champ_indices.keys())]]



def calculate_trait_bonus(traits):
    active_traits = []
    for trait, value in traits.items():
        trait_level = 0
        milestones = trait_dict[trait].milestones

        for milestone in milestones:
            if value < int(milestone):
                break
            trait_level += 1

        if trait_level > 0:
            active_traits.append(trait + 'lvl' + str(trait_level))
    return active_traits

def test():
    team = []
    traits = {}
    user_input = input("Enter a champion: ")
    if user_input == "quit":
        team = []
        names = []

    if champ_dict.get(user_input,0) == 0:
        print("Not a champion, try re-entering the name")

    champ = champ_dict[user_input]
    team.append(champ.name)
    for trait, value in champ.trait.items():
        traits[trait] = traits.get(trait,0) + value

    print('Team: ' + ' '.join(team))
    print('Active Traits: ' + ' '.join(calculate_trait_bonus(traits)))

def main():
    st.title("TFT-lytics")
    st.subheader("Final Project Submission by Daniel Liu")
    menu = ["Tier List", "Computer Vision"]
    choice = st.sidebar.selectbox("Menu", menu)

main()