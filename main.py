from library import *
import streamlit as st

def main():
    st.set_page_config(layout="wide")
    overview,tier_lists,team_designer,analytics,data = st.tabs(["Overview","Tier Lists", "Team Designer", "Interactive Analytics","Data"])

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
        st.write('Interactive Analytics: Displays interactive charts visualizing the distribution of gameplay variables (champions/traits/augments) '
                 'based on final placement (1st - 8th)')
        st.write("Data: Browse through the data that all the analytics and figures are based off of")

    with tier_lists:
        st.title('Tier Lists')
        st.write('*All tier lists are based off appearance rate in top-4 placing players')

        item_df, augments_df, champions_df, traits_df = generate_placement_dfs(4)



        st.subheader('Champions')
        st.dataframe(champions_df)
        st.subheader('Augments')
        st.dataframe(augments_df)
        st.subheader('Items')
        st.dataframe(item_df)
        st.subheader('Traits')
        st.dataframe(traits_df)


    with team_designer:
        st.title("Team Designer")
        team_designer = st.multiselect(label='Select champions to add to your team',
                                       options=[champ.capitalize() for champ in champ_dict.keys()])
        team,trait_bonuses,bonuses,spaces = display_bonuses(team_designer)
        st.button('Save Team to File',on_click=write_team(team,trait_bonuses,bonuses,spaces))

    with analytics:
        st.title("Interactive Analytics")
        st.pyplot(generate_champ_chart(champions_df))

    with data:
        st.title("Data")
        st.subheader('Challenger TFT Match History - Raw')
        st.dataframe(pd.read_csv('data/tft_match_history.csv',low_memory=False))

        st.subheader('TFT Set 7 Champion Data')
        st.dataframe(pd.read_csv('data/champions.csv'))

        st.subheader('TFT Set 7 Trait Data')
        st.dataframe(pd.read_csv('data/traits.csv', index_col=False,on_bad_lines='skip'))

main()
