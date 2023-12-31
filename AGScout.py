import streamlit as st
import pandas as pd
import numpy as np
from googlesearch import search


# Assuming 'df' is your DataFrame
df = pd.read_csv("https://drive.google.com/file/d/19uKAvinaof-210NlmFS1uL4kyKZ4SpJv/view?usp=sharing")
df['UID'] = range(1, len(df) + 1)

def namesearch(name):
    id = df[(df['short_name'] == name) | (df['long_name'] == name)][['UID','player_id','long_name','age','nationality_name','player_positions','overall','potential','club_name','fifa_version']]
    return id

def clubname(name, year):
    cn = df[(df['club_name'] == name) &  (df['fifa_version'] == year)][['UID','short_name','age','overall','player_positions','club_position','club_jersey_number','nationality_name']]
    return cn

def get_similar_players(player_id, age_range=None, nationality=None, year=None):
    fdf = df[df['UID'] == player_id]

    overall = fdf['overall'].values[0]
    position = fdf['player_positions'].values[0]
    potential = fdf['potential'].values[0]

    # Filter based on additional criteria
    filtered_df = df[(df['overall'] >= overall - 2) & (df['overall'] < overall + 3) & (df['player_positions'] == position)]



    similar_data = filtered_df.sort_values('potential', ascending=False)
    num_rows = len(similar_data)

    np.random.seed(123)
    
    # Check if player_row is empty
    if len(similar_data[similar_data['UID'] == player_id]) == 0:
        print("Player not found.")
        return pd.DataFrame()

    player_row = similar_data[similar_data['UID'] == player_id].iloc[0]
    other_rows = similar_data[similar_data['UID'] != player_id].sample(n=int(num_rows) - 1)

    columns_to_diff = ['pace', 'shooting', 'passing', 'dribbling', 'defending', 'physic',
                       'attacking_crossing', 'attacking_finishing', 'attacking_heading_accuracy',
                       'attacking_short_passing', 'attacking_volleys', 'skill_dribbling', 'skill_curve',
                       'skill_fk_accuracy', 'skill_long_passing', 'skill_ball_control', 'movement_acceleration',
                       'movement_sprint_speed', 'movement_agility', 'movement_reactions', 'movement_balance',
                       'power_shot_power', 'power_jumping', 'power_stamina', 'power_strength', 'power_long_shots',
                       'mentality_aggression', 'mentality_interceptions', 'mentality_positioning', 'mentality_vision',
                       'mentality_penalties', 'mentality_composure', 'defending_marking_awareness',
                       'defending_standing_tackle', 'defending_sliding_tackle']

    # Calculate differences for each column
    diffs = {}
    for column in columns_to_diff:
        diffs[column] = other_rows[column] - player_row[column]

    names = other_rows['short_name']
    uid = other_rows['UID']
    age = other_rows['age']
    club = other_rows['club_name']
    nat = other_rows['nationality_name']
    ovr = other_rows['overall']
    pot = other_rows['potential']
    uid = other_rows['UID']
    ver = other_rows['fifa_version']

    data = {'Name': names,
            'UID': uid,
            'Age': age,
            'Club Name': club,
            'Nationality': nat,
            'OVR': ovr,
            'POT': pot,
            'Year': ver}
    data.update(diffs)

    # Create a new DataFrame
    new_df = pd.DataFrame(data)
    new_df['Similarity'] = new_df.iloc[:, 7:].abs().sum(axis=1)
    new_df['Similarity'] = new_df['Similarity'] / 34
    new_df['Similarity'] = 100 - new_df['Similarity']
    sorted_new_df = new_df.sort_values('Similarity', ascending=False)

    # Filter sorted_new_df based on the desired criteria
    if age_range:
        sorted_new_df = sorted_new_df[(sorted_new_df['Age'] >= age_range[0]) & (sorted_new_df['Age'] <= age_range[1])]

    if nationality:
        sorted_new_df = sorted_new_df[sorted_new_df['Nationality'] == nationality]
   
    if year:
        sorted_new_df = sorted_new_df[sorted_new_df['Year'] == year]        

    return sorted_new_df[['UID', 'Name', 'Age', 'Year', 'Club Name', 'Nationality', 'OVR', 'POT', 'Similarity']]


def playerdetails(player_id):
    # Use .loc to access the specific row based on the player_id
    player_row = df.loc[df['UID'] == player_id]

    # Check if the player_id exists in the DataFrame
    if player_row.empty:
        return f"No player found with ID: {player_id}"

    # Access the 'player_url' column from the selected row
    player_url = player_row['player_url'].values[0]
    base_url='https://sofifa.com'

    if "http" in player_url:  # Check if the URL is valid
             return player_url
    else:
        player_url = f"https://sofifa.com{player_url}"
        return player_url

def transfermrkt_profile(player_id):
    player_name = df.loc[df['UID'] == player_id, 'long_name'].values[0]
    sentence = f"{player_name} transfermrkt"
    try:
        # Perform the Google search and get the first link
        search_results = search(sentence, num_results=1)
        first_link = next(search_results, None)

        if first_link:
            return first_link
        else:
            return "No results found."

    except Exception as e:
        return f"Error: {str(e)}"

def welcome_page():
    st.title("AGScout - Welcome")
    st.write("Welcome to AGScout, your tool for exploring FIFA player data!")
    st.write("Navigate through the sidebar options to search for players and discover similar players.")
    st.write("Developed by Arijit Goswami, based on EA sports ratings 16-24")


def main():
    st.set_page_config(page_title="AGScout", page_icon="⚽")

    # Display the welcome page by default
    welcome_page()

    st.title("Find Similar Players")

    # Sidebar for Name and Club Search
    st.sidebar.header("Search Options")
    search_option = st.sidebar.radio("Select Search Option", ["Name Search", "Club Search"])

    if search_option == "Name Search":
        name_input = st.sidebar.text_input("Enter player name:")
        name_search_button = st.sidebar.button("Search Name", key="name_search_button")
        if name_search_button:
            result = namesearch(name_input)
            st.write(result)

    elif search_option == "Club Search":
        club_input = st.sidebar.text_input("Enter club name:")
        year_input = st.sidebar.text_input("Enter FIFA version (e.g., 22):")
        club_search_button = st.sidebar.button("Search Club", key="club_search_button")
        if club_search_button:
            result = clubname(club_input, int(year_input))
            st.write(result)

    # Similar Players on the right side
    st.sidebar.subheader("Similar Players")
    player_id_input = st.sidebar.number_input("Enter player UID:")
    age_range_input = st.sidebar.slider("Select Age Range", min_value=16, max_value=40, step=1, value=(16, 40))
    nationality_input = st.sidebar.text_input("Enter Nationality:")
    year_input = st.sidebar.text_input("Enter Year:")

    similar_players_button = st.sidebar.button("Search Similar Players", key="similar_players_button")
    year_filter = int(year_input) if year_input.strip().isdigit() else None
    if similar_players_button:
        result = get_similar_players(player_id_input, age_range=age_range_input,
                                     nationality=nationality_input, year=year_filter)
        st.write(result)

    # Player Details and Navigation to Player's URL
    st.sidebar.subheader("Player Details")
    player_id_details_input = st.sidebar.number_input("Enter player UID:", key="player_id_details_input")
    player_details_button = st.sidebar.button("Get Player Details", key="player_details_button")
    if player_details_button:
        player_url = playerdetails(player_id_details_input)
        if "http" in player_url:
            st.markdown(f"[Open Player Details]({player_url})")

    # Transfermarkt Profile Search
    st.sidebar.subheader("Transfermarkt Profile")
    transfermarkt_player_id_input = st.sidebar.number_input("Enter player UID for Transfermarkt Profile:", key="transfermarkt_player_id_input")
    transfermarkt_profile_button = st.sidebar.button("Get Transfermarkt Profile", key="transfermarkt_profile_button")
    
    if transfermarkt_profile_button:
        transfermarkt_link = transfermrkt_profile(transfermarkt_player_id_input)
        if "http" in transfermarkt_link:
            st.markdown(f"[Open Transfermarkt Profile]({transfermarkt_link})")
        else:
            st.write(transfermarkt_link)

if __name__ == "__main__":
    main()

