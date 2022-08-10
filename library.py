from Champion import Champion
from Trait import Trait
import csv
import streamlit as st
import pandas as pd
import numpy as np


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


def load_data():
    with open('data/tft_match_history.csv') as file:
        reader = csv.reader(file)
        header = next(reader)
        tst = next(reader)

        placement = tst[0]

    champs = header[33:]
    champ_indices = {}
    for i in range(len(champs)):
        if i % 4 == 0:
            champ_indices[champs[i]] = i

    champ_dict = initialize_data('champion')
    trait_dict = initialize_data('trait')

    temp = pd.read_csv('data/tft_match_history.csv', low_memory=False)

    champs_df = temp[temp.columns[temp.columns.isin(champ_indices.keys())]]
    return champ_dict, trait_dict, champs_df, champ_indices


champ_dict, trait_dict, champs_df, champ_indices = load_data()


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
            active_traits.append(trait.capitalize() + '_' + str(trait_level))
    return active_traits


def get_trait_bonus(traits):
    bonuses = []

    for trait in traits:
        trait_level = trait[-1]
        bonus_index = int(trait_level) - 1
        trait_name = trait[:-2]

        bonuses.append(trait.capitalize() + ': ' + trait_dict[trait_name.lower()].bonus[bonus_index])

    return bonuses


def display_bonuses(user_input):
    team_container, trait_container, spaces_container, bonus_container = st.empty(), st.empty(), st.empty(), st.empty()
    team = []
    traits = {}

    for champ in user_input:
        champ = champ_dict[champ.lower()]
        team.append(champ.name.capitalize())
        for trait, value in champ.trait.items():
            traits[trait] = traits.get(trait, 0) + value

    spaces = len(team)
    if traits.get('dragon', 0) > 0:
        spaces += traits['dragon']

        # There can only be one Dragon on the board to gain the dragon bonus
        if traits.get('dragon', 0) > 1:
            traits.pop('dragon', None)

    trait_bonuses = calculate_trait_bonus(traits)
    bonuses = get_trait_bonus(calculate_trait_bonus(traits))

    team_container.text('Team: ' + ', '.join(team))
    trait_container.text('Active Traits: ' + ' '.join(trait_bonuses))
    spaces_container.text('Required Spaces: ' + str(spaces))
    bonus_container.text('Bonuses:\n' + '\n'.join(bonuses))

    return team, trait_bonuses, bonuses, spaces


def write_team(team, trait_bonuses, bonuses, spaces):
    with open('output/tft_sample_team.txt', 'w') as fout:
        fout.write('Team: ' + ', '.join(team) + '\n\n')
        fout.write('Active Traits: ' + ' '.join(trait_bonuses) + '\n\n')
        fout.write('Required Spaces: ' + str(spaces) + '\n\n')
        fout.write('Bonuses:\n' + '\n'.join(bonuses))


def get_augments(df):
    return (pd.DataFrame(pd.concat([df['augment0'], df['augment1'], df['augment2']]), columns=['augment']).groupby(
        'augment').value_counts().sort_values(ascending=False) / len(df)).to_frame().reset_index().rename(
        columns={'index': 'Augment', 0: 'Frequency of Appearance'})


def get_champions(df):
    return (pd.DataFrame(
        df[df.columns[df.columns.isin(champ_indices.keys())]].notnull().astype('int')).sum().sort_values(
        ascending=False) / len(df)).to_frame().reset_index().rename(
        columns={'index': 'Champion', 0: 'Frequency of Appearance'})


def get_traits(df):
    return (df.loc[:, 'Set7_Assassin':'Set7_Whispers'].replace(0.0, np.nan).notnull().astype('int').sum().sort_values(
        ascending=False) / len(df)).to_frame().reset_index().rename(
        columns={'index': 'Trait', 0: 'Frequency of Appearance'})


def get_items(df):
    items = df.filter(regex='_item')
    item_list = []

    for col in items:
        for item in items[col]:
            if item:
                item_list.append(item)

    return (pd.Series(item_list).dropna().value_counts().sort_values(ascending=False).drop('None')/len(df)).to_frame().reset_index().rename(columns={'index':'Item',0:'Frequency of Appearance'})


def generate_placement_dfs(placement: int):
    all_data_df = pd.read_csv('data/tft_match_history.csv', low_memory=False)
    df = all_data_df[all_data_df['placement'] <= placement]
    item_df = get_items(df)
    augments_df = get_augments(df)
    champions_df = get_champions(df)
    traits_df = get_traits(df)

    return item_df, augments_df, champions_df, traits_df

def get_total_bonus(df):
    traits = {}
    for col in df:
        for row in df[col]:
            trait = col.split('_')[1].lower()
            if row < 1:
                continue

            traits[trait+str(int(row))] = traits.get(trait+str(int(row)),0) + 1

    return pd.Series(traits)

def generate_champ_chart(df):
    res = pd.DataFrame(df[df.columns[df.columns.isin(champ_indices.keys())]].replace(np.nan, 0.0))

    return