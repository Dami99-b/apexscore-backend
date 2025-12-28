from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from datetime import datetime
import random, hashlib, uuid

app = FastAPI(
    title="ApexScore Global Credit Intelligence",
    description="Global Unified Loan History & Risk Engine",
    version="6.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# GLOBAL DATA (EXPANDED)
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
        "isps": ["Reliance Jio", "Airtel IN", "Vodafone Idea"],
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
    "Tecno Spark 10", "Infinix Hot 30", "Samsung A12", "Samsung A04",
    "Redmi 9A", "Redmi Note 11", "Itel S23",
    "Pixel 6", "Pixel 7"
]

IOS_MODELS = [
    "iPhone XR", "iPhone 11", "iPhone 12",
    "iPhone 13", "iPhone 14"
]

DESKTOP_DEVICES = [
    "Windows 10 Chrome", "Windows 11 Edge",
    "macOS Safari", "Ubuntu Firefox"
]

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
# DEVICE INTELLIGENCE
# ======================================================

def generate_device_profile(email: str, country: str):
    seed(email + "device")

    device_type = random.choice(["Android", "iOS", "Desktop"])

    if device_type == "Android":
        model = random.choice(ANDROID_MODELS)
        os = f"Android {random.randint(9,14)}"
    elif device_type == "iOS":
        model = random.choice(IOS_MODELS)
        os = f"iOS {random.randint(13,17)}"
    else:
        model = random.choice(DESKTOP_DEVICES)
        os = "Desktop"

    return {
        "device_id": hashlib.md5(email.encode()).hexdigest(),
        "type": device_type,
        "model": model,
        "os_version": os,
        "is_emulator": random.random() < 0.06,
        "rooted_or_jailbroken": random.random() < 0.1,
        "first_seen": datetime.utcnow().isoformat()
    }

# ======================================================
# PROFILE GENERATION
# ======================================================

def generate_profile(email: str) -> Dict:
    seed(email)

    country = random.choice(list(COUNTRIES.keys()))
    country_data = COUNTRIES[country]

    first_names = ["John", "Ahmed", "Sadiq", "Blessing", "Michael", "Fatima", "Daniel", "Aisha"]
    last_names = ["Okoye", "Smith", "Hassan", "Patel", "Brown", "Adeyemi", "Khan"]

    first = random.choice(first_names)
    last = random.choice(last_names)

    score = random.randint(25, 95)
    level = risk_level(score)

    device = generate_device_profile(email, country)

    outstanding = random.randint(500, 25000)

    profile = {
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
            "currency": country_data["currency"],
            "outstanding_debt": outstanding,
            "bank_accounts": [
                {
                    "bank": random.choice(country_data["banks"]),
                    "account_last_5": str(random.randint(10000, 99999))
                }
                for _ in range(random.randint(1, 3))
            ]
        },
        "device_profile": device,
        "network": {
            "isp": random.choice(country_data["isps"]),
            "ip_risk": random.choice(["Low", "Medium", "High"])
        },
        "apex_score": score,
        "risk_level": level,
        "created_at": datetime.utcnow().isoformat()
    }

    return profile

# ======================================================
# API
# ======================================================

@app.get("/api/search")
async def search_by_email(email: str, request: Request):
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email")

    if email not in APPLICANTS_DB:
        APPLICANTS_DB[email] = generate_profile(email)

    profile = APPLICANTS_DB[email]

    ACTIVITY_LOGS.append({
        "email": email,
        "ip": request.client.host,
        "time": datetime.utcnow().isoformat(),
        "event": "PROFILE_SEARCH"
    })

    DECISION_LOGS.append({
        "email": email,
        "score": profile["apex_score"],
        "risk": profile["risk_level"],
        "decision_time": datetime.utcnow().isoformat()
    })

    return {
        **profile,
        "activity_logs_count": len(ACTIVITY_LOGS),
        "decision_logs_count": len(DECISION_LOGS)
    }

@app.get("/api/applicants")
async def endless_feed(limit: int = 20):
    while len(APPLICANTS_DB) < limit:
        fake_email = f"user{random.randint(10000,99999)}@mail.com"
        APPLICANTS_DB[fake_email] = generate_profile(fake_email)

    return {
        "applicants": list(APPLICANTS_DB.values())[-limit:]
}
