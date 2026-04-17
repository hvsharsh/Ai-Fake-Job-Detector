import os
import sys
import time  # ADDED: For UI animation sleep timer
import pandas as pd
import streamlit as st
import plotly.graph_objects as go  
import streamlit.components.v1 as components 
import pdfplumber
import re 

# Add source directory to system path for local imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.predictor import predict


# =========================
# CONFIG
# Set page layout and history file path
# =========================
st.set_page_config(page_title="AI Fake Job Detector", layout="wide")

BASE_DIR = os.path.dirname(__file__)
HISTORY_FILE = os.path.join(BASE_DIR, "history.csv")

# ==========================================
# SESSION STATE MANAGEMENT
# Required to auto-fill text boxes when a PDF is uploaded
# ==========================================
if "job_text" not in st.session_state:
    st.session_state.job_text = ""
if "salary_text" not in st.session_state: 
    st.session_state.salary_text = ""

# =========================
# UI HEADER
# =========================
st.title("🤖 AI Fake Job Detector")
st.markdown("---")

# =========================
# FEATURE: PDF UPLOADER
# Allows users to upload a PDF. Extracts text and isolates salary figures.
# =========================
st.write("### Upload Job Offer / JD (Optional)")
uploaded_file = st.file_uploader("Upload your job description PDF, and let the AI do the reading!", type=["pdf"])

if uploaded_file is not None:
    try:
        # Extract raw text from all pages of the PDF
        with pdfplumber.open(uploaded_file) as pdf:
            extracted_text = ""
            for page in pdf.pages:
                text_content = page.extract_text()
                if text_content:
                    extracted_text += text_content + "\n"

        # Regex Pattern to intelligently find salary-related text
        salary_pattern = r"(?i)salary(?:\s+range)?\s*[:\-]?\s*(.*)"
        salary_match = re.search(salary_pattern, extracted_text)

        if salary_match:
            # Route matched salary text to the Salary input box state
            st.session_state.salary_text = salary_match.group(1).strip()
            # Remove the salary line from the main text to avoid duplication in the JD box
            extracted_text = re.sub(salary_pattern, "", extracted_text).strip()
        else:
            st.session_state.salary_text = ""

        # Route the remaining text to the Job Description input box state
        st.session_state.job_text = extracted_text
        st.success("Text successfully extracted from PDF! Neeche text box mein auto-fill ho gaya hai.")
    except Exception as e:
        st.error(f" Error reading PDF: {e}")

st.markdown("---")

# =========================
# INPUT FIELDS
# Tied to session_state to allow both manual typing and PDF auto-filling
# =========================

text = st.text_area(" Job Description", value=st.session_state.job_text, height=200)
salary = st.text_input(" Salary Range", value=st.session_state.salary_text)

# Update session state if the user manually modifies the text boxes
if text != st.session_state.job_text:
    st.session_state.job_text = text
if salary != st.session_state.salary_text:
    st.session_state.salary_text = salary

# =========================
# ANALYZE BUTTON
# =========================
if st.button(" Analyze Job"):
    
    if not text.strip():
        st.warning(" Please enter a job description before analyzing.")
    else:
        # UX IMPROVEMENT: Adding a spinner for a "Live AI" feel
        with st.spinner("🤖 AI Brain is analyzing text and scanning for fraud patterns..."):
            time.sleep(1.5)  # Pause for dramatic UX effect
            # Call the backend ML pipeline
            res = predict({"text": text, "salary": salary})
            
        # UX IMPROVEMENT: Success toast notification
        st.toast("Analysis Complete!", icon="✅")
        
        # UX IMPROVEMENT: Celebration balloons if the job is highly safe
        if res["risk"] < 20:
            st.balloons()
            
        st.markdown("---")
        # Define a 2-column layout for the results dashboard
        col1, col2 = st.columns([1.5, 1])

        # =========================
        # RIGHT COLUMN: Risk Meter & Final Result
        # =========================
        with col2:
            st.subheader("Final Result")
            if res["risk"] > 70:
                st.error(f"FAKE ({res['risk']}%)")
            elif res["risk"] > 40:
                st.warning(f" SUSPICIOUS ({res['risk']}%)")
            else:
                safe_score = 100 - res["risk"]
                st.success(f" REAL ({safe_score}% Safe)")

            # Render an interactive Plotly Gauge chart
            fig = go.Figure(go.Indicator(
                mode="gauge+number",
                value=res["risk"],
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': "Risk Meter", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "darkblue"},
                    'bar': {'color': "black"},
                    'bgcolor': "white",
                    'borderwidth': 2,
                    'bordercolor': "gray",
                    'steps': [
                        {'range': [0, 40], 'color': "#00cc96"},   
                        {'range': [40, 70], 'color': "#ffa15a"},   
                        {'range': [70, 100], 'color': "#ef553b"}   
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': res["risk"]
                    }
                }
            ))
            st.plotly_chart(fig, use_container_width=True)

        # =========================
        # LEFT COLUMN: Explanations & LIME
        # =========================
        with col1:
            # Display Company and Email verification status via Metric cards
            m1, m2 = st.columns(2)
            m1.metric(label=" Email Status", value=res["email_status"].replace("_", " ").title())
            m2.metric(label=" Company Status", value=res["company_status"].replace("_", " ").title())
            
            # UX IMPROVEMENT: Changed heading from "Rule Engine" to user-friendly text
            st.write("### 🔍 Risk Factors Detected") 
            for r in res["explanation"]:
                st.write(f"- {r}")
                
            # Render the HTML from the LIME explainer    
            st.write("### 🧠 AI Brain (Word Analysis)")
            st.markdown("*Transparency Report: Words highlighted in **Red** indicate fraud risk, while **Green** indicates legitimacy.*")
            components.html(res["lime_html"], height=350, scrolling=True)


        # =========================
        # SAVE HISTORY 
        # Appends the latest result to a local CSV file
        # =========================
        try:
            new_row = pd.DataFrame([{
                "prediction": res["prediction"],
                "risk": res["risk"],
                "email": res["email_status"],
                "company": res["company_status"]
            }])

            if os.path.exists(HISTORY_FILE):
                old_df = pd.read_csv(HISTORY_FILE)
                updated_df = pd.concat([old_df, new_row], ignore_index=True)
            else:
                updated_df = new_row

            updated_df.to_csv(HISTORY_FILE, index=False)

        except Exception as e:
            st.error(f" History save error: {e}")

st.markdown("---")

# =========================
# HISTORY EXPANDER
# Allows users to view and clear their recent scans
# =========================
with st.expander(" View Analysis History"):
    if os.path.exists(HISTORY_FILE):
        hist = pd.read_csv(HISTORY_FILE)
        st.dataframe(hist.tail(5), use_container_width=True)
        # Clear history functionality
        if st.button(" Clear History"):
            os.remove(HISTORY_FILE)
            st.rerun()
    else:
        st.info("No history yet")
        