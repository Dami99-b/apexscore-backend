from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import random, uuid, datetime, re
from datetime import timedelta

app = FastAPI(title="ApexScore API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- CONSTANTS --------------------

COUNTRIES = {
    "Nigeria": {
        "code": "+234",
        "currency": "NGN",
        "symbol": "₦",
        "banks": ["GTBank", "Access Bank", "First Bank", "Sterling Bank", "UBA", "Opay", "Moniepoint MFB", "PalmPay", "Kuda"],
        "isps": ["MTN", "Airtel", "Glo", "9mobile"],
        "cities": ["Lagos", "Ibadan", "Abeokuta", "Benin City", "Onitsha"],
        "android_models": ["Tecno Spark", "Infinix Hot", "Samsung A14", "Xiaomi Redmi"],
        "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]
    },
    "USA": {
        "code": "+1",
        "currency": "USD",
        "symbol": "$",
        "banks": ["Chase", "Bank of America", "Wells Fargo", "Capital One"],
        "isps": ["Verizon", "AT&T", "T-Mobile"],
        "cities": ["New York", "Houston", "Chicago", "Dallas", "Los Angeles"],
        "android_models": ["Samsung Galaxy", "Google Pixel", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14"]
    },
    "UK": {
        "code": "+44",
        "currency": "GBP",
        "symbol": "£",
        "banks": ["Barclays", "HSBC", "NatWest", "Monzo", "Revolut"],
        "isps": ["Vodafone", "O2", "EE"],
        "cities": ["London", "Manchester", "Birmingham", "Leeds"],
        "android_models": ["Samsung Galaxy", "Google Pixel"],
        "ios_models": ["iPhone 13", "iPhone 14"]
    }
}

FIRST_NAMES = ["Michael", "David", "Blessing", "Fatima", "Esther", "Joseph", "Daniel", "Grace", "Amara"]
LAST_NAMES = ["Anderson", "Brown", "Okoye", "Hassan", "Adeyemi", "Johnson"]
MIDDLE_NAMES = ["James", "Paul", "Grace", "Anne", "Marie"]
JOBS = ["Trader", "Farmer", "POS Agent", "Driver", "Vendor", "Tailor", "Teacher", "Nurse"]

LOAN_PURPOSES = ["Business", "Education", "Medical", "Rent", "Inventory", "Equipment"]
REPAYMENT_STATUS = ["Paid On Time", "Paid Early", "Paid Late", "Defaulted", "Restructured", "Active"]
VALID_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]

DATABASE = {}

# -------------------- HELPERS --------------------

def is_valid_email(email: str) -> bool:
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(pattern, email):
        return False
    return email.split("@")[1].lower() in VALID_EMAIL_DOMAINS

def generate_email(fn, ln):
    return f"{fn.lower()}{ln.lower()}{random.randint(10,999)}@{random.choice(VALID_EMAIL_DOMAINS)}"

def calculate_bsi_scores(has_defaults, sim_verified):
    location = random.randint(70, 95) if not has_defaults else random.randint(40, 65)
    device = random.randint(70, 95) if not has_defaults else random.randint(40, 65)
    sim = random.randint(75, 95) if sim_verified else random.randint(20, 45)
    return location, device, sim

def calculate_apex_score(bsi_l, bsi_d, bsi_s, outstanding, history):
    bsi_avg = (bsi_l + bsi_d + bsi_s) / 3
    score = bsi_avg * 0.6

    if history:
        paid = sum(1 for l in history if l["status"] in ["Paid On Time", "Paid Early"])
        total = len(history)
        repayment_rate = paid / total
        score += repayment_rate * 40

    if outstanding > 80000:
        score -= 15
    elif outstanding > 50000:
        score -= 10
    elif outstanding > 30000:
        score -= 5

    return max(35, min(95, int(score)))

def generate_loan_history(n, banks, currency, symbol):
    history = []
    base = datetime.datetime.utcnow() - timedelta(days=1500)

    for _ in range(n):
        amount = random.randint(500, 50000)
        status = random.choice(REPAYMENT_STATUS)
        history.append({
            "loan_id": uuid.uuid4().hex[:10],
            "institution": random.choice(banks),
            "amount": amount,
            "currency": currency,
            "currency_symbol": symbol,
            "purpose": random.choice(LOAN_PURPOSES),
            "status": status,
            "repayment_amount": amount + int(amount * 0.15) if status.startswith("Paid") else None
        })
    return history

def generate_applicant(email=None):
    country = random.choice(list(COUNTRIES))
    c = COUNTRIES[country]

    fn = random.choice(FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    mid = random.choice(MIDDLE_NAMES)

    if not email:
        email = generate_email(fn, ln)

    history = generate_loan_history(random.randint(4, 8), c["banks"], c["currency"], c["symbol"])
    has_defaults = any(l["status"] == "Defaulted" for l in history)
    outstanding = sum(l["amount"] for l in history if l["status"] in ["Active", "Defaulted"])

    sim_verified = random.choice([True, True, True, False])
    bsi_l, bsi_d, bsi_s = calculate_bsi_scores(has_defaults, sim_verified)
    apex = calculate_apex_score(bsi_l, bsi_d, bsi_s, outstanding, history)

    applicant = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": f"{fn} {mid} {ln}",
        "country": country,
        "occupation": random.choice(JOBS),
        "bsi": {
            "location": bsi_l,
            "device": bsi_d,
            "sim": bsi_s
        },
        "apex_score": apex,
        "risk_level": "Low" if apex >= 75 else "Medium" if apex >= 50 else "High",
        "tfd": {
            "currency": c["currency"],
            "outstanding_debt": outstanding,
            "loan_history": history
        },
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    DATABASE[applicant["id"]] = applicant
    return applicant

# -------------------- PRELOAD DATA --------------------

for _ in range(150):
    generate_applicant()

# -------------------- ROUTES --------------------

@app.get("/")
def root():
    return {"status": "ApexScore API running", "version": "2.0"}

@app.get("/api/applicants")
def list_applicants(limit: int = 50):
    return list(DATABASE.values())[:limit]

@app.get("/api/search")
def search(email: str = Query(...)):
    if not is_valid_email(email):
        raise HTTPException(400, "Invalid email domain")
    for a in DATABASE.values():
        if a["email"].lower() == email.lower():
            return a
    return generate_applicant(email)

@app.get("/api/applicant/{id}")
def get_applicant(id: str):
    if id not in DATABASE:
        raise HTTPException(404, "Applicant not found")
    return DATABASE[id]

@app.get("/api/stats")
def stats():
    total = len(DATABASE)
    high = len([a for a in DATABASE.values() if a["risk_level"] == "High"])
    medium = len([a for a in DATABASE.values() if a["risk_level"] == "Medium"])
    low = len([a for a in DATABASE.values() if a["risk_level"] == "Low"])
    avg = sum(a["apex_score"] for a in DATABASE.values()) / total if total else 0

    return {
        "total_applicants": total,
        "high_risk": high,
        "medium_risk": medium,
        "low_risk": low,
        "high_risk_percentage": f"{int((high / total) * 100)}%" if total else "0%",
        "average_apex_score": round(avg, 2)
    }
