# 🛡️ AI Fake Job Posting Detector

🚀 **[Live App Demo: Click Here to Test the AI Tool](https://ai-fake-job-detectors.streamlit.app/)**

An advanced, AI-powered web application designed to protect job seekers from employment fraud and phishing scams. This tool uses a **Hybrid Risk Scoring Engine** to instantly analyze job descriptions and detect hidden red flags.

---

## ✨ Key Features
* **Hybrid Intelligence Engine:** Combines Machine Learning (NLP) context analysis with a strict Rule-Based Engine (checking for free emails, fake startup details, and phishing patterns).
* **Smart PDF Parsing:** Automatically extracts text and isolates salary figures from uploaded job offer letters using `pdfplumber` and advanced Regex.
* **Explainable AI (XAI):** Features a scrollable LIME (Local Interpretable Model-agnostic Explanations) chart that provides a transparent "Word Analysis," highlighting exact words that triggered fraud alerts.
* **Interactive UI/UX:** Built with Streamlit, featuring real-time risk gauges (Plotly), live analysis spinners, toast notifications, and celebration animations for safe jobs.
* **Analysis History:** Saves and displays recent job scans for quick reference.

## 🛠️ Technology Stack
* **Language:** Python 3.8+
* **Frontend:** Streamlit, Streamlit Components
* **Machine Learning:** Scikit-Learn (TF-IDF, Classification), LIME (Explainable AI)
* **Data Processing:** Pandas, NumPy, Regex (`re`)
* **Data Visualization:** Plotly Graph Objects

## 💻 How to Run Locally

1. Clone the repository:
   ```bash
   git clone [https://github.com/hvsharsh/Ai-Fake-Job-Detector.git](https://github.com/hvsharsh/Ai-Fake-Job-Detector.git)