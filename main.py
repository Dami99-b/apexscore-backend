from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import random, uuid, hashlib

app = FastAPI(title="ApexScore Global Engine", version="7.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ======================================================
# GLOBAL DATABASE (EXPANDABLE)
# ======================================================

COUNTRIES = {
    "Nigeria": {
        "currency": "NGN",
        "cities": ["Lagos", "Ibadan", "Abeokuta", "Akure", "Benin"],
        "isps": ["MTN", "Airtel", "Glo", "9mobile", "Starlink NG"],
        "banks": ["GTBank", "Access Bank", "Opay", "Palmpay", "Moniepoint", "Kuda", "Carbon", "LAPO MFB", "AB Microfinance"]
    },
    "USA": {
        "currency": "USD",
        "cities": ["New York", "Houston", "Chicago", "Austin"],
        "isps": ["Verizon", "AT&T", "T-Mobile", "Comcast"],
        "banks": ["Chase", "Bank of America", "Wells Fargo", "Chime", "SoFi"]
    },
    "UK": {
        "currency": "GBP",
        "cities": ["London", "Manchester", "Birmingham"],
        "isps": ["Vodafone UK", "O2", "EE"],
        "banks": ["HSBC", "Barclays", "Monzo", "Starling"]
    }
}

FIRST_NAMES = [
    "Michael","David","John","James","Daniel","Ahmed","Sadiq",
    "Blessing","Samuel","Aisha","Fatima","Mary","Esther","Joseph"
]

MIDDLE_NAMES = [
    "James","Oluwaseun","Ibrahim","Paul","Grace","Abdul","Marie","Anne"
]

LAST_NAMES = [
    "Anderson","Smith","Johnson","Brown","Adeyemi","Okoye","Hassan","Khan","Williams"
]

OCCUPATIONS = [
    "Market Trader","Taxi Driver","Bolt Driver","POS Agent",
    "Bricklayer","Welder","Tailor","Farmer","Fisherman",
    "Phone Repairer","Small Shop Owner","Sole Proprietor"
]

ANDROID_MODELS = ["Tecno Spark 10","Infinix Hot 30","Samsung A12","Redmi 9A"]
IOS_MODELS = ["iPhone XR","iPhone 11","iPhone 13"]
DESKTOP = ["Windows 11 Chrome","macOS Safari","Ubuntu Firefox"]

APPLICANTS = {}

# ======================================================
# HELPERS
# ======================================================

def seed(val: str):
    random.seed(int(hashlib.sha256(val.encode()).hexdigest(), 16))

def risk_level(score):
    return "Low" if score >= 75 else "Medium" if score >= 50 else "High"

def device_profile(email):
    device_type = random.choice(["Android","iOS","Desktop"])
    if device_type == "Android":
        model = random.choice(ANDROID_MODELS)
        os = f"Android {random.randint(9,14)}"
    elif device_type == "iOS":
        model = random.choice(IOS_MODELS)
        os = f"iOS {random.randint(14,17)}"
    else:
        model = random.choice(DESKTOP)
        os = "Desktop"

    return {
        "device_id": hashlib.md5(email.encode()).hexdigest(),
        "device_type": device_type,
        "model": model,
        "os_version": os,
        "is_emulator": random.random() < 0.05,
        "is_rooted": random.random() < 0.07,
        "vpn_detected": random.random() < 0.12,
        "proxy_detected": random.random() < 0.08
    }

# ======================================================
# PROFILE GENERATION
# ======================================================

def generate_profile(email: str):
    seed(email)

    country = random.choice(list(COUNTRIES.keys()))
    data = COUNTRIES[country]

    first = random.choice(FIRST_NAMES)
    middle = random.choice(MIDDLE_NAMES)
    last = random.choice(LAST_NAMES)

    score = random.randint(25, 95)

    return {
        "id": str(uuid.uuid4()),
        "email": email,
        "phone": f"+{random.randint(1,234)} {random.randint(700,999)} {random.randint(100,999)} {random.randint(1000,9999)}",
        "name": {
            "first": first,
            "middle": middle,
            "last": last,
            "full": f"{first} {middle} {last}"
        },
        "occupation": random.choice(OCCUPATIONS),
        "location": {
            "city": random.choice(data["cities"]),
            "country": country,
            "address": f"{random.randint(10,299)} High Street",
            "coordinates": {
                "lat": round(random.uniform(-90,90),6),
                "lng": round(random.uniform(-180,180),6)
            }
        },
        "network": {
            "isp": random.choice(data["isps"]),
            "ip_address": ".".join(str(random.randint(1,255)) for _ in range(4))
        },
        "device_fingerprint": device_profile(email),
        "bank_accounts": [
            {
                "bank_name": random.choice(data["banks"]),
                "account_number": str(random.randint(10**9, 10**10-1)),
                "account_type": random.choice(["Savings","Current"]),
                "status": random.choice(["Active","Dormant"])
            }
            for _ in range(random.randint(1,3))
        ],
        "tfd": {
            "currency": data["currency"],
            "outstanding_debt": random.randint(500, 50000),
            "loan_history": [
                {
                    "lender": random.choice(data["banks"]),
                    "amount": random.randint(1000,20000),
                    "date": f"{random.randint(2020,2024)}-{random.randint(1,12):02d}",
                    "status": random.choice(["Completed","Active","Defaulted"])
                }
                for _ in range(random.randint(1,4))
            ]
        },
        "bsi": {
            "location_consistency": random.randint(20,95),
            "device_stability": random.randint(20,95),
            "sim_changes": random.randint(10,95),
            "travel_frequency": random.randint(10,95)
        },
        "apex_score": score,
        "risk_level": risk_level(score),
        "action_recommendation": {
            "recommendation": "Approve" if score >= 75 else "Manual Review" if score >= 50 else "Reject"
        },
        "created_at": datetime.utcnow().isoformat()
    }

# ======================================================
# API
# ======================================================

@app.get("/api/search")
def search(email: str):
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email")

    if email not in APPLICANTS:
        APPLICANTS[email] = generate_profile(email)

    return APPLICANTS[email]

@app.get("/api/applicants")
def applicants(limit: int = 50):
    while len(APPLICANTS) < limit:
        fake = f"user{random.randint(10000,99999)}@mail.com"
        APPLICANTS[fake] = generate_profile(fake)

    return {"applicants": list(APPLICANTS.values())[-limit:]}

@app.get("/api/stats")
def stats():
    total = len(APPLICANTS)
    high = len([a for a in APPLICANTS.values() if a["risk_level"] == "High"])
    return {
        "total_applicants": total,
        "active_defaults": high,
        "high_risk_percentage": f"{int((high/max(total,1))*100)}%"
    }
