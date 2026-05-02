import re
# ==========================================
# CONSTANTS & KEYWORD LISTS
# Define the keywords used by the Rule Engine
# ==========================================

# Words commonly used by scammers to lure candidates
SUSPICIOUS = [
    "easy money", "quick money", "no experience",
    "earn fast", "click here", "urgent hiring",
    "telegram", "whatsapp message", "crypto", 
    "investment required", "registration fee"
]

# Words that indicate a non-specific or low-quality job posting
VAGUE_WORDS = [
    "work from home", "data entry", "online job",
    "part time job", "earn daily", "flexible hours",
    "unlimited earning"
]

# Common free email domains (professional companies rarely use these for HR)
FREE_EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com"
]

# A sample list of well-known, verified companies
KNOWN_COMPANIES = [
    "tcs", "infosys", "wipro", "google", "amazon", "microsoft"
]

# ==========================================
# HELPER FUNCTIONS (TEXT PROCESSING & RULES)
# ==========================================

# Cleans the input text by removing special characters and converting to lowercase
# This makes it easier for the ML model to process the text

def clean_text(text):
    if not isinstance(text, str):
        return ""
    return re.sub(r'[^a-z0-9 ]', '', text.lower())

# Checks if the job description contains any high-risk suspicious keywords
def detect_keywords(text):
    text = text.lower()
    return [k for k in SUSPICIOUS if k in text]

# Checks if the job description sounds vague or unprofessional
def vague_job(text):
    text = text.lower()
    return any(v in text for v in VAGUE_WORDS)

# Analyzes the salary string to detect unrealistic figures
# Flags the job if the maximum salary is unusually high (> 20L) or the gap is too large
def salary_flag(salary):
    if not salary:
        return False
    salary = salary.replace(",", "")
    nums = list(map(int, re.findall(r'\d+', salary)))

    if len(nums) >= 2:
        low, high = nums[0], nums[1]
        if high > 2000000 or (high - low) > 1000000:
            return True

    return False

# Extracts email addresses from the text and categorizes them
# Returns 'free_email', 'company_email', 'unknown_email', or 'no_email'
def email_check(text):
    emails = re.findall(
        r'[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+',
        text
    )

    if not emails:
        return "no_email"

    raw_domain = emails[0].split("@")[1].lower()
    domain = raw_domain.rstrip('.')

    if domain in FREE_EMAIL_DOMAINS:
        return "free_email"

    if any(c in domain for c in KNOWN_COMPANIES):
        return "company_email"

    return "unknown_email"

# Verifies if the company name is recognized or contains registered entity tags (Pvt, Ltd, Inc)
# Uses regex \b to ensure exact word matches (e.g., 'tcs' not 'matchtcs')
def company_check(text):
    text = text.lower()

    # New code: \b ensures exact word match
    if any(re.search(rf'\b{c}\b', text) for c in KNOWN_COMPANIES):
        return True

    if any(re.search(rf'\b{word}\b', text) for word in ["pvt", "ltd", "private limited", "inc"]):
        return True

    return False

# Checks if the text contains any external web links (http/https)
def has_link(text):
    return bool(re.search(r'http[s]?://', text))

# Generates a human-readable list of explanations based on triggered rules
# This helps the user understand WHY a job was flagged
def explanation(keywords, salary, email_status, company_verified, link_flag, vague_flag):
    reasons = []

    if keywords:
        reasons.append("Suspicious keywords found")

    if salary:
        reasons.append("Unrealistic salary")

    if email_status == "free_email":
        reasons.append("Using free email domain")

    if email_status == "unknown_email":
        reasons.append("Unknown email domain")

    if email_status == "no_email":
        reasons.append("No email provided")

    if not company_verified:
        reasons.append("Company not identifiable")

    if link_flag:
        reasons.append("Contains external link")

    if vague_flag:
        reasons.append("Vague job description")

    if not reasons:
        reasons.append("Looks legitimate")

    return reasons

