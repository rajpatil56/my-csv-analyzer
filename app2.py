
import pandas as pd
import csv
import streamlit as st
from openai import OpenAI

# -----------------------------
# Initialize OpenRouter client
# -----------------------------
API_KEY = # Replace with your key
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=API_KEY
)

# -----------------------------
# Page Config (PC + Mobile)
# -----------------------------
st.set_page_config(
    page_title="CSV AI Analyzer",
    page_icon="📊",
    layout="wide"
)

st.title("📊 AI-Powered CSV Analyzer")
st.markdown("Upload your dataset and ask questions. Works on **PC and Mobile**.")

# -----------------------------
# Helper functions
# -----------------------------
def detect_delimiter(file_obj, encoding='utf-8'):
    file_obj.seek(0)
    sample = file_obj.read(2048).decode(encoding, errors="ignore")
    try:
        dialect = csv.Sniffer().sniff(sample)
        return dialect.delimiter
    except:
        return ','

def load_csv_robust(file_obj):
    file_obj.seek(0)
    try:
        return pd.read_csv(file_obj)
    except:
        for enc in ['latin1', 'cp1252', 'utf-16']:
            try:
                delimiter = detect_delimiter(file_obj, enc)
                file_obj.seek(0)
                return pd.read_csv(file_obj, encoding=enc, delimiter=delimiter)
            except:
                pass
    st.error("❌ Failed to load CSV")
    return None

def get_analysis_code_and_summary(user_prompt, df):
    sample_data = df.head(5).to_string()
    col_info = df.dtypes.to_string()

    prompt = f"""I have a CSV dataset.

Here is a preview of the first 5 rows:
{sample_data}

Column names and types:
{col_info}

User request:
{user_prompt}

Please provide ONLY:
1. Python code using pandas, matplotlib, seaborn for the analysis.
2. A concise written summary of the results.
"""
    completion = client.chat.completions.create(
        model="meta-llama/llama-3.3-70b-instruct:free",
        messages=[{"role": "user", "content": prompt}],
        extra_headers={
            "HTTP-Referer": "https://streamlit.io",
            "X-Title": "CSV Analyzer"
        }
    )
    return completion.choices[0].message.content

# -----------------------------
# Streamlit UI
# -----------------------------
uploaded_file = st.file_uploader("Upload CSV file", type=["csv"])

if uploaded_file:
    df = load_csv_robust(uploaded_file)
    if df is not None:
        st.success("✅ CSV loaded successfully!")
        st.write("### Preview", df.head())

        user_prompt = st.text_area("Enter your analysis request:", placeholder="e.g. Show correlation heatmap")

        if st.button("Analyze with AI"):
            with st.spinner("Analyzing..."):
                try:
                    response = get_analysis_code_and_summary(user_prompt, df)
                    st.subheader("📌 AI Response")
                    st.markdown(response)
                except Exception as e:
                    st.error(f"Error: {e}")
