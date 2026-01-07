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

COUNTRIES = {
    "Nigeria": {
        "code": "+234", "currency": "NGN", "symbol": "₦",
        "banks": ["GTBank", "Access Bank", "First Bank", "Sterling Bank", "UBA", "Opay", "Moniepoint MFB", "PalmPay", "Kuda", "FairMoney"],
        "isps": ["MTN", "Airtel", "Glo", "9mobile"],
        "cities": ["Lagos", "Ibadan", "Abeokuta", "Benin City", "Onitsha"],
        "android_models": ["Tecno Spark", "Infinix Hot", "Samsung A14", "Xiaomi Redmi"],
        "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]
    },
    "USA": {
        "code": "+1", "currency": "USD", "symbol": "$",
        "banks": ["Chase", "Bank of America", "Wells Fargo", "Capital One"],
        "isps": ["Verizon", "AT&T", "T-Mobile"],
        "cities": ["New York", "Houston", "Chicago", "Dallas", "Los Angeles"],
        "android_models": ["Samsung Galaxy S21", "Google Pixel", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "UK": {
        "code": "+44", "currency": "GBP", "symbol": "£",
        "banks": ["Barclays", "HSBC", "NatWest", "Monzo", "Revolut"],
        "isps": ["Vodafone", "O2", "EE"],
        "cities": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
        "android_models": ["Samsung Galaxy", "Google Pixel", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
}

FIRST_NAMES = ["Michael", "David", "Blessing", "Fatima", "Esther", "Joseph", "Daniel", "Grace", "Amara", "Chen", "Raj", "Maria"]
LAST_NAMES = ["Anderson", "Brown", "Okoye", "Hassan", "Adeyemi", "Johnson", "Silva", "Kumar", "Wang", "Garcia"]
MIDDLE_NAMES = ["James", "Oluwaseun", "Ibrahim", "Paul", "Grace", "Abdul", "Marie", "Anne", "Luis", "Wei"]
JOBS = ["Trader", "Farmer", "POS Agent", "Ride-hailing Driver", "Market Vendor", "Tailor", "Electrician", "Teacher", "Nurse", "Shop Owner"]

LOAN_PURPOSES = ["Business Expansion", "Education", "Medical Emergency", "Rent Payment", "Inventory Purchase", "Equipment", "Working Capital", "Personal Use"]
REPAYMENT_STATUS = ["Paid On Time", "Paid Early", "Paid Late", "Defaulted", "Restructured", "Active"]
VALID_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]

DATABASE = {}

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    domain = email.split('@')[1].lower()
    return domain in VALID_EMAIL_DOMAINS

def generate_email(fn, ln):
    return f"{fn.lower()}{ln.lower()}{random.randint(1, 999)}@{random.choice(VALID_EMAIL_DOMAINS)}"

def calculate_bsi_scores(loan_history, has_defaults, sim_verified, ip_matches):
    # BSI scores should reflect actual status
    # Higher score = lower risk = more stable
    
    # Location: based on defaults
    location_consistency = random.randint(70, 95) if not has_defaults else random.randint(40, 65)
    
    # Device: based on defaults
    device_stability = random.randint(70, 95) if not has_defaults else random.randint(40, 65)
    
    # SIM: If VERIFIED, should be high (75-95), if UNVERIFIED should be low (20-45)
    if sim_verified:
        sim_changes = random.randint(75, 95)
    else:
        sim_changes = random.randint(20, 45)
    
    return location_consistency, device_stability, sim_changes

def calculate_apex_score(bsi_location, bsi_device, bsi_sim, outstanding_debt, loan_history):
    bsi_average = (bsi_location + bsi_device + bsi_sim) / 3
    bsi_component = bsi_average * 0.6
    tfd_score = 50
    
    if loan_history:
        paid_on_time = sum(1 for loan in loan_history if loan['status'] in ['Paid On Time', 'Paid Early'])
        total_completed = sum(1 for loan in loan_history if loan['status'] in ['Paid On Time', 'Paid Early', 'Paid Late', 'Defaulted', 'Restructured'])
        defaults = sum(1 for loan in loan_history if loan['status'] == 'Defaulted')
        active_loans = sum(1 for loan in loan_history if loan['status'] == 'Active')
        restructured = sum(1 for loan in loan_history if loan['status'] == 'Restructured')
        
        if total_completed > 0:
            repayment_rate = paid_on_time / total_completed
            tfd_score = repayment_rate * 100
        
        if defaults > 0:
            tfd_score -= (defaults * 20)
        if restructured > 0:
            tfd_score -= (restructured * 10)
        if active_loans > 2:
            tfd_score -= 10
    
    if outstanding_debt > 50000:
        tfd_score -= 25
    elif outstanding_debt > 30000:
        tfd_score -= 15
    elif outstanding_debt > 15000:
        tfd_score -= 10
    elif outstanding_debt > 5000:
        tfd_score -= 5
    
    tfd_score = max(0, min(100, tfd_score))
    tfd_component = tfd_score * 0.4
    apex_score = int(bsi_component + tfd_component)
    return max(30, min(95, apex_score))

def generate_ai_recommendation(apex_score, outstanding_debt, loan_history, bsi_location, bsi_device, bsi_sim, currency_symbol):
    if loan_history:
        paid_on_time = sum(1 for loan in loan_history if loan['status'] in ['Paid On Time', 'Paid Early'])
        total_loans = len(loan_history)
        defaults = sum(1 for loan in loan_history if loan['status'] == 'Defaulted')
        restructured = sum(1 for loan in loan_history if loan['status'] == 'Restructured')
        active_loans = sum(1 for loan in loan_history if loan['status'] == 'Active')
        
        # Calculate total paid amount from successfully repaid loans
        total_paid = sum(loan.get('repayment_amount', 0) for loan in loan_history if loan.get('repayment_amount'))
        avg_loan = sum(loan['amount'] for loan in loan_history) / len(loan_history)
    else:
        paid_on_time = 0
        total_loans = 0
        defaults = 0
        restructured = 0
        active_loans = 0
        total_paid = 0
        avg_loan = 0
    
    # Recommendation based on 40-50% of total successfully paid loans
    base_recommendation = int(total_paid * 0.45) if total_paid > 0 else int(avg_loan * 0.3)
    
    if defaults >= 2 or outstanding_debt > 50000:
        max_loan = min(1000, int(base_recommendation * 0.1))
        return {
            "decision": "REJECT - High Default Risk",
            "recommended_loan_amount": 0,
            "max_loan_amount": max_loan,
            "interest_rate_range": "30-40%",
            "repayment_period": "1 month maximum",
            "reasoning": [
                f"Critical Risk: ApexScore of {apex_score}/100 with {defaults} default(s)",
                f"Outstanding debt: {currency_symbol}{outstanding_debt:,} must be cleared",
                f"Payment history: {paid_on_time}/{total_loans} loans paid successfully",
                f"BSI Profile: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})"
            ],
            "conditions": [
                f"Clear at least 80% of outstanding debt first",
                f"After debt clearance, micro-loan up to {currency_symbol}{max_loan:,} with 200% collateral",
                "Co-signer with verified income mandatory",
                "Daily repayment with tracking required"
            ]
        }
    
    elif apex_score >= 70 and defaults == 0 and outstanding_debt < 20000:
        max_loan = min(int(base_recommendation * 1.2), int(avg_loan * 1.5))
        return {
            "decision": "Approve",
            "recommended_loan_amount": base_recommendation,
            "max_loan_amount": max_loan,
            "interest_rate_range": "8-12%",
            "repayment_period": "6-12 months",
            "reasoning": [
                f"Good ApexScore of {apex_score}/100 indicates reliable borrower",
                f"Strong payment record: {paid_on_time}/{total_loans} loans paid on time",
                f"Total successfully repaid: {currency_symbol}{int(total_paid):,}",
                f"Stable BSI: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"Manageable debt: {currency_symbol}{outstanding_debt:,}"
            ],
            "conditions": [
                "Income verification required",
                "Employment confirmation needed",
                f"Collateral optional for amounts under {currency_symbol}5,000"
            ]
        }
    
    elif apex_score >= 50 and defaults <= 1 and outstanding_debt < 40000:
        max_loan = int(base_recommendation * 0.8)
        return {
            "decision": "Review Required - Conditional Approval",
            "recommended_loan_amount": int(base_recommendation * 0.6),
            "max_loan_amount": max_loan,
            "interest_rate_range": "15-22%",
            "repayment_period": "3-6 months",
            "reasoning": [
                f"Moderate ApexScore of {apex_score}/100 requires assessment",
                f"Payment record: {paid_on_time}/{total_loans} successful, {defaults} default(s)",
                f"Successfully repaid: {currency_symbol}{int(total_paid):,}",
                f"BSI Review: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"Outstanding: {currency_symbol}{outstanding_debt:,} needs monitoring"
            ],
            "conditions": [
                "Collateral worth 120% required",
                f"Maximum approved: {currency_symbol}{max_loan:,}",
                "Bi-weekly repayment schedule",
                "Co-signer recommended for amounts over " + f"{currency_symbol}{int(max_loan*0.5):,}"
            ]
        }
    
    else:
        max_loan = min(2000, int(base_recommendation * 0.2))
        return {
            "decision": "REJECT - Unacceptable Risk",
            "recommended_loan_amount": 0,
            "max_loan_amount": max_loan,
            "interest_rate_range": "35-45%",
            "repayment_period": "1 month only",
            "reasoning": [
                f"Low ApexScore of {apex_score}/100 indicates high risk",
                f"Payment issues: {defaults} defaults, only {paid_on_time}/{total_loans} paid on time",
                f"Outstanding debt: {currency_symbol}{outstanding_debt:,} is excessive",
                f"Weak BSI: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})"
            ],
            "conditions": [
                "Application REJECTED",
                f"Clear all defaults and reduce debt below {currency_symbol}10,000",
                f"After 6 months good history, micro-loan up to {currency_symbol}{max_loan:,}",
                "Credit counseling mandatory"
            ]
        }

def generate_loan_history(num_loans, country_banks, currency_code, currency_symbol):
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
            "currency": currency_code,
            "currency_symbol": currency_symbol,
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

    if email is None:
        email = generate_email(fn, ln)
    
    num_loans = random.randint(5, 10)
    loan_history = generate_loan_history(num_loans, c["banks"], c["currency"], c["symbol"])
    has_defaults = any(loan['status'] == 'Defaulted' for loan in loan_history)
    
    # Calculate outstanding debt from active, defaulted, and restructured loans
    outstanding_debt = 0
    for loan in loan_history:
        if loan['status'] == 'Active':
            outstanding_debt += loan['amount']
        elif loan['status'] == 'Defaulted':
            outstanding_debt += loan['amount']
        elif loan['status'] == 'Restructured':
            outstanding_debt += int(loan['amount'] * 0.6)
    
    # Determine SIM verification status first
    sim_verified = random.choice([True, True, True, False])  # 75% verified
    
    # Determine IP match
    ip_matches_location = random.random() > 0.25  # 75% match rate
    
    # Calculate BSI scores based on actual status
    bsi_location, bsi_device, bsi_sim = calculate_bsi_scores(loan_history, has_defaults, sim_verified, ip_matches_location)
    
    # IP region match should be high if IP matches, low if not
    ip_region_match = random.randint(85, 95) if ip_matches_location else random.randint(25, 45)
    
    apex_score = calculate_apex_score(bsi_location, bsi_device, bsi_sim, outstanding_debt, loan_history)
    
    device_type = random.choice(["Android", "iOS"])
    if device_type == "Android":
        model = random.choice(c["android_models"])
        os_version = random.choice(["Android 13", "Android 12", "Android 11"])
    else:
        model = random.choice(c["ios_models"])
        os_version = random.choice(["iOS 16", "iOS 15", "iOS 17"])
    
    city_name = random.choice(c["cities"])
    last_email_login = (datetime.datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat()
    last_sim_activity = (datetime.datetime.utcnow() - timedelta(hours=random.randint(1, 72))).isoformat()
    
    # Get unique banks from loan history
    banks_used = list(set(loan['institution'] for loan in loan_history))
    
    # Create bank accounts matching loan history banks
    bank_accounts = []
    for bank in banks_used[:3]:  # Max 3 accounts
        bank_accounts.append({
            "bank_name": bank,
            "account_number": str(random.randint(1000000000, 9999999999)),
            "account_type": random.choice(["Savings", "Current"]),
            "status": random.choice(["Active", "Active", "Active", "Dormant"])
        })

    applicant = {
        "id": str(uuid.uuid4()),
        "email": email,
        "name": {"first": fn, "middle": mid, "last": ln, "full": f"{fn} {mid} {ln}"},
        "phone": f"{c['code']} {random.randint(700000000, 999999999)}",
        "occupation": random.choice(JOBS),
        "location": {
            "city": city_name,
            "country": country,
            "address": f"{random.randint(10, 300)} Main Street",
            "coordinates": {"lat": round(random.uniform(-60, 60), 4), "lng": round(random.uniform(-120, 120), 4)}
        },
        "network": {
            "isp": random.choice(c["isps"]),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "ip_location": city_name if ip_matches_location else random.choice(c["cities"]),
            "ip_matches_declared_address": ip_matches_location
        },
        "sim_registration": "VERIFIED" if sim_verified else "UNVERIFIED",
        "activity_log": {
            "last_email_login": last_email_login,
            "last_sim_activity": last_sim_activity,
            "email_sim_sync": abs((datetime.datetime.fromisoformat(last_email_login) - datetime.datetime.fromisoformat(last_sim_activity)).total_seconds()) < 86400
        },
        "device_fingerprint": {
            "device_id": str(uuid.uuid4()),
            "device_type": device_type,
            "model": model,
            "os_version": os_version,
            "is_rooted": random.choice([False, False, False, True]),
            "vpn_detected": random.choice([False, False, True]),
        },
        "bank_accounts": bank_accounts,
        "tfd": {
            "currency": c["currency"],
            "currency_symbol": c["symbol"],
            "outstanding_debt": outstanding_debt,
            "loan_history": loan_history
        },
        "bsi": {
            "location_consistency": bsi_location,
            "device_stability": bsi_device,
            "sim_changes": bsi_sim,
            "ip_region_match": ip_region_match,
            "travel_frequency": random.randint(60, 95) if not has_defaults else random.randint(40, 70)
        },
        "apex_score": apex_score,
        "risk_level": "Low" if apex_score >= 75 else "Medium" if apex_score >= 50 else "High",
        "action_recommendation": generate_ai_recommendation(apex_score, outstanding_debt, loan_history, bsi_location, bsi_device, bsi_sim, c["symbol"]),
        "created_at": datetime.datetime.utcnow().isoformat()
    }

    DATABASE[applicant["id"]] = applicant
    return applicant

for _ in range(150):
    generate_applicant()

@app.get("/")
def root():
    return {"status": "ApexScore API running", "version": "2.0"}

@app.get("/api/applicants")
def list_applicants(limit: int = 50):
    return {"applicants": list(DATABASE.values())[:limit]}

@app.get("/api/search")
def search(email: str = Query(...)):
    if not is_valid_email(email):
        raise HTTPException(status_code=400, detail=f"Invalid email format or domain. Only {', '.join(VALID_EMAIL_DOMAINS)} are accepted.")
    for applicant in DATABASE.values():
        if applicant["email"].lower() == email.lower():
            return applicant
    return generate_applicant(email)

@app.get("/api/applicant/{id}")
def get_applicant(id: str):
    applicant = DATABASE.get(id)
    if not applicant:
        raise HTTPException(status_code=404, detail="Applicant not found")
    return applicant

@app.get("/api/stats")
def stats():
    total = len(DATABASE)
    high = len([a for a in DATABASE.values() if a["risk_level"] == "High"])
    medium = len([a for a in DATABASE.values() if a["risk_level"] == "Medium"])
    low = len([a for a in DATABASE.values() if a["risk_level"] == "Low"])
    avg_score = sum(a["apex_score"] for a in DATABASE.values()) / total if total > 0 else 0
    return {
        "total_applicants": total,
        "active_defaults": high,
        "high_risk_percentage": f"{int((high/total)*100)}%" if total > 0 else "0%",
        "risk_distribution": {"high": high, "medium": medium, "low": low},
        "average_apex_score": round(avg_score, 1)
    }
