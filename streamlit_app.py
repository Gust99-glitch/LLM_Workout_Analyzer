import os
import pandas as pd
import streamlit as st
from supabase import create_client
from dotenv import load_dotenv
load_dotenv()

# Load Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# App UI
st.set_page_config(page_title="Workout Viewer", layout="wide")
st.title("🏋️ Military Fitness Workouts")

# Fetch data
@st.cache_data(ttl=60)
def load_data():
    response = supabase.table("workouts").select("*").order("id", desc=True).execute()
    return pd.DataFrame(response.data)

df = load_data()

if df.empty:
    st.warning("No workout data found.")
else:
    st.dataframe(df, use_container_width=True)

    # Filter by Day
    day = st.selectbox("Choose a day", df["day"].unique())
    st.subheader(f"Workout for {day}")
    st.write(df[df["day"] == day][["title", "workout"]].iloc[0])

    # Simple chart of keyword frequency
    st.subheader("Exercise Frequency")
    keywords = ["pushups", "crunches", "squats", "lunges", "jumping jacks"]
    freq = {kw: df["workout"].str.lower().str.contains(kw).sum() for kw in keywords}
    st.bar_chart(pd.DataFrame.from_dict(freq, orient="index", columns=["count"]))