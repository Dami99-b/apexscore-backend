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

# -------------------- GLOBAL DATA --------------------

COUNTRIES = {
    "Nigeria": {
        "code": "+234",
        "currency": "NGN",
        "symbol": "₦",
        "banks": ["GTBank", "Access Bank", "First Bank", "Sterling Bank", "UBA", "Opay", "Moniepoint MFB", "PalmPay", "Kuda", "FairMoney"],
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
        "android_models": ["Samsung Galaxy S21", "Google Pixel", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "UK": {
        "code": "+44",
        "currency": "GBP",
        "symbol": "£",
        "banks": ["Barclays", "HSBC", "NatWest", "Monzo", "Revolut"],
        "isps": ["Vodafone", "O2", "EE"],
        "cities": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"],
        "android_models": ["Samsung Galaxy", "Google Pixel", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Germany": {
        "code": "+49",
        "currency": "EUR",
        "symbol": "€",
        "banks": ["Deutsche Bank", "Commerzbank", "N26"],
        "isps": ["Telekom", "Vodafone DE"],
        "cities": ["Berlin", "Hamburg", "Munich", "Frankfurt", "Cologne"],
        "android_models": ["Samsung Galaxy", "Huawei", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Canada": {
        "code": "+1",
        "currency": "CAD",
        "symbol": "C$",
        "banks": ["TD Bank", "RBC", "Scotiabank", "BMO"],
        "isps": ["Rogers", "Bell", "Telus"],
        "cities": ["Toronto", "Vancouver", "Montreal", "Calgary", "Ottawa"],
        "android_models": ["Samsung Galaxy", "Google Pixel", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Kenya": {
        "code": "+254",
        "currency": "KES",
        "symbol": "KSh",
        "banks": ["Equity Bank", "KCB", "M-Pesa", "Safaricom"],
        "isps": ["Safaricom", "Airtel Kenya", "Telkom"],
        "cities": ["Nairobi", "Mombasa", "Kisumu", "Nakuru", "Eldoret"],
        "android_models": ["Tecno", "Infinix", "Samsung A-series"],
        "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]
    },
    "Ghana": {
        "code": "+233",
        "currency": "GHS",
        "symbol": "₵",
        "banks": ["Ecobank", "GCB Bank", "MTN Mobile Money", "Stanbic Bank"],
        "isps": ["MTN Ghana", "Vodafone Ghana", "AirtelTigo"],
        "cities": ["Accra", "Kumasi", "Tamale", "Takoradi", "Cape Coast"],
        "android_models": ["Tecno", "Infinix", "Samsung"],
        "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]
    },
    "South Africa": {
        "code": "+27",
        "currency": "ZAR",
        "symbol": "R",
        "banks": ["Standard Bank", "FNB", "Absa", "Capitec"],
        "isps": ["MTN", "Vodacom", "Cell C"],
        "cities": ["Johannesburg", "Cape Town", "Durban", "Pretoria", "Port Elizabeth"],
        "android_models": ["Samsung", "Huawei", "Xiaomi"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "India": {
        "code": "+91",
        "currency": "INR",
        "symbol": "₹",
        "banks": ["SBI", "HDFC", "ICICI", "Paytm"],
        "isps": ["Jio", "Airtel", "Vi"],
        "cities": ["Mumbai", "Delhi", "Bangalore", "Hyderabad", "Chennai"],
        "android_models": ["Xiaomi", "Samsung", "Realme", "OnePlus"],
        "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]
    },
    "Brazil": {
        "code": "+55",
        "currency": "BRL",
        "symbol": "R$",
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

VALID_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]

DATABASE = {}

# -------------------- HELPERS --------------------

def is_valid_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        return False
    domain = email.split('@')[1].lower()
    return domain in VALID_EMAIL_DOMAINS

def generate_email(fn, ln):
    return f"{fn.lower()}{ln.lower()}{random.randint(1, 999)}@{random.choice(VALID_EMAIL_DOMAINS)}"

def calculate_bsi_scores(loan_history, has_defaults):
    location_consistency = random.randint(70, 95) if not has_defaults else random.randint(30, 60)
    device_stability = random.randint(65, 95) if not has_defaults else random.randint(30, 65)
    sim_changes = random.randint(60, 95) if not has_defaults else random.randint(10, 50)
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
        
        # Heavy penalty for defaults - this is critical
        if defaults > 0:
            tfd_score -= (defaults * 20)  # Increased from 15 to 20
        
        # Penalty for restructured loans
        if restructured > 0:
            tfd_score -= (restructured * 10)
        
        # Penalty for too many active loans
        if active_loans > 2:
            tfd_score -= 10
    
    # Much harsher debt penalties
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
        avg_loan = sum(loan['amount'] for loan in loan_history) / len(loan_history)
    else:
        paid_on_time = 0
        total_loans = 0
        defaults = 0
        restructured = 0
        active_loans = 0
        avg_loan = 0
    
    # If person has defaults or high debt, they should NOT get good recommendations
    if defaults >= 2 or outstanding_debt > 30000:
        # Force them into high risk category regardless of score
        max_loan = 500 if defaults >= 3 else 1000
        
        recommendation = {
            "decision": "REJECT - High Default Risk",
            "recommended_loan_amount": 0,
            "max_loan_amount": max_loan,
            "interest_rate_range": "30-40%",
            "repayment_period": "1 month maximum",
            "reasoning": [
                f"Critical Risk: ApexScore of {apex_score}/100 with {defaults} default(s)",
                f"Outstanding debt: {currency_symbol}{outstanding_debt:,} across {active_loans} active + {defaults} defaulted loans",
                f"Poor repayment history: Only {paid_on_time}/{total_loans} loans paid on time",
                f"BSI indicators: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"{restructured} loan(s) required restructuring - payment difficulty pattern detected"
            ],
            "conditions": [
                f"MUST clear at least 50% of outstanding debt ({currency_symbol}{int(outstanding_debt*0.5):,}) before reapplication",
                "Only micro-loans under {0} considered after debt clearance".format(f"{currency_symbol}{max_loan:,}"),
                "Strong collateral (2x loan value) mandatory",
                "Co-signer with verified income required",
                "Daily repayment with GPS tracking",
                "Credit counseling completion required",
                "6-month good payment history on micro-loan before larger amounts"
            ]
        }
    elif apex_score >= 75 and defaults == 0:
        max_loan = int(avg_loan * 1.5) if avg_loan > 0 else 10000
        if outstanding_debt > 0:
            max_loan = int(max_loan * 0.6)
        
        recommendation = {
            "decision": "Approve",
            "recommended_loan_amount": max_loan,
            "max_loan_amount": int(max_loan * 1.3),
            "interest_rate_range": "8-12%",
            "repayment_period": "6-12 months",
            "reasoning": [
                f"Excellent ApexScore of {apex_score}/100 indicates low default risk",
                f"Strong BSI metrics: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"Positive repayment history: {paid_on_time}/{total_loans} loans paid on time",
                f"Current debt level: {currency_symbol}{outstanding_debt:,} across {active_loans} active loans" if outstanding_debt > 0 else "No outstanding debt"
            ],
            "conditions": [
                "Verify income documentation",
                "Confirm current employment status",
                f"Collateral may be waived for amounts under {currency_symbol}5,000"
            ]
        }
    elif apex_score >= 50 and defaults <= 1:
        max_loan = int(avg_loan * 0.5) if avg_loan > 0 else 3000
        if outstanding_debt > 10000:
            max_loan = int(max_loan * 0.3)
        
        recommendation = {
            "decision": "Review Required - Conditional Approval",
            "recommended_loan_amount": max_loan,
            "max_loan_amount": int(max_loan * 1.1),
            "interest_rate_range": "18-25%",
            "repayment_period": "3-6 months",
            "reasoning": [
                f"Moderate ApexScore of {apex_score}/100 requires careful review",
                f"BSI indicators show mixed signals: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"Repayment history: {paid_on_time}/{total_loans} on-time, {defaults} default(s)",
                f"Outstanding debt: {currency_symbol}{outstanding_debt:,} must be monitored closely"
            ],
            "conditions": [
                "MANDATORY: Collateral worth 150% of loan value",
                "Co-signer with stable income required",
                f"Strict maximum: {currency_symbol}{max_loan:,}",
                "Weekly repayment schedule mandatory",
                "Income verification and bank statements (3 months)",
                f"If outstanding debt exceeds {currency_symbol}10,000, must clear 30% first"
            ]
        }
    else:
        max_loan = 500
        
        recommendation = {
            "decision": "REJECT - Unacceptable Risk",
            "recommended_loan_amount": 0,
            "max_loan_amount": max_loan,
            "interest_rate_range": "35-45%",
            "repayment_period": "1 month only",
            "reasoning": [
                f"Low ApexScore of {apex_score}/100 indicates very high default risk",
                f"Weak BSI: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"Critical payment history: {defaults} default(s), only {paid_on_time}/{total_loans} paid on time",
                f"High outstanding debt: {currency_symbol}{outstanding_debt:,}",
                "Pattern indicates high likelihood of non-repayment"
            ],
            "conditions": [
                "Loan application REJECTED",
                f"Must resolve all {defaults} defaulted loans before reapplication",
                f"Clear outstanding debt below {currency_symbol}5,000",
                "After clearance, only micro-loans (max {0}) with 200% collateral".format(f"{currency_symbol}{max_loan}"),
                "Credit counseling mandatory",
                "6-month cooling period with no new defaults required"
            ]
        }
    
    return recommendation

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
    
    # Calculate outstanding debt from active and defaulted loans
    outstanding_debt = 0
    for loan in loan_history:
        if loan['status'] == 'Active':
            outstanding_debt += loan['amount']
        elif loan['status'] == 'Defaulted':
            outstanding_debt += loan['amount']
        elif loan['status'] == 'Restructured':
            outstanding_debt += int(loan['amount'] * 0.6)  # 60% of original
    
    bsi_location, bsi_device, bsi_sim = calculate_bsi_scores(loan_history, has_defaults)
    
    apex_score = calculate_apex_score(bsi_location, bsi_device, bsi_sim, outstanding_debt, loan_history)
    
    device_type = random.choice(["Android", "iOS"])
    if device_type == "Android":
        model = random.choice(c["android_models"])
        os_version = random.choice(["Android 13", "Android 12", "Android 11"])
    else:
        model = random.choice(c["ios_models"])
        os_version = random.choice(["iOS 16", "iOS 15", "iOS 17"])
    
    city_name = random.choice(c["cities"])
    ip_matches_location = random.random() > 0.3
    
    last_email_login = (datetime.datetime.utcnow() - timedelta(hours=random.randint(1, 48))).isoformat()
    last_sim_activity = (datetime.datetime.utcnow() - timedelta(hours=random.randint(1, 72))).isoformat()

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
            "city": city_name,
            "country": country,
            "address": f"{random.randint(10, 300)} Main Street",
            "coordinates": {
                "lat": round(random.uniform(-60, 60), 4),
                "lng": round(random.uniform(-120, 120), 4)
            }
        },
        "network": {
            "isp": random.choice(c["isps"]),
            "ip_address": f"{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}.{random.randint(1, 255)}",
            "ip_location": city_name if ip_matches_location else random.choice(c["cities"]),
            "ip_matches_declared_address": ip_matches_location
        },
        "sim_registration": random.choice(["VERIFIED", "VERIFIED", "VERIFIED", "UNVERIFIED"]),
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
        "bank_accounts": [{
            "bank_name": random.choice(c["banks"]),
            "account_number": str(random.randint(1000000000, 9999999999)),
            "account_type": random.choice(["Savings", "Current"]),
            "status": random.choice(["Active", "Active", "Active", "Dormant"])
        } for _ in range(random.randint(1, 3))],
        "tfd": {
            "currency": c["currency"],
            "currency_symbol": c["symbol"],
            "outstanding_debt": outstanding_debt,
  
