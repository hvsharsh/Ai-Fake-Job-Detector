import os
import joblib
from lime.lime_text import LimeTextExplainer
from src.utils import (
    clean_text,
    company_check,
    detect_keywords,
    email_check,
    explanation,
    has_link,
    salary_flag,
    vague_job,
)

# =========================
#  MODEL LOADING
# Loads the trained Scikit-Learn model and Vectorizer safely
# =========================
MODEL_PATH = "models/model.pkl"
VEC_PATH = "models/vectorizer.pkl"

try:
    if os.path.exists(MODEL_PATH) and os.path.exists(VEC_PATH):
        model = joblib.load(MODEL_PATH)
        vectorizer = joblib.load(VEC_PATH)
    else:
        print(" Warning: Models not found. Please train the model first.")
        model, vectorizer = None, None
except Exception as e:
    print(f" Error loading models: {e}")
    model, vectorizer = None, None

# ==========================================
# LIME (EXPLAINABLE AI) SETUP
# Initializes LIME to explain ML predictions word-by-word
# ==========================================
if model and vectorizer:
    explainer = LimeTextExplainer(class_names=['REAL', 'FAKE'])
    # Pipeline function required by LIME to process text before prediction
    def lime_pipeline(texts):
        # LIME ke words ko clean karke model ko dena
        cleaned = [clean_text(t) for t in texts]
        vec = vectorizer.transform(cleaned)
        return model.predict_proba(vec)
else:
    explainer = None

# ==========================================
# MAIN PREDICTION FUNCTION (HYBRID ENGINE)
# Combines ML probability with Rule Engine constraints
# ==========================================
def predict(data):
    text = str(data.get("text", "")).strip()
    salary_input = str(data.get("salary", "")).strip()

    # =========================
    # INPUT VALIDATION
    # =========================
    if not text:
        return {
            "prediction": "INVALID",
            "risk": 0,
            "keywords": [],
            "email_status": "no_data",
            "company_verified": False,
            "company_status": "not_found",
            "has_link": False,
            "explanation": ["Error: Job description is empty"],
        }

    # =========================
    # MISSING MODEL CHECK
    # =========================
    if model is None or vectorizer is None:
        return {
            "prediction": "ERROR",
            "risk": 100,
            "keywords": [],
            "email_status": "error",
            "company_verified": False,
            "company_status": "error",
            "has_link": False,
            "explanation": ["System Error: ML Model missing. Run model_training.ipynb first."],
        }

    # =========================
    # ML PREDICTION
    # =========================
    cleaned_text = clean_text(text)
    vec = vectorizer.transform([cleaned_text])
    prob = model.predict_proba(vec)[0][1]

    # Generate LIME Explanation HTML
    # Gets the top 10 contributing words and formats them into a clean UI container
    try:
        exp = explainer.explain_instance(text, lime_pipeline, num_features=10)
        raw_html = exp.as_html()  
        
        # UI UPGRADE
        lime_html = f"""
        <div style="background-color: #f9f9f9; padding: 25px; border-radius: 12px; color: #222; border: 1px solid #eee;">
            <style>
                div, text, tspan, p, span {{
                    font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif !important;
                }}
            </style>
            {raw_html}
        </div>
        """
    except Exception as e:
        lime_html = "<p>LIME Explanation not available.</p>"

    # =========================
    # RULE SIGNALS
    # Extracts all factual indicators from the text using utils.py
    # =========================
    keywords = detect_keywords(text)
    salary = salary_flag(salary_input)
    email_status = email_check(text)

    company_verified = company_check(text)
    company_status = "verified" if company_verified else "not_found"

    link_flag = has_link(text)
    vague_flag = vague_job(text)

    # Base Explanation list loaded from utils
    explanations_list = explanation(
        keywords, salary, email_status, company_verified, link_flag, vague_flag
    )

    # =========================
    # HYBRID RISK (BALANCED )
    #Base risk is set by ML (50% weight). Rules add or subtract specific penalties.
    # =========================
    risk = prob * 0.5

    # keywords
    risk += min(len(keywords) * 0.05, 0.15)

    # salary
    if salary:
        risk += 0.15

    # email
    if email_status == "free_email":
        risk += 0.20
    elif email_status == "unknown_email":
        risk += 0.10
    elif email_status == "no_email":
        risk += 0.10
    elif email_status == "company_email":
        risk -= 0.10

    # link
    if link_flag:
        risk += 0.10

    # company
    if not company_verified:
        risk += 0.15
    else:
        risk -= 0.15

    # vague job
    if vague_flag:
        risk += 0.15

    # combo rule (IMPORTANT)
    if vague_flag and not company_verified:
        risk += 0.15

    if email_status == "free_email" and not company_verified:
        risk += 0.10

    #  NEW PHISHING RULE: Big Company Name + Free Email = SCAM ALERT
    if company_verified and email_status == "free_email":
        risk += 0.40  
        explanations_list.append(" CRITICAL: Professional company using a free/public email domain.")

    #  ZERO-TOLERANCE FINANCIAL SCAM RULE (Crypto & Fees)
    # Instantly applies a massive penalty if any fee/crypto payment is requested
    text_lower = text.lower()
    scam_words = ["security deposit", "bitcoin", "crypto", "registration fee", "processing fee", "equipment fee"]
    
    for word in scam_words:
        if word in text_lower:
            risk += 0.70  # Override ML probability
            explanations_list.append(f" SCAM ALERT: Mentions '{word}'. Real jobs never ask for money or pay in crypto.")
            break 

    # =========================
    # CLAMP
    # =========================
    risk = max(0.01, min(risk, 1.0))

    # =========================
    # FINAL PREDICTION
    # =========================
    pred = 1 if risk > 0.55 else 0

    return {
        "prediction": "FAKE" if pred else "REAL",
        "risk": int(risk * 100),
        "keywords": keywords,
        "email_status": email_status,
        "company_verified": company_verified,
        "company_status": company_status,
        "has_link": link_flag,
        "lime_html": lime_html, 
        "explanation": explanations_list, #  FIX: Custom explanation list return 
    }

