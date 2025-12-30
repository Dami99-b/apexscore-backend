from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import random, uuid, datetime
from datetime import timedelta

app = FastAPI(title="ApexScore API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- GLOBAL DATA --------------------

COUNTRIES = {
    "Nigeria": {
        "code": "+234",
        "banks": ["GTBank", "Access Bank", "First Bank", "Sterling Bank", "UBA", "Opay", "Moniepoint MFB", "PalmPay", "Kuda", "FairMoney"],
        "isps": ["MTN", "Airtel", "Glo", "9mobile"],
        "cities": ["Lagos", "Ibadan", "Abeokuta", "Benin City", "Onitsha"],
        "android_models": ["Tecno Spark", "Infinix Hot", "Samsung A14", "Xiaomi Redmi"],
        "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]
    },
    "USA": {
        "code": "+1",
        "banks": ["Chase", "Bank of America", "Wells Fargo", "Capital One"],
        "isps": ["Verizon", "AT&T", "T-Mobile"],
        "cities": ["New York", "Houston", "Chicago", "Dallas", "Los Angeles"],
        "android_models": ["Samsung Galaxy S21", "Google Pixel", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "UK": {
        "code": "+44",
        "banks": ["Barclays", "HSBC", "NatWest", "Monzo", "Revolut"],
        "isps": ["Vodafone", "O2", "EE"],
        "cities": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
        "android_models": ["Samsung Galaxy", "Google Pixel", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Germany": {
        "code": "+49",
        "banks": ["Deutsche Bank", "Commerzbank", "N26"],
        "isps": ["Telekom", "Vodafone DE"],
        "cities": ["Berlin", "Hamburg", "Munich", "Frankfurt", "Cologne"],
        "android_models": ["Samsung Galaxy", "Huawei", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Canada": {
        "code": "+1",
        "banks": ["TD Bank", "RBC", "Scotiabank", "BMO"],
        "isps": ["Rogers", "Bell", "Telus"],
        "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
        "android_models": ["Samsung Galaxy", "Google Pixel", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Kenya": {
        "code": "+254",
        "banks": ["Equity Bank", "KCB", "M-Pesa", "Safaricom"],
        "isps": ["Safaricom", "Airtel Kenya", "Telkom"],
        "cities": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"],
        "android_models": ["Tecno", "Infinix", "Samsung A-series"],
        "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]
    },
    "Ghana": {
        "code": "+233",
        "banks": ["Ecobank", "GCB Bank", "MTN Mobile Money", "Stanbic Bank"],
        "isps": ["MTN Ghana", "Vodafone Ghana", "AirtelTigo"],
        "cities": ["Accra", "Kumasi", "Tamale", "Takoradi", "Cape Coast"],
        "android_models": ["Tecno", "Infinix", "Samsung"],
        "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]
    },
    "South Africa": {
        "code": "+27",
        "banks": ["Standard Bank", "FNB", "Absa", "Capitec"],
        "isps": ["MTN", "Vodacom", "Cell C"],
        "cities": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth"],
        "android_models": ["Samsung", "Huawei", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "India": {
        "code": "+91",
        "banks": ["SBI", "HDFC", "ICICI", "Paytm"],
        "isps": ["Jio", "Airtel", "Vi"],
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
        "android_models": ["Xiaomi", "Samsung", "Realme", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Brazil": {
        "code": "+55",
        "banks": ["Banco do Brasil", "Itaú", "Bradesco", "Nubank"],
        "isps": ["Vivo", "Claro", "TIM"],
        "cities": ["São Paulo", "Rio de Janeiro", "Brasília", "Salvador", "Fortaleza"],
        "android_models": ["Samsung", "Motorola", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 11"]
    },
}

FIRST_NAMES = ["Michael", "David", "Blessing", "Fatima", "Esther", "Joseph", "Daniel", "Grace", "Amara", "Chen", "Raj", "Maria"]
LAST_NAMES = ["Anderson", "Brown", "Okoye", "Hassan", "Adeyemi", "Johnson", "Silva", "Kumar", "Wang", "Garcia"]
MIDDLE_NAMES = ["James", "Oluwaseun", "Ibrahim", "Paul", "Grace", "Abdul", "Marie", "Anne", "Luis", "Wei"]
JOBS = ["Trader", "Farmer", "POS Agent", "Ride-hailing Driver", "Market Vendor", "Tailor", "Electrician", "Teacher", "Nurse", "Shop Owner"]

LOAN_PURPOSES = ["Business Expansion", "Education", "Medical Emergency", "Rent Payment", "Inventory Purchase", "Equipment", "Working Capital", "Personal Use"]
REPAYMENT_STATUS = ["Paid On Time", "Paid Early", "Paid Late", "Defaulted", "Restructured", "Active"]

DATABASE = {}

# -------------------- HELPERS --------------------

def generate_email(fn, ln):
    domains = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com"]
    return f"{fn.lower()}{ln.lower()}{random.randint(1, 999)}@{random.choice(domains)}"

def generate_loan_history(num_loans, country_banks):
    """Generate realistic loan history"""
    history = []
    base_date = datetime.datetime.utcnow() - timedelta(days=random.randint(365, 1825))
    
    for i in range(num_loans):
        loan_date = base_date + timedelta(days=random.randint(0, 730))
        amount = random.randint(500, 50000)
        status = random.choice(REPAYMENT_STATUS)
        
        days_overdue = 0
        if status == "Paid Late":
            days_overdue = random.randint(1, 30)
        elif status == "Defaulted":
            days_overdue = random.randint(31, 365)
        
        loan = {
            "loan_id": f"LN-{uuid.uuid4().hex[:8].upper()}",
            "institution": random.choice(country_banks),
            "amount": amount,
            "currency": "USD",
            "purpose": random.choice(LOAN_PURPOSES),
            "disbursement_date": loan_date.strftime("%Y-%m-%d"),
            "due_date": (loan_date + timedelta(days=random.randint(30, 365))).strftime("%Y-%m-%d"),
            "status": status,
            "days_overdue": days_overdue if days_overdue > 0 else None,
            "repayment_amount": amount + int(amount * random.uniform(0.05, 0.25)) if status in ["Paid On Time", "Paid Early", "Paid Late"] else None
        }
        history.append(loan)
    
    return sorted(history, key=lambda x: x["disbursement_date"], reverse=True)

def generate_applicant(email=None):
    country = random.choice(list(COUNTRIES.keys()))
    c = COUNTRIES[country]

    fn = random.choice(FIRST_NAMES)
    ln = random.choice(LAST_NAMES)
    mid = random.choice(MIDDLE_NAMES)

    email = email or generate_email(fn, ln)
    score = random.randint(30, 95)
    
    num_loans = random.randint(0, 5)
    loan_history = generate_loan_history(num_loans, c["banks"])
    
    # Choose device type first, then match OS and model
    device_type = random.choice(["Android", "iOS"])
    if device_type == "Android":
        model = random.choice(c["android_models"])
        os_version = random.choice(["Android 13", "Android 12", "Android 11"])
    else:
        model = random.choice(c["ios_models"])
        os_version = random.choice(["iOS 16", "iOS 15", "iOS 17"])

    applicant = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": {
            "first": fn,
            "middle": mid,
            "last": ln,
            "full": f"{fn} {mid} {ln}"
        },
        "phone": f"{c['code']} {random.randint(700000000, 999999999)}",
        "occupation": random.choice(JOBS),
        "location": {
            "city": random.choice(c["cities"]),
            "country": country,
            "address": f"{random.randint(10, 300)} Main Street",
            "coordinates": {
                "lat": round(random.uniform(-60, 60), 4),
                "lng": round(random.uniform(-120, 120), 4)
            }
        },
        "network": {
            "isp": random.choice(c["isps"]),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}"
        },
        "sim_registration": random.choice(["VERIFIED", "UNVERIFIED"]),
        "device_fingerprint": {
            "device_id": str(uuid.uuid4()),
            "device_type": device_type,
            "model": model,
            "os_version": os_version,
            "is_rooted": random.choice([False, False, False, True]),
            "vpn_detected": random.choice([False, False, True]),
        },
        "bank_accounts": [{
            "bank_name": random.choice(c["banks"]),
            "account_number": str(random.randint(1000000000, 9999999999)),
            "account_type": random.choice(["Savings", "Current"]),
            "status": random.choice(["Active", "Active", "Active", "Dormant"])
        } for _ in range(random.randint(1, 3))],
        "tfd": {
            "currency": "USD",
            "outstanding_debt": random.randint(0, 50000),
            "loan_history": loan_history
        },
        "bsi": {
            "location_consistency": random.randint(30, 95),
            "device_stability": random.randint(30, 95),
            "sim_changes": random.randint(10, 90)
        },
        "apex_score": score,
        "risk_level": "Low" if score >= 75 else "Medium" if score >= 50 else "High",
        "action_recommendation": {
            "recommendation": "Approve" if score >= 75 else "Review" if score >= 50 else "Reject"
        },
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    DATABASE[applicant["id"]] = applicant
    return applicant

# preload
for _ in range(150):
    generate_applicant()

# -------------------- ROUTES --------------------

@app.get("/")
def root():
    return {"status": "ApexScore API running"}

@app.get("/api/applicants")
def list_applicants(limit: int = 50):
    return {"applicants": list(DATABASE.values())[:limit]}

@app.get("/api/search")
def search(email: str = Query(...)):
    for a in DATABASE.values():
        if a["email"].lower() == email.lower():
            return a
    return generate_applicant(email)

@app.get("/api/applicant/{id}")
def get_applicant(id: str):
    return DATABASE.get(id)

@app.get("/api/stats")
def stats():
    total = len(DATABASE)
    high = len([a for a in DATABASE.values() if a["risk_level"] == "High"])
    return {
        "total_applicants": total,
        "active_defaults": high,
        "high_risk_percentage": f"{int((high/total)*100)}%"
    }
