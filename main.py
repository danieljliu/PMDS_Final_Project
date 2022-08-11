from library import *
import streamlit as st

df = pd.read_csv('data/tft_match_history.csv', low_memory=False)


def main():
    st.set_page_config(layout="wide")
    overview, tier_lists, analytics, team_designer, data = st.tabs(
        ["Overview", "Tier Lists", "Interactive Analytics", "Team Designer", "Data"])

    with overview:
        st.title("TFT-lytics")
        st.subheader("PMDS Final Project Submission by Daniel Liu")
        st.write('TFT-Lytics is a Streamlit data app that uses competitive '
                 'TFT match data to generate analyses ranking the different champions and traits in competitive use. '
                 'There is also a team-picker function so that you can try different combinations of champions and '
                 'the resulting bonuses.')
        st.subheader('Overview of Sections:')
        st.write('Tier Lists: View lists of champions/traits/augments/items ranked by appearance in winning games')
        st.write('Team Designer: View lists of champions/traits/augments/items ranked by appearance in winning games')
        st.write(
            'Interactive Analytics: Displays interactive charts visualizing the distribution of gameplay variables (champions/traits/augments) '
            'based on final placement (1st - 8th)')
        st.write("Data: Browse through the data that all the analytics and figures are based off of")

    with tier_lists:
        st.title('Tier Lists')
        st.write('*All tier lists are based off win-rate in top-4 placing players')
        st.write(
            '**Win rate is calculated by the number of times a champion/item/augment/trait is seen in a winning placement divided '
            'by the number of times it is seen overall, regardless of placement')

        st.subheader('Champions')
        st.dataframe(calculate_winrate('Champion'))

        st.subheader('Items')
        st.dataframe(calculate_winrate('Item'))

        st.subheader('Augments')
        st.dataframe(calculate_winrate('Augment'))

        st.subheader('Traits')
        st.dataframe(calculate_winrate('Trait'))

    with analytics:
        st.title("Interactive Analytics")
        st.write(
            'Select a placement level to view charts of the various distributions of gameplay variables at different placements')

        placement = st.selectbox('Select placement level', options=range(1, 9))
        view = st.selectbox('Select how many entries to show', options=range(5, 20, 5))

        item_df, augments_df, champions_df, traits_df, df_len = generate_placement_dfs(placement)
        item_df['Counts of Appearance'] = item_df['Counts of Appearance'] / df_len
        augments_df['Counts of Appearance'] = augments_df['Counts of Appearance'] / df_len
        champions_df['Counts of Appearance'] = champions_df['Counts of Appearance'] / df_len
        traits_df['Counts of Appearance'] = traits_df['Counts of Appearance'] / df_len

        st.subheader('Champions')
        plot_fig('Champion', champions_df, view)

        st.subheader('Augments')
        plot_fig('Augment', augments_df, view)

        st.subheader('Items')
        plot_fig('Item', item_df, view)

        st.subheader('Traits')
        plot_fig('Trait', traits_df, view)

    with team_designer:
        st.title("Team Designer")
        team_designer = st.multiselect(label='Select champions to add to your team',
                                       options=[champ.capitalize() for champ in champ_dict.keys()])
        team, trait_bonuses, bonuses, spaces = display_bonuses(team_designer)
        st.button('Save Team to File', on_click=write_team(team, trait_bonuses, bonuses, spaces))

    with data:
        st.title("Data")
        st.subheader('Challenger TFT Match History - Raw')
        st.dataframe(pd.read_csv('data/tft_match_history.csv', low_memory=False))

        st.subheader('TFT Set 7 Champion Data')
        st.dataframe(pd.read_csv('data/champions.csv'))

        st.subheader('TFT Set 7 Trait Data')
        st.dataframe(pd.read_csv('data/traits.csv', index_col=False, on_bad_lines='skip'))


main()
