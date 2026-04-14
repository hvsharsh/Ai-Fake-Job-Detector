# AI Fake Job Posting Detector

A Machine Learning web application designed to protect job seekers from fake employment scams using Natural Language Processing (NLP) and a Rule-Based Engine.

## How It Works
* **Smart PDF Parsing:** Upload a Job Offer PDF, and the system automatically extracts the text and auto-fills the details using Regex.
* **AI Word Analysis:** The model analyzes the job description to find suspicious words that scammers normally use.
* **Hybrid Risk Scoring:** The system checks for free email domains (like @gmail.com for HR), unverified companies, and suspicious requests (like asking for security deposits) to give a final Fake/Real score.
* **Interactive Dashboard:** A clean, easy-to-use user interface built with Streamlit.

## Tech Stack Used
* **Frontend:** Streamlit, Plotly (For the Risk Meter Gauge)
* **Backend & Machine Learning:** Python, Scikit-Learn, Pandas
* **Text Processing:** pdfplumber, Regular Expressions (Regex)

## Developed By
**Harshvardhan Singh** B.Tech 4th Year, AKTU | AI/ML Enthusiast