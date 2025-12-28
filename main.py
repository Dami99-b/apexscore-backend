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
# GLOBAL DATA
# ======================================================

COUNTRIES = {
    "Nigeria": {
        "currency": "NGN",
        "lat": 6.5244, "lng": 3.3792,
        "isps": ["MTN", "Airtel", "Glo", "9mobile"],
        "banks": ["GTBank", "Access Bank", "Opay", "Palmpay", "Kuda"]
    },
    "Kenya": {
        "currency": "KES",
        "lat": -1.2921, "lng": 36.8219,
        "isps": ["Safaricom", "Airtel KE"],
        "banks": ["KCB", "Equity Bank", "M-Pesa"]
    },
    "USA": {
        "currency": "USD",
        "lat": 40.7128, "lng": -74.0060,
        "isps": ["Verizon", "AT&T", "T-Mobile"],
        "banks": ["Chase", "Bank of America", "Chime"]
    },
    "UK": {
        "currency": "GBP",
        "lat": 51.5074, "lng": -0.1278,
        "isps": ["Vodafone UK", "O2", "EE"],
        "banks": ["HSBC", "Barclays", "Monzo"]
    },
    "India": {
        "currency": "INR",
        "lat": 19.0760, "lng": 72.8777,
        "isps": ["Reliance Jio", "Airtel IN"],
        "banks": ["HDFC", "ICICI", "Paytm"]
    }
}

OCCUPATIONS = [
    "Market Trader", "Okada Rider", "Taxi Driver", "Bolt Driver",
    "POS Agent", "Bricklayer", "Welder", "Carpenter",
    "Phone Repairer", "Street Food Vendor", "Farmer",
    "Fisherman", "Tailor", "Laundry Operator", "Small Shop Owner"
]

APPLICANTS_DB: Dict[str, Dict] = {}

# ======================================================
# HELPERS
# ======================================================

def seed(value: str):
    random.seed(int(hashlib.sha256(value.encode()).hexdigest(), 16))

def risk_level(score):
    return "Low" if score >= 75 else "Medium" if score >= 50 else "High"

def mask_email(email: str) -> str:
    """Mask email showing only first 2 and last 2 chars before @"""
    if "@" not in email:
        return email
    
    local, domain = email.split("@")
    
    if len(local) <= 4:
        masked = local[0] + "*" * (len(local) - 1)
    else:
        masked = local[:2] + "*" * (len(local) - 4) + local[-2:]
    
    return f"{masked}@{domain}"

# ======================================================
# PROFILE GENERATION
# ======================================================

def generate_profile(email: str) -> Dict:
    seed(email)

    country = random.choice(list(COUNTRIES.keys()))
    country_data = COUNTRIES[country]

    # Realistic names
    first_names = {
        "Nigeria": ["Chidi", "Amina", "Tunde", "Blessing", "Emeka", "Ngozi", "Oluwaseun", "Chiamaka"],
        "Kenya": ["Wanjiru", "Otieno", "Akinyi", "Kamau", "Njeri", "Omondi"],
        "USA": ["Michael", "Sarah", "James", "Emily", "David", "Jessica"],
        "UK": ["Oliver", "Emma", "Harry", "Sophie", "George", "Charlotte"],
        "India": ["Rajesh", "Priya", "Amit", "Sneha", "Arjun", "Kavya"]
    }
    
    last_names = {
        "Nigeria": ["Okonkwo", "Adeyemi", "Nwosu", "Okeke", "Adeleke", "Eze"],
        "Kenya": ["Kamau", "Onyango", "Mwangi", "Odhiambo", "Wambui"],
        "USA": ["Smith", "Johnson", "Williams", "Brown", "Davis", "Miller"],
        "UK": ["Smith", "Jones", "Taylor", "Brown", "Davies", "Wilson"],
        "India": ["Kumar", "Sharma", "Patel", "Singh", "Reddy", "Gupta"]
    }

    first = random.choice(first_names.get(country, first_names["USA"]))
    last = random.choice(last_names.get(country, last_names["USA"]))
    full_name = f"{first} {last}"

    score = random.randint(25, 95)
    level = risk_level(score)
    outstanding = random.randint(5000, 250000)
    
    cities = {
        "Nigeria": ["Lagos", "Abuja", "Port Harcourt"],
        "Kenya": ["Nairobi", "Mombasa"],
        "USA": ["New York", "Los Angeles"],
        "UK": ["London", "Manchester"],
        "India": ["Mumbai", "Delhi"]
    }
    city = random.choice(cities.get(country, ["Capital City"]))
    
    # Generate BSI
    if level == "Low":
        bsi = {
            "location_consistency": random.randint(85, 98),
            "ip_vs_address": random.randint(82, 96),
            "device_stability": random.randint(88, 99),
            "sim_changes": random.randint(90, 99),
            "travel_frequency": random.randint(10, 30)
        }
    elif level == "Medium":
        bsi = {
            "location_consistency": random.randint(60, 84),
            "ip_vs_address": random.randint(55, 78),
            "device_stability": random.randint(60, 85),
            "sim_changes": random.randint(55, 82),
            "travel_frequency": random.randint(35, 55)
        }
    else:
        bsi = {
            "location_consistency": random.randint(25, 59),
            "ip_vs_address": random.randint(20, 54),
            "device_stability": random.randint(25, 59),
            "sim_changes": random.randint(20, 54),
            "travel_frequency": random.randint(60, 90)
        }
    
    # Generate loan history
    loan_count = random.randint(1, 4)
    loan_history = []
    for i in range(loan_count):
        year = random.randint(2021, 2024)
        month = random.randint(1, 12)
        loan_history.append({
            "institution": random.choice(country_data["banks"]),
            "amount": random.randint(10000, 100000),
            "date": f"{year}-{month:02d}"
        })
    
    # Generate phone
    phone_codes = {"Nigeria": "+234", "Kenya": "+254", "USA": "+1", "UK": "+44", "India": "+91"}
    phone = f"{phone_codes.get(country, '+234')} {random.randint(700, 999)} {random.randint(100, 999)} {random.randint(1000, 9999)}"

    profile = {
        "id": str(uuid.uuid4()),
        "email": email,
        "email_masked": mask_email(email),
        "name": full_name,
        "phone": phone,
        "country": country,
        "occupation": random.choice(OCCUPATIONS),
        "location": {
            "city": city,
            "country": country,
            "address": f"{random.randint(1, 999)} {random.choice(['Main', 'Market', 'Station'])} Street, {city}",
            "coordinates": {
                "lat": country_data["lat"] + random.uniform(-0.5, 0.5),
                "lng": country_data["lng"] + random.uniform(-0.5, 0.5)
            }
        },
        "tfd": {
            "currency": country_data["currency"],
            "outstanding_debt": outstanding,
            "loan_history": loan_history
        },
        "bsi": bsi,
        "apex_score": score,
        "risk_level": level,
        "action_recommendation": {
            "recommendation": "Approve with standard monitoring" if score >= 75 
                             else "Enhanced monitoring required" if score >= 50
                             else "High risk - Legal escalation recommended"
        },
        "created_at": datetime.utcnow().isoformat()
    }

    return profile

# ======================================================
# API ENDPOINTS
# ======================================================

@app.get("/api/search")
async def search_by_email(email: str, request: Request):
    """Search by email - creates profile if doesn't exist"""
    if "@" not in email:
        raise HTTPException(status_code=400, detail="Invalid email format")

    email_lower = email.lower().strip()
    
    if email_lower not in APPLICANTS_DB:
        APPLICANTS_DB[email_lower] = generate_profile(email_lower)

    return APPLICANTS_DB[email_lower]

@app.get("/api/applicants")
async def get_applicants(limit: int = 50):
    """Get all applicants with realistic emails"""
    
    # Generate realistic email addresses if database is small
    email_templates = [
        # Gmail addresses
        "chidi.okonkwo@gmail.com",
        "amina.hassan@gmail.com",
        "michael.johnson@gmail.com",
        "sarah.williams@gmail.com",
        "rajesh.kumar@gmail.com",
        "priya.sharma@gmail.com",
        "tunde.adeyemi@gmail.com",
        "blessing.okeke@gmail.com",
        "wanjiru.kamau@gmail.com",
        "otieno.onyango@gmail.com",
        # Yahoo addresses
        "james.brown@yahoo.com",
        "emily.davis@yahoo.com",
        "david.miller@yahoo.com",
        "jessica.wilson@yahoo.com",
        # Outlook addresses
        "oliver.smith@outlook.com",
        "emma.jones@outlook.com",
        "harry.taylor@outlook.com",
        "sophie.davies@outlook.com",
        # Hotmail
        "ngozi.nwosu@hotmail.com",
        "emeka.eze@hotmail.com",
        "oluwaseun.adeleke@hotmail.com",
        # iCloud
        "george.brown@icloud.com",
        "charlotte.wilson@icloud.com",
        # Professional domains
        "amit.patel@protonmail.com",
        "sneha.reddy@protonmail.com",
        "arjun.singh@protonmail.com",
        "kavya.gupta@protonmail.com",
        "chiamaka.nnamdi@gmail.com",
        "njeri.wambui@gmail.com",
        "kamau.mwangi@gmail.com",
        "akinyi.odhiambo@gmail.com",
        # Additional realistic emails
        "john.smith123@gmail.com",
        "mary.johnson45@yahoo.com",
        "robert.williams78@outlook.com",
        "linda.brown21@gmail.com",
        "william.jones89@hotmail.com",
        "elizabeth.taylor34@icloud.com",
        "thomas.davis56@gmail.com",
        "sarah.miller90@yahoo.com",
        "joseph.anderson12@outlook.com",
        "jessica.thomas67@gmail.com",
        "christopher.jackson43@hotmail.com",
        "ashley.white29@icloud.com",
        "matthew.harris81@gmail.com",
        "amanda.martin52@yahoo.com",
        "daniel.thompson74@outlook.com",
        "stephanie.garcia36@gmail.com",
        "joshua.martinez95@hotmail.com",
        "michelle.rodriguez18@icloud.com"
    ]
    
    # Ensure we have enough profiles
    while len(APPLICANTS_DB) < min(limit, len(email_templates)):
        for email in email_templates:
            if email not in APPLICANTS_DB:
                APPLICANTS_DB[email] = generate_profile(email)
            if len(APPLICANTS_DB) >= limit:
                break
    
    all_applicants = list(APPLICANTS_DB.values())[:limit]
    
    return {
        "total": len(all_applicants),
        "applicants": all_applicants
    }

@app.get("/api/applicant/{applicant_id}")
async def get_applicant_detail(applicant_id: str):
    """Get applicant by ID"""
    for email, profile in APPLICANTS_DB.items():
        if profile["id"] == applicant_id:
            return profile
    
    raise HTTPException(status_code=404, detail="Applicant not found")

@app.get("/api/stats")
async def get_statistics():
    """Get system statistics"""
    if not APPLICANTS_DB:
        # Generate some initial data
        for i in range(20):
            fake_email = f"user{random.randint(10000,99999)}@mail.com"
            APPLICANTS_DB[fake_email] = generate_profile(fake_email)
    
    total = len(APPLICANTS_DB)
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    
    for profile in APPLICANTS_DB.values():
        risk_counts[profile["risk_level"]] += 1
    
    return {
        "total_applicants": total,
        "active_defaults": risk_counts["High"],
        "high_risk_percentage": f"{(risk_counts['High'] / total * 100):.1f}%" if total > 0 else "0%"
    }

@app.get("/health")
async def health_check():
    """Health check"""
    return {
        "status": "healthy",
        "applicants_loaded": len(APPLICANTS_DB),
        "timestamp": datetime.utcnow().isoformat()
    }
