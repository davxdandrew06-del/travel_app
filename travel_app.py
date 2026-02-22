import streamlit as st
import sqlite3
from openai import OpenAI

# --- 1. DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('hackathon_travel.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trips 
                 (destination TEXT, style TEXT, plan TEXT)''')
    conn.commit()
    return conn

# --- 2. THE AI BRAIN (System Prompt) ---
SYSTEM_PROMPT = """
You are 'TravelPro AI', a professional travel consultant.
Create a detailed 3-day itinerary based on the user's destination and travel style.
Format with 'Day 1', 'Day 2', and 'Day 3' headers. 
Always include one local food item and one 'Pro Budget Tip'.
"""

# --- 3. BACKEND LOGIC ---
def generate_ai_plan(destination, style):
    # This line pulls the key from your secrets.toml file
    client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Plan a {style} trip to {destination}"}
        ]
    )
    return response.choices[0].message.content

# --- 4. FRONTEND UI ---
st.set_page_config(page_title="TravelPro AI", page_icon="✈️")

st.title("🌍 AI Travel Planner")
st.info("Built for the BCA Hackathon - Problem Solving with AI")

with st.sidebar:
    st.header("Trip Planner")
    dest_input = st.text_input("Destination", placeholder="e.g. Bali")
    style_input = st.selectbox("Style", ["Backpacker", "Luxury", "Adventure"])
    
    if st.button("Generate Plan"):
        if dest_input:
            with st.spinner("Consulting our AI travel experts..."):
                # Run Backend
                itinerary = generate_ai_plan(dest_input, style_input)
                
                # Save to Database
                conn = init_db()
                c = conn.cursor()
                c.execute("INSERT INTO trips VALUES (?, ?, ?)", (dest_input, style_input, itinerary))
                conn.commit()
                
                # Show Result
                st.session_state.current_plan = itinerary
                st.balloons()
        else:
            st.error("Enter a destination!")

# Display the generated plan if it exists
if 'current_plan' in st.session_state:
    st.markdown(st.session_state.current_plan)

# --- 5. DATABASE HISTORY ---
st.divider()
st.subheader("📜 Recently Planned Trips")
conn = init_db()
c = conn.cursor()
c.execute("SELECT * FROM trips ORDER BY rowid DESC LIMIT 5")
for trip in c.fetchall():
    with st.expander(f"📍 {trip[0]} ({trip[1]})"):
        st.write(trip[2])