
import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="PE / Acquirer Summary Tool", layout="centered")
st.title("🔍 PE / Strategic Acquirer Summary Tool")

# Inputs
firm_name = st.text_input("Firm or Strategic Acquirer Name", placeholder="e.g., Thoma Bravo")
employee_names = st.text_area("Optional Employee Names (one per line)", placeholder="Up to 5 names")
investment_names = st.text_area("Optional Investment Names (one per line)", placeholder="Up to 5 investments")

if st.button("Generate Summary") and firm_name:
    with st.spinner("Gathering and generating summary..."):
        system_prompt = """
You are a professional analyst assistant. When given the name of a private equity firm or strategic acquirer, generate:

1. Location of headquarters
2. Estimated number of active investments
3. AUM (Assets Under Management)
4. Most recent fund size and vintage
5. A 4-bullet overview of the firm/acquirer
6. 2-sentence bios for up to 5 employees (if names are provided)
7. 2-sentence descriptions of up to 5 investments (if names are provided)

Also include a confidence level (High, Medium, Low) for Location, Active Investments, AUM, and Fund info.

Prioritize information from the firm's official website. If not available, reference PitchBook summaries or other reputable online sources.

Finally, generate a "Sources" section at the end with footnotes pointing to the URLs of your data (e.g., [1] https://www.thomabravo.com/team).
"""

        user_prompt = f"Firm: {firm_name}\nEmployees: {employee_names.strip()}\nInvestments: {investment_names.strip()}\nGenerate as specified."

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4
        )

        output = response.choices[0].message.content
        st.text_area("📄 Output", output, height=700)
