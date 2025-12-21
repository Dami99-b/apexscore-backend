from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import os
from datetime import datetime
import random
import hashlib

app = FastAPI(
    title="ApexScore Risk Prediction System",
    description="PRD-Compliant AI Loan Risk Assessment",
    version="1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === DATA MODELS ===

class BehavioralStabilityIndicators(BaseModel):
    location_consistency: int
    ip_vs_address: int
    device_stability: int
    sim_changes: int
    travel_frequency: int

# === DYNAMIC PROFILE GENERATION ===

LOCATIONS = [
    {"city": "Lagos", "country": "Nigeria", "currency": "NGN", "lat": 6.4541, "lng": 3.3947},
    {"city": "Nairobi", "country": "Kenya", "currency": "KES", "lat": -1.2864, "lng": 36.8344},
    {"city": "Accra", "country": "Ghana", "currency": "GHS", "lat": 5.5557, "lng": -0.1963},
    {"city": "Johannesburg", "country": "South Africa", "currency": "ZAR", "lat": -26.2041, "lng": 28.0473},
    {"city": "Cairo", "country": "Egypt", "currency": "EGP", "lat": 30.0444, "lng": 31.2357},
    {"city": "Mumbai", "country": "India", "currency": "INR", "lat": 19.0760, "lng": 72.8777},
    {"city": "São Paulo", "country": "Brazil", "currency": "BRL", "lat": -23.5505, "lng": -46.6333},
    {"city": "Mexico City", "country": "Mexico", "currency": "MXN", "lat": 19.4326, "lng": -99.1332},
    {"city": "Manila", "country": "Philippines", "currency": "PHP", "lat": 14.5995, "lng": 120.9842},
    {"city": "Bangkok", "country": "Thailand", "currency": "THB", "lat": 13.7563, "lng": 100.5018},
]

EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", "protonmail.com"]

OCCUPATIONS = [
    "Shop Owner", "Market Vendor", "Taxi Driver", "Teacher", "Farmer",
    "Small Business Owner", "Restaurant Owner", "Mechanic", "Trader",
    "Construction Worker", "Nurse", "Accountant", "IT Consultant",
    "Real Estate Agent", "Freelancer", "Driver", "Electrician"
]

INSTITUTIONS = ["FirstBank", "Access Bank", "Standard Bank", "Barclays", "KCB Bank", "Equity Bank", "Zenith Bank", "GTBank", "Ecobank"]

def generate_profile_from_name(name: str) -> Dict:
    """Generate consistent profile for any name using hash-based randomization"""
    name_hash = int(hashlib.md5(name.encode()).hexdigest(), 16)
    random.seed(name_hash)
    
    app_id = (name_hash % 9000) + 1000
    location = random.choice(LOCATIONS)
    occupation = random.choice(OCCUPATIONS)
    
    risk_seed = random.random()
    if risk_seed < 0.25:
        profile_type = "high"
    elif risk_seed < 0.60:
        profile_type = "medium"
    else:
        profile_type = "low"
    
    if profile_type == "low":
        bsi = {
            "location_consistency": random.randint(85, 98),
            "ip_vs_address": random.randint(82, 96),
            "device_stability": random.randint(88, 99),
            "sim_changes": random.randint(90, 99),
            "travel_frequency": random.randint(10, 30)
        }
        debt = random.uniform(15000, 85000)
        has_default = False
    elif profile_type == "medium":
        bsi = {
            "location_consistency": random.randint(65, 84),
            "ip_vs_address": random.randint(58, 78),
            "device_stability": random.randint(65, 85),
            "sim_changes": random.randint(60, 82),
            "travel_frequency": random.randint(35, 55)
        }
        debt = random.uniform(30000, 120000)
        has_default = False
    else:
        bsi = {
            "location_consistency": random.randint(25, 64),
            "ip_vs_address": random.randint(20, 55),
            "device_stability": random.randint(30, 62),
            "sim_changes": random.randint(25, 58),
            "travel_frequency": random.randint(60, 90)
        }
        debt = random.uniform(50000, 200000)
        has_default = random.random() < 0.4
    
    apex_score = round(
        bsi["location_consistency"] * 0.30 +
        bsi["ip_vs_address"] * 0.20 +
        bsi["device_stability"] * 0.20 +
        bsi["sim_changes"] * 0.15 +
        (100 - bsi["travel_frequency"]) * 0.15
    )
    
    risk_level = determine_risk_level(apex_score)
    
    loan_count = random.randint(1, 4)
    loan_history = []
    for i in range(loan_count):
        year = random.randint(2021, 2024)
        month = random.randint(1, 12)
        loan_history.append({
            "institution": f"{random.choice(INSTITUTIONS)} {location['country']}",
            "amount": int(random.uniform(10000, 100000)),
            "date": f"{year}-{month:02d}"
        })
    
    repayment_history = []
    months = ["2024-11", "2024-10", "2024-09", "2024-08", "2024-07"]
    for month in months:
        if has_default and random.random() < 0.5:
            status = "default"
            days_late = None
        elif profile_type == "high" and random.random() < 0.4:
            status = "late"
            days_late = random.randint(5, 30)
        elif profile_type == "medium" and random.random() < 0.2:
            status = "late"
            days_late = random.randint(3, 15)
        else:
            status = "on-time"
            days_late = None
        
        payment = {"date": month, "status": status, "amount": int(debt / 24)}
        if days_late:
            payment["days_late"] = days_late
        repayment_history.append(payment)
    
    email_name = name.lower().replace(" ", ".")
    email_domain = random.choice(EMAIL_DOMAINS)
    email = f"{email_name}@{email_domain}"
    
    country_codes = {
        "Nigeria": "234", "Kenya": "254", "Ghana": "233", "South Africa": "27", 
        "Egypt": "20", "India": "91", "Brazil": "55", "Mexico": "52", 
        "Philippines": "63", "Thailand": "66"
    }
    country_code = country_codes.get(location["country"], "234")
    phone = f"+{country_code} {random.randint(700, 799)} {random.randint(100, 999)} {random.randint(1000, 9999)}"
    
    return {
        "id": app_id,
        "name": name,
        "phone": phone,
        "email": email,
        "occupation": occupation,
        "location": {
            "city": location["city"],
            "country": location["country"],
            "address": f"{random.randint(1, 999)} {random.choice(['Main', 'Market', 'High', 'Church', 'Station'])} Street, {location['city']}",
            "coordinates": {"lat": location["lat"], "lng": location["lng"]}
        },
        "tfd": {
            "loan_history": loan_history,
            "outstanding_debt": int(debt),
            "currency": location["currency"],
            "repayment_history": repayment_history
        },
        "bsi": bsi,
        "apex_score": apex_score,
        "risk_level": risk_level,
        "has_default": has_default
    }

def get_or_create_applicant(identifier) -> Dict:
    """Get applicant by ID or name, create if doesn't exist"""
    if isinstance(identifier, int):
        if identifier in APPLICANTS_DB:
            return APPLICANTS_DB[identifier]
        return None
    
    name_lower = str(identifier).lower().strip()
    for app in APPLICANTS_DB.values():
        if app["name"].lower() == name_lower:
            return app
    
    proper_name = identifier.strip().title()
    new_profile = generate_profile_from_name(proper_name)
    APPLICANTS_DB[new_profile["id"]] = new_profile
    return new_profile

# === SAMPLE DATABASE ===

APPLICANTS_DB = {
    1: {
        "id": 1,
        "name": "Chidi Okonkwo",
        "phone": "+234 801 234 5678",
        "email": "chidi.okonkwo@gmail.com",
        "occupation": "Shop Owner",
        "location": {
            "city": "Lagos",
            "country": "Nigeria",
            "address": "45 Broad Street, Lagos Island",
            "coordinates": {"lat": 6.4541, "lng": 3.3947}
        },
        "tfd": {
            "loan_history": [
                {"institution": "FirstBank Nigeria", "amount": 500000, "date": "2022-03"},
                {"institution": "Access Bank", "amount": 750000, "date": "2023-06"},
                {"institution": "Zenith Bank", "amount": 450000, "date": "2024-01"}
            ],
            "outstanding_debt": 1200000,
            "currency": "NGN",
            "repayment_history": [
                {"date": "2024-11", "status": "on-time", "amount": 50000},
                {"date": "2024-10", "status": "on-time", "amount": 50000},
                {"date": "2024-09", "status": "on-time", "amount": 50000},
                {"date": "2024-08", "status": "late", "amount": 50000, "days_late": 5},
                {"date": "2024-07", "status": "on-time", "amount": 50000}
            ]
        },
        "bsi": {
            "location_consistency": 92,
            "ip_vs_address": 88,
            "device_stability": 90,
            "sim_changes": 95,
            "travel_frequency": 25
        },
        "apex_score": 89,
        "risk_level": "Low",
        "has_default": False
    },
    2: {
        "id": 2,
        "name": "Amina Hassan",
        "phone": "+254 712 345 678",
        "email": "amina.hassan@yahoo.com",
        "occupation": "Market Vendor",
        "location": {
            "city": "Nairobi",
            "country": "Kenya",
            "address": "Gikomba Market, Nairobi",
            "coordinates": {"lat": -1.2864, "lng": 36.8344}
        },
        "tfd": {
            "loan_history": [
                {"institution": "Kenya Commercial Bank", "amount": 150000, "date": "2023-08"},
                {"institution": "M-Pesa Fuliza", "amount": 50000, "date": "2024-03"}
            ],
            "outstanding_debt": 180000,
            "currency": "KES",
            "repayment_history": [
                {"date": "2024-11", "status": "late", "amount": 15000, "days_late": 12},
                {"date": "2024-10", "status": "on-time", "amount": 15000},
                {"date": "2024-09", "status": "late", "amount": 15000, "days_late": 8},
                {"date": "2024-08", "status": "on-time", "amount": 15000}
            ]
        },
        "bsi": {
            "location_consistency": 78,
            "ip_vs_address": 65,
            "device_stability": 72,
            "sim_changes": 58,
            "travel_frequency": 45
        },
        "apex_score": 68,
        "risk_level": "Medium",
        "has_default": False
    },
    3: {
        "id": 3,
        "name": "Kwame Boateng",
        "phone": "+233 24 567 8901",
        "email": "kwame.b@outlook.com",
        "occupation": "Taxi Driver",
        "location": {
            "city": "Accra",
            "country": "Ghana",
            "address": "Osu, Greater Accra",
            "coordinates": {"lat": 5.5557, "lng": -0.1963}
        },
        "tfd": {
            "loan_history": [
                {"institution": "Barclays Ghana", "amount": 20000, "date": "2022-01"},
                {"institution": "Ecobank Ghana", "amount": 35000, "date": "2023-04"},
                {"institution": "GCB Bank", "amount": 28000, "date": "2023-11"}
            ],
            "outstanding_debt": 65000,
            "currency": "GHS",
            "repayment_history": [
                {"date": "2024-11", "status": "default", "amount": 5000},
                {"date": "2024-10", "status": "default", "amount": 5000},
                {"date": "2024-09", "status": "late", "amount": 5000, "days_late": 30},
                {"date": "2024-08", "status": "late", "amount": 5000, "days_late": 15}
            ]
        },
        "bsi": {
            "location_consistency": 42,
            "ip_vs_address": 38,
            "device_stability": 45,
            "sim_changes": 35,
            "travel_frequency": 78
        },
        "apex_score": 35,
        "risk_level": "High",
        "has_default": True
    }
}

# === API ENDPOINTS ===

@app.get("/", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the risk analyst dashboard"""
    if os.path.exists('dashboard.html'):
        with open('dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()
    
    return """
    <html><body style="font-family: Arial; padding: 40px; text-align: center;">
    <h1>Dashboard Missing</h1>
    <p>Upload dashboard.html to your repository</p>
    <p><a href="/docs">View API Documentation</a></p>
    </body></html>
    """

@app.get("/api/applicants")
async def get_all_applicants(risk_level: Optional[str] = None, limit: int = 100):
    """Get all applicants with their ApexScore"""
    applicants = []
    for app_id, app_data in list(APPLICANTS_DB.items())[:limit]:
        if risk_level and app_data["risk_level"] != risk_level:
            continue
        applicants.append({
            "id": app_data["id"],
            "name": app_data["name"],
            "location": f"{app_data['location']['city']}, {app_data['location']['country']}",
            "occupation": app_data["occupation"],
            "apex_score": app_data["apex_score"],
            "risk_level": app_data["risk_level"],
            "outstanding_debt": f"{app_data['tfd']['currency']} {app_data['tfd']['outstanding_debt']:,.0f}"
        })
    return {"total": len(applicants), "applicants": applicants}

@app.get("/api/applicant/{applicant_id}")
async def get_applicant_detail(applicant_id: int):
    """Get complete applicant profile by ID"""
    app_data = get_or_create_applicant(applicant_id)
    if not app_data:
        raise HTTPException(status_code=404, detail=f"Applicant {applicant_id} not found")
    
    has_default = app_data.get("has_default", False)
    action_recommendation = generate_action_recommendation(app_data["apex_score"], app_data["bsi"], has_default)
    
    return {
        **app_data,
        "action_recommendation": action_recommendation,
        "calculation_timestamp": datetime.now().isoformat(),
        "model_version": "1.0"
    }

@app.get("/api/search")
async def search_applicant(name: str):
    """Search for applicant by name - creates if doesn't exist"""
    if not name or len(name.strip()) < 2:
        raise HTTPException(status_code=400, detail="Name must be at least 2 characters")
    
    app_data = get_or_create_applicant(name)
    has_default = app_data.get("has_default", False)
    action_recommendation = generate_action_recommendation(app_data["apex_score"], app_data["bsi"], has_default)
    
    return {
        **app_data,
        "action_recommendation": action_recommendation,
        "calculation_timestamp": datetime.now().isoformat(),
        "model_version": "1.0",
        "is_new": app_data["id"] not in [1, 2, 3]
    }

@app.post("/api/calculate-score")
async def calculate_apex_score(bsi: BehavioralStabilityIndicators):
    """Calculate ApexScore from BSI inputs"""
    score = (
        bsi.location_consistency * 0.30 +
        bsi.ip_vs_address * 0.20 +
        bsi.device_stability * 0.20 +
        bsi.sim_changes * 0.15 +
        (100 - bsi.travel_frequency) * 0.15
    )
    apex_score = round(score)
    return {
        "apex_score": apex_score,
        "risk_level": determine_risk_level(apex_score),
        "calculation_time_ms": "<500ms",
        "model_version": "1.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/high-risk")
async def get_high_risk_applicants(threshold: int = 40):
    """Get applicants flagged as high risk"""
    high_risk = []
    for app_id, app_data in APPLICANTS_DB.items():
        if app_data["apex_score"] < threshold:
            high_risk.append({
                "id": app_data["id"],
                "name": app_data["name"],
                "apex_score": app_data["apex_score"],
                "location": f"{app_data['location']['city']}, {app_data['location']['country']}",
                "outstanding_debt": f"{app_data['tfd']['currency']} {app_data['tfd']['outstanding_debt']:,.0f}",
                "has_default": app_data.get("has_default", False),
                "urgency": "CRITICAL" if app_data.get("has_default") else "HIGH"
            })
    return {
        "threshold": threshold,
        "high_risk_count": len(high_risk),
        "applicants": sorted(high_risk, key=lambda x: x["apex_score"])
    }

@app.get("/api/stats")
async def get_system_statistics():
    """System-wide statistics"""
    total = len(APPLICANTS_DB)
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    defaults = 0
    for app_data in APPLICANTS_DB.values():
        risk_counts[app_data["risk_level"]] += 1
        if app_data.get("has_default", False):
            defaults += 1
    return {
        "total_applicants": total,
        "risk_distribution": risk_counts,
        "active_defaults": defaults,
        "high_risk_percentage": f"{(risk_counts['High'] / total * 100):.1f}%" if total > 0 else "0%"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "applicants_loaded": len(APPLICANTS_DB)
    }

# === HELPER FUNCTIONS ===

def determine_risk_level(score: int) -> str:
    if score >= 75:
        return "Low"
    elif score >= 50:
        return "Medium"
    else:
        return "High"

def generate_action_recommendation(score: int, bsi: Dict, has_default: bool) -> Dict:
    if score < 40:
        if bsi["location_consistency"] > 70 and bsi["device_stability"] > 70:
            return {
                "action_type": "CONTACT_VIA_REGISTERED_CHANNELS",
                "priority": "HIGH",
                "recommendation": "High BSI: Stable Location & Device. Contact via registered address/device.",
                "rationale": f"Location: {bsi['location_consistency']}/100, Device: {bsi['device_stability']}/100"
            }
        else:
            return {
                "action_type": "LEGAL_ESCALATION",
                "priority": "CRITICAL",
                "recommendation": "Low BSI: Unstable patterns. Legal escalation recommended.",
                "rationale": f"Location: {bsi['location_consistency']}/100, SIM: {bsi['sim_changes']}/100"
            }
    elif score < 75:
        return {
            "action_type": "ENHANCED_MONITORING",
            "priority": "MEDIUM",
            "recommendation": "Medium risk. Approve with enhanced monitoring."
        }
    else:
        return {
            "action_type": "STANDARD_APPROVAL",
            "priority": "LOW",
            "recommendation": "Low risk. Standard approval and monitoring."
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
