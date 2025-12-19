from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, List, Optional
import json
import os
from datetime import datetime
import random

app = FastAPI(
    title="ApexScore Risk Prediction System",
    description="PRD-Compliant AI Loan Risk Assessment for Risk Analysts",
    version="1.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === PRD DATA MODELS ===

class TraditionalFinancialData(BaseModel):
    """TFD - Traditional Financial Data (Section 2.1)"""
    loan_history: List[Dict]  # TFD-1: Loan Collection History
    outstanding_debt: float     # TFD-2: Total Outstanding Debt
    currency: str
    repayment_history: List[Dict]  # TFD-3: Repayment History Log

class BehavioralStabilityIndicators(BaseModel):
    """BSI - Behavioral Stability Indicators (Section 2.2)"""
    location_consistency: int   # BSI-1: 0-100
    ip_vs_address: int         # BSI-2: 0-100
    device_stability: int       # BSI-3: 0-100
    sim_changes: int           # BSI-4: 0-100
    travel_frequency: int      # BSI-5: 0-100 (lower is better)

class ApplicantProfile(BaseModel):
    """Complete applicant profile for risk analysts"""
    id: int
    name: str
    phone: str
    email: str
    occupation: str
    location: Dict
    tfd: TraditionalFinancialData
    bsi: BehavioralStabilityIndicators
    apex_score: int
    risk_level: str

# === DATABASE ===

APPLICANTS_DB = {}

def load_sample_data():
    """Load PRD-compliant sample data"""
    global APPLICANTS_DB
    
    APPLICANTS_DB = {
        1: {
            "id": 1,
            "name": "Chidi Okonkwo",
            "phone": "+234 801 234 5678",
            "email": "chidi.okonkwo@email.com",
            "occupation": "Shop Owner",
            "location": {
                "city": "Lagos",
                "country": "Nigeria",
                "region": "West Africa",
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
            "risk_level": "Low"
        },
        2: {
            "id": 2,
            "name": "Amina Hassan",
            "phone": "+254 712 345 678",
            "email": "amina.hassan@email.com",
            "occupation": "Market Vendor",
            "location": {
                "city": "Nairobi",
                "country": "Kenya",
                "region": "East Africa",
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
            "risk_level": "Medium"
        },
        3: {
            "id": 3,
            "name": "Kwame Boateng",
            "phone": "+233 24 567 8901",
            "email": "kwame.b@email.com",
            "occupation": "Taxi Driver",
            "location": {
                "city": "Accra",
                "country": "Ghana",
                "region": "West Africa",
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

load_sample_data()

# === API ENDPOINTS ===

@app.get("/")
def serve_dashboard():
    """Serve the risk analyst dashboard"""
    if os.path.exists('dashboard.html'):
        return FileResponse('dashboard.html')
    return {
        "message": "ApexScore Risk Prediction System API",
        "version": "1.0",
        "prd_version": "1.0",
        "target_users": "Loan Officers and Risk Analysts",
        "endpoints": {
            "dashboard": "/",
            "applicants": "GET /api/applicants",
            "applicant_detail": "GET /api/applicant/{id}",
            "calculate_score": "POST /api/calculate-score",
            "high_risk": "GET /api/high-risk",
            "default_actions": "GET /api/default-actions/{id}",
            "stats": "GET /api/stats"
        }
    }

@app.get("/api/applicants")
def get_all_applicants(risk_level: Optional[str] = None):
    """
    FR 3.1.1: Client History Display
    Get all applicants with their ApexScore
    """
    applicants = []
    
    for app_id, app_data in APPLICANTS_DB.items():
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
    
    return {
        "total": len(applicants),
        "applicants": applicants
    }

@app.get("/api/applicant/{applicant_id}")
def get_applicant_detail(applicant_id: int):
    """
    FR 3.1.1, FR 3.1.2: Complete applicant profile with TFD and BSI
    FR 3.1.3: BSI breakdown available
    """
    if applicant_id not in APPLICANTS_DB:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    app_data = APPLICANTS_DB[applicant_id]
    
    # FR 3.3.2: Check for defaults and generate action recommendation
    has_default = any(r["status"] == "default" for r in app_data["tfd"]["repayment_history"])
    action_recommendation = generate_action_recommendation(
        app_data["apex_score"], 
        app_data["bsi"], 
        has_default
    )
    
    return {
        **app_data,
        "has_default": has_default,
        "action_recommendation": action_recommendation,
        "calculation_timestamp": datetime.now().isoformat(),
        "model_version": "1.0"
    }

@app.get("/api/applicant/{applicant_id}/bsi-breakdown")
def get_bsi_breakdown(applicant_id: int):
    """
    FR 3.1.3: BSI Transparency View
    Analysts can view how BSI factors contributed to the score
    """
    if applicant_id not in APPLICANTS_DB:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    app_data = APPLICANTS_DB[applicant_id]
    bsi = app_data["bsi"]
    
    return {
        "applicant_id": applicant_id,
        "applicant_name": app_data["name"],
        "apex_score": app_data["apex_score"],
        "bsi_breakdown": {
            "BSI-1: Location Consistency": {
                "score": bsi["location_consistency"],
                "weight": "30%",
                "contribution": round(bsi["location_consistency"] * 0.3, 1),
                "description": "Consistency of city/region over time"
            },
            "BSI-2: IP vs Declared Address": {
                "score": bsi["ip_vs_address"],
                "weight": "20%",
                "contribution": round(bsi["ip_vs_address"] * 0.2, 1),
                "description": "Device IP region matches declared address"
            },
            "BSI-3: Device Stability": {
                "score": bsi["device_stability"],
                "weight": "20%",
                "contribution": round(bsi["device_stability"] * 0.2, 1),
                "description": "Frequency of primary device changes"
            },
            "BSI-4: SIM Changes": {
                "score": bsi["sim_changes"],
                "weight": "15%",
                "contribution": round(bsi["sim_changes"] * 0.15, 1),
                "description": "SIM card turnover frequency"
            },
            "BSI-5: Travel Frequency": {
                "score": 100 - bsi["travel_frequency"],
                "weight": "15%",
                "contribution": round((100 - bsi["travel_frequency"]) * 0.15, 1),
                "description": "Travel outside home region (lower is better)"
            }
        }
    }

@app.post("/api/calculate-score")
def calculate_apex_score(bsi: BehavioralStabilityIndicators):
    """
    FR 3.1.2: Risk Score Synthesis
    Calculate ApexScore from BSI inputs (0-100, where 100 is low risk)
    NFR 4.3: Must be near-instantaneous (< 500ms)
    """
    # Calculate weighted score
    score = (
        bsi.location_consistency * 0.30 +
        bsi.ip_vs_address * 0.20 +
        bsi.device_stability * 0.20 +
        bsi.sim_changes * 0.15 +
        (100 - bsi.travel_frequency) * 0.15
    )
    
    apex_score = round(score)
    risk_level = determine_risk_level(apex_score)
    
    return {
        "apex_score": apex_score,
        "risk_level": risk_level,
        "calculation_time_ms": "<500ms",
        "model_version": "1.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/high-risk")
def get_high_risk_applicants(threshold: int = 40):
    """
    FR 3.3.1: Default Prediction Trigger
    Flag clients with ApexScore below threshold as High Risk for Default
    """
    high_risk = []
    
    for app_id, app_data in APPLICANTS_DB.items():
        if app_data["apex_score"] < threshold:
            has_default = any(r["status"] == "default" for r in app_data["tfd"]["repayment_history"])
            
            high_risk.append({
                "id": app_data["id"],
                "name": app_data["name"],
                "apex_score": app_data["apex_score"],
                "location": f"{app_data['location']['city']}, {app_data['location']['country']}",
                "outstanding_debt": f"{app_data['tfd']['currency']} {app_data['tfd']['outstanding_debt']:,.0f}",
                "has_default": has_default,
                "urgency": "CRITICAL" if has_default else "HIGH"
            })
    
    return {
        "threshold": threshold,
        "high_risk_count": len(high_risk),
        "applicants": sorted(high_risk, key=lambda x: x["apex_score"])
    }

@app.get("/api/default-actions/{applicant_id}")
def get_default_action_recommendation(applicant_id: int):
    """
    FR 3.3.2: Refusal/Default Scenario Handling
    Recommend next best action based on BSI for defaulted clients
    """
    if applicant_id not in APPLICANTS_DB:
        raise HTTPException(status_code=404, detail="Applicant not found")
    
    app_data = APPLICANTS_DB[applicant_id]
    has_default = any(r["status"] == "default" for r in app_data["tfd"]["repayment_history"])
    
    if not has_default:
        return {
            "applicant_id": applicant_id,
            "has_default": False,
            "message": "No default detected for this applicant"
        }
    
    action = generate_action_recommendation(
        app_data["apex_score"],
        app_data["bsi"],
        has_default
    )
    
    return {
        "applicant_id": applicant_id,
        "applicant_name": app_data["name"],
        "apex_score": app_data["apex_score"],
        "has_default": True,
        **action
    }

@app.get("/api/stats")
def get_system_statistics():
    """System-wide statistics for dashboard"""
    total = len(APPLICANTS_DB)
    risk_counts = {"High": 0, "Medium": 0, "Low": 0}
    defaults = 0
    
    for app_data in APPLICANTS_DB.values():
        risk_counts[app_data["risk_level"]] += 1
        if any(r["status"] == "default" for r in app_data["tfd"]["repayment_history"]):
            defaults += 1
    
    return {
        "total_applicants": total,
        "risk_distribution": risk_counts,
        "active_defaults": defaults,
        "high_risk_percentage": f"{(risk_counts['High'] / total * 100):.1f}%"
    }

# === HELPER FUNCTIONS ===

def determine_risk_level(score: int) -> str:
    """Determine risk level from ApexScore"""
    if score >= 75:
        return "Low"
    elif score >= 50:
        return "Medium"
    else:
        return "High"

def generate_action_recommendation(score: int, bsi: Dict, has_default: bool) -> Dict:
    """
    FR 3.3.2: Generate action recommendation based on ApexScore and BSI
    """
    if score < 40:
        # High risk for default
        if bsi["location_consistency"] > 70 and bsi["device_stability"] > 70:
            return {
                "action_type": "CONTACT_VIA_REGISTERED_CHANNELS",
                "priority": "HIGH",
                "recommendation": "High BSI: Stable Location & Device suggests successful contact via registered address/device. Recommend final registered communication.",
                "rationale": f"Location Consistency: {bsi['location_consistency']}/100, Device Stability: {bsi['device_stability']}/100",
                "next_steps": [
                    "Send registered mail to declared address",
                    "Contact via primary phone number",
                    "Email to registered email address",
                    "Schedule in-person visit if no response within 7 days"
                ]
            }
        else:
            return {
                "action_type": "LEGAL_ESCALATION",
                "priority": "CRITICAL",
                "recommendation": "Low BSI: High SIM/Travel changes suggest difficulty locating client. Recommend legal escalation.",
                "rationale": f"Location Consistency: {bsi['location_consistency']}/100, SIM Stability: {bsi['sim_changes']}/100",
                "next_steps": [
                    "Initiate legal proceedings immediately",
                    "Engage debt collection agency",
                    "File with credit bureau",
                    "Consider asset seizure if applicable"
                ]
            }
    elif score < 75:
        return {
            "action_type": "ENHANCED_MONITORING",
            "priority": "MEDIUM",
            "recommendation": "Medium risk. Approve with enhanced monitoring and periodic check-ins.",
            "next_steps": [
                "Schedule monthly payment reviews",
                "Limit loan amount to 75% of requested",
                "Require additional collateral"
            ]
        }
    else:
        return {
            "action_type": "STANDARD_APPROVAL",
            "priority": "LOW",
            "recommendation": "Low risk. Proceed with standard loan approval and monitoring.",
            "next_steps": [
                "Standard approval process",
                "Quarterly payment reviews",
                "Standard terms and conditions"
            ]
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
