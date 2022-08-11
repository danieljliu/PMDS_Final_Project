from Champion import Champion
from Champ_Trait import Champ_Trait
from Comp_Trait import Comp_Trait
import csv
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


raw_df = pd.read_csv('data/tft_match_history.csv', low_memory=False)


def convert_str(trait_str, delim):
    lst = []
    for trait in trait_str.split(delim):
        lst.append(Champ_Trait(name = trait[:-1], value=int(trait[-1])))
    return lst


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

                trait = Comp_Trait(name, milestones, bonus, innate)
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
        milestones = trait_dict[trait.name].milestones

        for milestone in milestones:
            if value < int(milestone):
                break
            trait_level += 1

        if trait_level > 0:
            active_traits.append(trait.name.capitalize() + '_' + str(trait_level))
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
        for trait in champ.trait:
            traits[trait] = traits.get(trait, 0) + trait.value

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
    return (pd.DataFrame(pd.concat([df['augment0'], df['augment1'], df['augment2']]), columns=['Augment']).groupby(
        'Augment').value_counts().sort_values(ascending=False)).to_frame().reset_index().rename(
        columns={'index': 'Augment', 0: 'Counts of Appearance'})


def get_champions(df):
    return (pd.DataFrame(
        df[df.columns[df.columns.isin(champ_indices.keys())]].notnull().astype('int')).sum().sort_values(
        ascending=False)).to_frame().reset_index().rename(
        columns={'index': 'Champion', 0: 'Counts of Appearance'})


def get_traits(df):
    return (df.loc[:, 'Set7_Assassin':'Set7_Whispers'].replace(0.0, np.nan).notnull().astype('int').sum().sort_values(
        ascending=False)).to_frame().reset_index().rename(
        columns={'index': 'Trait', 0: 'Counts of Appearance'})


def get_traits_specific(df):
    return df.loc[:, 'Set7_Assassin':'Set7_Whispers'].replace(np.nan, 0.0)

def get_champ_specific(df):
    return df[df.columns[df.columns.isin(champ_indices.keys())]].replace(np.nan, 0.0)

def get_items(df):
    items = df.filter(regex='_item')
    item_list = []

    for col in items:
        for item in items[col]:
            if item:
                item_list.append(item)

    return (pd.Series(item_list).dropna().value_counts().sort_values(ascending=False).drop(
        'None')).to_frame().reset_index().rename(columns={'index': 'Item', 0: 'Counts of Appearance'})


def generate_placement_dfs(placement: int):
    global raw_df

    df = raw_df[raw_df['placement'] <= placement]
    item_df = get_items(df)
    augments_df = get_augments(df)
    champions_df = get_champions(df)
    traits_df = get_traits(df)

    return item_df, augments_df, champions_df, traits_df, len(df)

top_4_item_df, top_4_augments_df, top_4_champions_df, top_4_traits_df, _ = generate_placement_dfs(4)
all_item_df, all_augments_df, all_champions_df, all_traits_df, _ = generate_placement_dfs(8)


def individual_level_counts(df):
    traits = {}
    for col in df:
        for row in df[col]:
            trait = col.split('_')[1].lower()
            if row < 1:
                continue

            traits[trait + str(int(row))] = traits.get(trait + str(int(row)), 0) + 1

    return pd.Series(traits).to_frame().reset_index()


def calculate_winrate(key):
    global raw_df, top_4_item_df, top_4_augments_df, top_4_champions_df, top_4_traits_df, all_item_df, all_augments_df, all_champions_df, all_traits_df

    if key == 'Item':
        top_4_df = top_4_item_df
        all_df = all_item_df
    elif key == 'Augment':
        top_4_df = top_4_augments_df
        all_df = all_augments_df
    elif key == 'Trait':
        top_4_df = individual_level_counts(get_traits_specific(raw_df[raw_df['placement'] <= 4])).rename(
            columns={'index': 'Trait', 0: 'Counts of Appearance'})
        all_df = individual_level_counts(get_traits_specific(raw_df[raw_df['placement'] <= 8])).rename(
            columns={'index': 'Trait', 0: 'Counts of Appearance'})
    else:  # key == Champion
        top_4_df = individual_level_counts(get_champ_specific(raw_df[raw_df['placement'] <= 4])).rename(
            columns={'index': 'Champion', 0: 'Counts of Appearance'})
        all_df = individual_level_counts(get_champ_specific(raw_df[raw_df['placement'] <= 8])).rename(
            columns={'index': 'Champion', 0: 'Counts of Appearance'})

    merged_df = pd.merge(top_4_df, all_df, on=key)
    win_rate = merged_df['Counts of Appearance_x'] / merged_df['Counts of Appearance_y']

    res = pd.DataFrame(zip(merged_df[key], win_rate)).rename(
        columns={0: key, 1: 'Win Rate'}).sort_values(by='Win Rate', ascending=False)

    if key == 'Item':
        res = res.drop(102).reset_index(drop=True)
    return res

def plot_fig(key,df,view):
    fig = plt.figure()
    plt.bar(df[key][:view], df['Counts of Appearance'][:view])
    plt.xticks(rotation=90)
    plt.ylabel('Frequency of Appearance')
    st.pyplot(fig)