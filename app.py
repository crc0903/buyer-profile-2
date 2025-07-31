import streamlit as st
from openai import OpenAI
import requests
from bs4 import BeautifulSoup

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(page_title="PE / Acquirer Summary Tool", layout="centered")
st.title("🔍 PE / Strategic Acquirer Summary Tool")

# Inputs
firm_name = st.text_input("Firm or Strategic Acquirer Name", placeholder="e.g., Thoma Bravo")
firm_url = st.text_input("Firm Website (optional)", placeholder="e.g., https://www.thomabravo.com")
employee_names = st.text_area("Optional Employee Names (one per line)", placeholder="Up to 5 names")
investment_names = st.text_area("Optional Investment Names (one per line)", placeholder="Up to 5 investments")

# Smart subpage scraping with HEAD check
def scrape_valid_pages(base_url, paths):
    content_sections = []
    for path in paths:
        full_url = base_url.rstrip('/') + path
        try:
            head = requests.head(full_url, timeout=5)
            if head.status_code == 200:
                response = requests.get(full_url, timeout=10)
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text(separator=' ', strip=True)
                cleaned = clean_text(text)
                content_sections.append(f"--- Content from {full_url} ---\n{cleaned[:3000]}")
        except Exception:
            continue
    return "\n\n".join(content_sections)

# Clean out nav/footer fluff
def clean_text(text):
    junk_phrases = ["accept cookies", "subscribe", "search", "privacy policy", "terms of use"]
    lines = text.splitlines()
    return "\n".join([line.strip() for line in lines if line and all(jp not in line.lower() for jp in junk_phrases)])

if st.button("Generate Summary") and firm_name:
    with st.spinner("Scraping firm pages and generating summary..."):
        base_url = firm_url if firm_url else f"https://www.{firm_name.lower().replace(' ', '')}.com"
        subpages = ["/", "/about", "/team", "/leadership", "/portfolio", "/investments", "/strategy"]
        structured_text = scrape_valid_pages(base_url, subpages)

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

Use only the clearly marked website content sections below. If a section isn't included, do not speculate. End with a "Sources" section listing URLs cited.
"""

        user_prompt = f"""Firm: {firm_name}
Employees: {employee_names.strip()}
Investments: {investment_names.strip()}

Scraped Website Content:
{structured_text}

Generate as specified.
"""

        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.4
        )

        output = response.choices[0].message.content
        st.text_area("📄 Output", output, height=700)
