import streamlit as st
import pandas as pd
import re
import os
from supabase import create_client, Client

# -------------------------
# SUPABASE CONFIG
# -------------------------
SUPABASE_URL = "https://vtjpurzleowqhwmftggb.supabase.co"  # your actual URL
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZ0anB1cnpsZW93cWh3bWZ0Z2diIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjMwNzc1MDksImV4cCI6MjA3ODY1MzUwOX0.AyWP7-o0BkATjglzN0INJEAK1EUokSdYaYSU80F7wwM"  # your actual service role key
BUCKET_NAME = "matchday-data"

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# -------------------------
# MAIN FUNCTION: Process + Save + Upload
# -------------------------
def process_and_save_match_data(data, season):
    sections = re.split(r'Matchday \d+', data)
    matchdays = re.findall(r'Matchday (\d+)', data)

    for matchday, section in zip(matchdays, sections[1:]):
        matches = []
        lines = section.strip().split('\n')

        for line in lines:
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
            # -------- LOCAL SAVE --------
            dir_path = f"data/season{season}"
            os.makedirs(dir_path, exist_ok=True)

            file_name = f"matchday_{matchday.zfill(2)}.csv"
            file_path = os.path.join(dir_path, file_name)

            df = pd.DataFrame(matches)
            df.to_csv(file_path, index=False)
            st.write(f"✅ Saved locally → {file_path}")

            # -------- SUPABASE UPLOAD --------
            try:
                with open(file_path, "rb") as f:
                    supabase.storage.from_(BUCKET_NAME).upload(
                        path=f"season{season}/{file_name}",
                        file=f
                    )
                st.success(f"☁️ Uploaded to Supabase → season{season}/{file_name}")
            except Exception as e:
                st.error(f"❌ Upload failed for Matchday {matchday}: {e}")

        else:
            st.error(f"⚠️ No matches found for Matchday {matchday}")


# -------------------------
# STREAMLIT INTERFACE
# -------------------------
st.title("BP Matchday Data Entry")

season = st.text_input("Enter season number here:", key="season")
match_data = st.text_area("Paste the matchday data here:", height=300, key="match_data")

if st.button("✅ Save Data"):
    if match_data.strip() and season.strip():
        process_and_save_match_data(match_data, season)
        st.success("🎉 All matchdays processed and saved successfully.")

        # # Clear fields via rerun
        # st.query_params(clear="1")
    else:
        st.error("🚨 Please fill in both season and match data.")
