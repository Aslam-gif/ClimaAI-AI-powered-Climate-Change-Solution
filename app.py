import streamlit as st
import pandas as pd
import plotly.express as px
from openai import OpenAI

# === YOUR GROQ API KEY HERE ===
GROQ_API_KEY = os.getenv("GROQ_API_KEY")  # Paste your Groq key

client = OpenAI(
    api_key=GROQ_API_KEY,
    base_url="https://api.groq.com/openai/v1"
)

# Page setup
st.set_page_config(page_title="ClimaAI", page_icon="🌍", layout="wide")

st.title("🌍 ClimaAI: AI-Powered Climate Action Advisor")
st.markdown("**Calculate → Chat with lightning-fast generative AI (Groq + Llama)!**")

# Calculator
st.header("1. Calculate Your Carbon Footprint")
col1, col2 = st.columns(2)
with col1:
    transport_miles = st.slider("Annual car miles driven", 0, 30000, 10000)
    flights = st.number_input("Long-haul flights per year", 0, 20, 2)
with col2:
    electricity_kwh = st.slider("Monthly electricity use (kWh)", 0, 2000, 600)
    diet = st.selectbox("Diet type", ["Meat-heavy", "Average", "Vegetarian", "Vegan"])

co2_transport = (transport_miles * 0.404) / 1000
co2_flights = flights * 3.5
co2_electricity = (electricity_kwh * 12) * 0.0004
co2_diet = {"Meat-heavy": 3.3, "Average": 2.5, "Vegetarian": 1.8, "Vegan": 1.4}[diet]
total_co2 = co2_transport + co2_flights + co2_electricity + co2_diet

st.metric("Your Annual Carbon Footprint", f"{total_co2:.1f} tons CO₂e")

chart_data = pd.DataFrame({
    "Category": ["Transport", "Flights", "Electricity", "Diet"],
    "Tons CO₂e": [co2_transport, co2_flights, co2_electricity, co2_diet]
})
fig = px.pie(chart_data, values="Tons CO₂e", names="Category", hole=0.4,
             color_discrete_sequence=px.colors.sequential.Greens)
st.plotly_chart(fig, use_container_width=True)

# Chatbot
st.markdown("---")
st.header("2. 💬 Chat with ClimaAI (Ultra-Fast Generative AI)")

if "messages" not in st.session_state:
    st.session_state.messages = []

if not st.session_state.messages:
    intro = f"""
    Hello! I'm ClimaAI, powered by Groq's lightning-fast AI (Llama model).
    
    Your footprint: **{total_co2:.1f} tons CO₂e/year**
    Breakdown: Transport {co2_transport:.1f}t | Flights {co2_flights:.1f}t | Electricity {co2_electricity:.1f}t | Diet {co2_diet:.1f}t ({diet})
    
    Ask for detailed plans — e.g., "30-day transport reduction plan in India", "Best EV under 15 lakh?", or "Vegan Indian meal ideas".
    """
    st.session_state.messages.append({"role": "assistant", "content": intro})

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("Ask your climate question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # System prompt for personalization
    messages = [
        {"role": "system", "content": f"You are ClimaAI, a motivating climate advisor for India. Be practical, detailed, use ₹ costs, mention subsidies (PM Surya Ghar, FAME), local apps/brands. User's footprint: {total_co2:.1f} tons/year (Transport {co2_transport:.1f}t, Flights {co2_flights:.1f}t, Electricity {co2_electricity:.1f}t, Diet {co2_diet:.1f}t - {diet}). Encourage them!"},
        *st.session_state.messages[-10:],  # Last 10 messages for context
        {"role": "user", "content": prompt}
    ]

    with st.chat_message("assistant"):
        with st.spinner("Thinking super fast..."):
            response = client.chat.completions.create(
                model="llama-3.1-8b-instant",  # Fast & free, or try "llama-3.1-70b-versatile" for smarter
                messages=messages,
                max_tokens=600,
                temperature=0.7
            )
            answer = response.choices[0].message.content
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

st.caption("Powered by Groq + Llama • Built for real impact 🌱")