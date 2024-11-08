import streamlit as st
import pandas as pd
import re
import os

def process_and_save_match_data(data, season):
    # Split the data into sections by "Matchday"
    sections = re.split(r'Matchday \d+', data)
    matchdays = re.findall(r'Matchday (\d+)', data)

    for matchday, section in zip(matchdays, sections[1:]):  # Skip the first split as it's before the first matchday
        matches = []
        lines = section.strip().split('\n')
        for line in lines:
            # Regular expression to extract the football match data
            match = re.match(r'([A-Z]+) - ([A-Z]+)\((\d+) - (\d+)\) (\d+) - (\d+)', line)
            if match:
                team1, team2, ht_team1, ht_team2, ft_team1, ft_team2 = match.groups()
                matches.append({
                    "Home team": team1,
                    "Away team": team2,
                    "Half-Time Home": int(ht_team1),
                    "Half-Time Away": int(ht_team2),
                    "Full-Time Home": int(ft_team1),
                    "Full-Time Away": int(ft_team2)
                })

        if matches:
            # Ensure directory exists
            dir_path = f"data/season{season}"
            os.makedirs(dir_path, exist_ok=True)

            # Save the CSV file
            file_name = f'matchday_{matchday.zfill(2)}.csv'
            file_path = os.path.join(dir_path, file_name)
            df = pd.DataFrame(matches)
            df.to_csv(file_path, index=False)

            st.write(f"Data for Matchday {matchday} saved successfully at {file_path}")
        else:
            st.error(f"No matches found for Matchday {matchday}")

# Streamlit interface setup
st.title("Data Entry Platform")
season = st.text_input("Enter season here:")
match_data = st.text_area("Paste the data here:", height=300)

if st.button('Save Data'):
    if match_data:
        process_and_save_match_data(match_data, season)
        st.success("All matchdays processed and saved successfully.")
    else:
        st.error("Please paste match data including matchdays.")
