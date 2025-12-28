from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from datetime import datetime
import random, hashlib, uuid

app = FastAPI(
    title="ApexScore Global Credit Intelligence",
    description="Global Unified Loan History & Risk Engine",
    version="6.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# GLOBAL DATA
# ======================================================

COUNTRIES = {
    "Nigeria": {
        "currency": "NGN",
        "isps": ["MTN", "Airtel", "Glo", "9mobile", "Starlink NG"],
        "banks": ["GTBank", "Access Bank", "Opay", "Palmpay", "Moniepoint", "Kuda", "FairMoney", "Carbon"]
    },
    "Kenya": {
        "currency": "KES",
        "isps": ["Safaricom", "Airtel KE", "Telkom"],
        "banks": ["KCB", "Equity Bank", "M-Pesa", "NCBA", "Absa KE"]
    },
    "USA": {
        "currency": "USD",
        "isps": ["Verizon", "AT&T", "T-Mobile", "Comcast"],
        "banks": ["Chase", "Bank of America", "Wells Fargo", "Chime", "Cash App"]
    },
    "UK": {
        "currency": "GBP",
        "isps": ["Vodafone UK", "O2", "EE", "BT"],
        "banks": ["HSBC", "Barclays", "Monzo", "Starling", "Lloyds"]
    },
    "India": {
        "currency": "INR",
        "isps": ["Airtel IN", "Reliance Jio", "Vodafone Idea"],
        "banks": ["HDFC", "ICICI", "Paytm", "Axis Bank"]
    }
}

OCCUPATIONS = [
    "Market Trader", "Okada Rider", "Taxi Driver", "Bolt Driver",
    "POS Agent", "Bricklayer", "Welder", "Carpenter",
    "Phone Repairer", "Street Food Vendor", "Farmer",
    "Fisherman", "Tailor", "Laundry Operator",
    "Sole Proprietor", "Small Shop Owner"
]

ANDROID_MODELS = [
    "Tecno Spark 10", "Infinix Hot 30", "Samsung A12",
    "Redmi Note 11", "Itel S23", "Pixel 6"
]

IOS_MODELS = ["iPhone 11", "iPhone 12", "iPhone 13"]
DESKTOP_DEVICES = ["Windows Chrome", "macOS Safari", "Ubuntu Firefox"]

APPLICANTS_DB: Dict[str, Dict] = {}
ACTIVITY_LOGS: List[Dict] = []
DECISION_LOGS: List[Dict] = []

# ======================================================
# HELPERS
# ======================================================

def seed(value: str):
    random.seed(int(hashlib.sha256(value.encode()).hexdigest(), 16))

def risk_level(score):
    return "Low" if score >= 75 else "Medium" if score >= 50 else "High"

# ======================================================
# DEVICE
# ======================================================

def generate_device(email: str):
    seed(email + "device")
    device_type = random.choice(["Android", "iOS", "Desktop"])

    if device_type == "Android":
        return {"type": "Android", "model": random.choice(ANDROID_MODELS)}
    if device_type == "iOS":
        return {"type": "iOS", "model": random.choice(IOS_MODELS)}
    return {"type": "Desktop", "model": random.choice(DESKTOP_DEVICES)}

# ======================================================
# PROFILE
# ======================================================

FIRST_NAMES = ["John", "Ahmed", "Blessing", "Michael", "Daniel", "Aisha", "Sadiq", "Fatima"]
LAST_NAMES = ["Okoye", "Smith", "Hassan", "Patel", "Brown", "Adeyemi", "Khan"]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com"]

def generate_real_email():
    return f"{random.choice(LAST_NAMES).lower()}{random.randint(10,999)}@{random.choice(EMAIL_DOMAINS)}"

def generate_profile(email: str):
    seed(email)

    country = random.choice(list(COUNTRIES.keys()))
    c = COUNTRIES[country]

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    score = random.randint(25, 95)

    return {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": {
            "first": first,
            "last": last,
            "full": f"{first} {last}"
        },
        "country": country,
        "occupation": random.choice(OCCUPATIONS),
        "financials": {
            "currency": c["currency"],
            "outstanding_debt": random.randint(500, 25000),
            "bank_accounts": [
                {
                    "bank": random.choice(c["banks"]),
                    "account_last_5": random.randint(10000, 99999)
                } for _ in range(random.randint(1, 3))
            ]
        },
        "device": generate_device(email),
        "network": {"isp": random.choice(c["isps"])},
        "apex_score": score,
        "risk_level": risk_level(score),
        "created_at": datetime.utcnow().isoformat()
    }

# ======================================================
# API
# ======================================================

@app.get("/api/search")
async def search(email: str, request: Request):
    if "@" not in email:
        raise HTTPException(400, "Invalid email")

    if email not in APPLICANTS_DB:
        APPLICANTS_DB[email] = generate_profile(email)

    return APPLICANTS_DB[email]

@app.get("/api/applicants")
async def endless(limit: int = 20):
    while len(APPLICANTS_DB) < limit:
        fake = generate_real_email()
        APPLICANTS_DB[fake] = generate_profile(fake)

    return {"applicants": list(APPLICANTS_DB.values())[-limit:]}

@app.get("/api/stats")
async def stats():
    total = len(APPLICANTS_DB)
    high = sum(1 for a in APPLICANTS_DB.values() if a["risk_level"] == "High")
    return {
        "total_applicants": total,
        "active_defaults": high,
        "high_risk_percentage": f"{(high/total*100):.1f}%" if total else "0%"
}
