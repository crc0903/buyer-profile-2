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

# Scrape likely firm subpages and combine
def scrape_combined_content(base_url, paths=["", "/about", "/team", "/portfolio", "/investments", "/our-team"]):
    combined_text = ""
    for path in paths:
        url = base_url + path
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, 'html.parser')
            text = soup.get_text(separator=' ', strip=True)
            combined_text += f"\n\n--- Content from {url} ---\n" + text[:3000]
        except Exception as e:
            combined_text += f"\n[Failed to fetch {url}: {e}]"
    return combined_text[:12000]

if st.button("Generate Summary") and firm_name:
    with st.spinner("Scraping and generating summary..."):
        base_url = f"https://www.{firm_name.lower().replace(' ', '')}.com"
        website_content = scrape_combined_content(base_url)

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

        user_prompt = f"""Firm: {firm_name}
Employees: {employee_names.strip()}
Investments: {investment_names.strip()}

Scraped Website Content:
{website_content}

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
