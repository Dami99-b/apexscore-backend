from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, List
from datetime import datetime
import random, hashlib, uuid

app = FastAPI(
    title="ApexScore Global Credit Intelligence",
    version="7.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# =====================================================
# GLOBAL DATA (LARGE & COUNTRY-SPECIFIC)
# =====================================================

COUNTRIES = {
    "Nigeria": {
        "currency": "NGN",
        "isps": ["MTN", "Airtel", "Glo", "9mobile", "Starlink NG"],
        "banks": [
            "GTBank", "Access Bank", "Zenith",
            "Kuda", "Opay", "Moniepoint", "Palmpay",
            "FairMoney MFB", "Carbon MFB", "LAPO MFB"
        ]
    },
    "USA": {
        "currency": "USD",
        "isps": ["Verizon", "AT&T", "T-Mobile", "Comcast"],
        "banks": ["Chase", "Wells Fargo", "Bank of America", "Chime", "Cash App"]
    },
    "UK": {
        "currency": "GBP",
        "isps": ["Vodafone", "EE", "O2", "BT"],
        "banks": ["HSBC", "Barclays", "Lloyds", "Monzo", "Starling"]
    },
    "India": {
        "currency": "INR",
        "isps": ["Airtel", "Jio", "Vi"],
        "banks": ["HDFC", "ICICI", "Axis", "Paytm"]
    },
    "Kenya": {
        "currency": "KES",
        "isps": ["Safaricom", "Airtel KE"],
        "banks": ["KCB", "Equity", "M-Pesa", "NCBA"]
    }
}

FIRST_NAMES = [
    "Michael","Ahmed","Fatima","Daniel","Grace","Samuel","Aisha","John",
    "Robert","Linda","Patricia","James","Elizabeth","Maria","Chen","Wei",
    "Raj","Anita","Mohammed","Yusuf","Ibrahim","Sadiq","Blessing"
]

LAST_NAMES = [
    "Okoye","Adeyemi","Balogun","Smith","Brown","Johnson","Patel","Singh",
    "Khan","Ali","Garcia","Martinez","Chen","Wang","Hassan","Abdul"
]

OCCUPATIONS = [
    "Market Trader","Taxi Driver","Ride-Hailing Driver","POS Agent",
    "Bricklayer","Carpenter","Welder","Mechanic","Farmer","Fisherman",
    "Street Vendor","Phone Repairer","Laundry Operator","Tailor",
    "Sole Proprietor","Shop Owner","Courier","Security Guard"
]

ANDROID_MODELS = [
    "Tecno Spark 10","Infinix Hot 30","Samsung A04","Samsung A12",
    "Redmi 9A","Redmi Note 11","Itel S23","Pixel 6","Pixel 7"
]

IOS_MODELS = ["iPhone XR","iPhone 11","iPhone 12","iPhone 13","iPhone 14"]

DESKTOP_DEVICES = ["Windows 10 Chrome","Windows 11 Edge","macOS Safari"]

# =====================================================
# STORAGE
# =====================================================

APPLICANTS: Dict[str, Dict] = {}
ACTIVITY_LOGS: List[Dict] = []

# =====================================================
# HELPERS
# =====================================================

def seed(val: str):
    random.seed(int(hashlib.sha256(val.encode()).hexdigest(), 16))

def mask_email(email: str):
    name, domain = email.split("@")
    return f"{name[:2]}***@{domain}"

def risk_level(score: int):
    return "Low" if score >= 75 else "Medium" if score >= 50 else "High"

# =====================================================
# DEVICE FINGERPRINT
# =====================================================

def device_profile(email: str):
    seed(email + "device")
    device_type = random.choice(["Android","iOS","Desktop"])

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
        "os": os,
        "emulator": random.random() < 0.05,
        "rooted": random.random() < 0.08
    }

# =====================================================
# PROFILE GENERATOR
# =====================================================

def generate_profile(email: str):
    seed(email)

    country = random.choice(list(COUNTRIES.keys()))
    c = COUNTRIES[country]

    first = random.choice(FIRST_NAMES)
    last = random.choice(LAST_NAMES)

    score = random.randint(25, 95)

    profile = {
        "id": str(uuid.uuid4()),
        "email": email,
        "email_masked": mask_email(email),
        "name": f"{first} {last}",
        "country": country,
        "occupation": random.choice(OCCUPATIONS),
        "apex_score": score,
        "risk_level": risk_level(score),
        "network": {
            "isp": random.choice(c["isps"]),
            "ip_risk": random.choice(["Low","Medium","High"])
        },
        "financials": {
            "currency": c["currency"],
            "outstanding_debt": random.randint(500, 30000),
            "bank_accounts": [
                {
                    "bank": random.choice(c["banks"]),
                    "account_last_5": random.randint(10000,99999)
                }
                for _ in range(random.randint(1,3))
            ]
        },
        "device": device_profile(email),
        "created_at": datetime.utcnow().isoformat()
    }

    return profile

# =====================================================
# API
# =====================================================

@app.get("/api/search")
async def search(email: str, request: Request):
    if "@" not in email:
        raise HTTPException(400, "Invalid email")

    if email not in APPLICANTS:
        APPLICANTS[email] = generate_profile(email)

    ACTIVITY_LOGS.append({
        "email": email,
        "ip": request.client.host,
        "time": datetime.utcnow().isoformat()
    })

    return APPLICANTS[email]

@app.get("/api/applicants")
async def endless(limit: int = 25):
    while len(APPLICANTS) < limit:
        fake = f"user{random.randint(10000,99999)}@mail.com"
        APPLICANTS[fake] = generate_profile(fake)

    return {
        "applicants": list(APPLICANTS.values())[-limit:]
                                     }
