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
    "Nigeria": {"code": "+234", "currency": "NGN", "symbol": "₦", "banks": ["GTBank", "Access Bank", "First Bank", "Sterling Bank", "UBA", "Opay", "Moniepoint MFB", "PalmPay", "Kuda", "FairMoney"], "isps": ["MTN", "Airtel", "Glo", "9mobile"], "cities": ["Lagos", "Ibadan", "Abeokuta", "Benin City", "Onitsha"], "android_models": ["Tecno Spark", "Infinix Hot", "Samsung A14", "Xiaomi Redmi"], "ios_models": ["iPhone 11", "iPhone 12", "iPhone SE"]},
    "USA": {"code": "+1", "currency": "USD", "symbol": "$", "banks": ["Chase", "Bank of America", "Wells Fargo", "Capital One"], "isps": ["Verizon", "AT&T", "T-Mobile"], "cities": ["New York", "Houston", "Chicago", "Dallas", "Los Angeles"], "android_models": ["Samsung Galaxy S21", "Google Pixel", "OnePlus"], "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]},
    "UK": {"code": "+44", "currency": "GBP", "symbol": "£", "banks": ["Barclays", "HSBC", "NatWest", "Monzo", "Revolut"], "isps": ["Vodafone", "O2", "EE"], "cities": ["London", "Manchester", "Birmingham", "Leeds", "Glasgow"], "android_models": ["Samsung Galaxy", "Google Pixel", "Xiaomi"], "ios_models": ["iPhone 13", "iPhone 14", "iPhone 12"]},
}

FIRST_NAMES = ["Michael", "David", "Blessing", "Fatima", "Esther", "Joseph", "Daniel", "Grace", "Amara", "Chen", "Raj", "Maria"]
LAST_NAMES = ["Anderson", "Brown", "Okoye", "Hassan", "Adeyemi", "Johnson", "Silva", "Kumar", "Wang", "Garcia"]
MIDDLE_NAMES = ["James", "Oluwaseun", "Ibrahim", "Paul", "Grace", "Abdul", "Marie", "Anne", "Luis", "Wei"]
JOBS = ["Trader", "Farmer", "POS Agent", "Ride-hailing Driver", "Market Vendor", "Tailor", "Electrician", "Teacher", "Nurse", "Shop Owner"]
LOAN_PURPOSES = ["Business Expansion", "Education", "Medical Emergency", "Rent Payment", "Inventory Purchase", "Equipment", "Working Capital", "Personal Use"]
REPAYMENT_STATUS = ["Paid On Time", "Paid Early", "Paid Late", "Defaulted", "Restructured", "Active"]
VALID_EMAIL_DOMAINS = ["gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"]

# Credit bureaus and financial data sources
CREDIT_BUREAUS = ["Experian", "Equifax", "TransUnion", "FICO", "Credit Registry", "Central Credit Bureau"]
INCOME_SOURCES = ["Employer Payroll", "Bank Statement Analysis", "Tax Records", "Self-Reported", "Business Revenue"]
EXPENDITURE_CATEGORIES = ["Housing", "Transportation", "Food & Groceries", "Utilities", "Healthcare", "Entertainment", "Debt Repayment", "Savings", "Other"]

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
    location_consistency = random.randint(70, 95) if not has_defaults else random.randint(40, 65)
    device_stability = random.randint(70, 95) if not has_defaults else random.randint(40, 65)
    if sim_verified:
        sim_changes = random.randint(75, 95)
    else:
        sim_changes = random.randint(20, 45)
    return location_consistency, device_stability, sim_changes

def calculate_apex_score(bsi_location, bsi_device, bsi_sim, outstanding_debt, loan_history):
    bsi_average = (bsi_location + bsi_device + bsi_sim) / 3
    bsi_component = bsi_average * 0.6
    tfd_score = 60
    
    if loan_history:
        total_loans = len(loan_history)
        paid_on_time = sum(1 for loan in loan_history if loan['status'] in ['Paid On Time', 'Paid Early'])
        paid_late = sum(1 for loan in loan_history if loan['status'] == 'Paid Late')
        defaults = sum(1 for loan in loan_history if loan['status'] == 'Defaulted')
        active_loans = sum(1 for loan in loan_history if loan['status'] == 'Active')
        restructured = sum(1 for loan in loan_history if loan['status'] == 'Restructured')
        
        completed_loans = paid_on_time + paid_late
        if total_loans > 0:
            completion_rate = completed_loans / total_loans
            tfd_score = 40 + (completion_rate * 40)
        
        if defaults > 0:
            tfd_score -= (defaults * 8)
        if restructured > 0:
            tfd_score -= (restructured * 4)
        if active_loans > 3:
            tfd_score -= 5
        if paid_on_time > 0:
            on_time_bonus = min(10, paid_on_time * 2)
            tfd_score += on_time_bonus
    
    debt_ratio = outstanding_debt / 50000
    if debt_ratio > 1.5:
        tfd_score -= 12
    elif debt_ratio > 1.0:
        tfd_score -= 8
    elif debt_ratio > 0.6:
        tfd_score -= 4
    
    tfd_score = max(20, min(100, tfd_score))
    tfd_component = tfd_score * 0.4
    apex_score = int(bsi_component + tfd_component)
    return max(35, min(95, apex_score))

def generate_ai_recommendation(apex_score, outstanding_debt, loan_history, bsi_location, bsi_device, bsi_sim, currency_symbol):
    if loan_history:
        paid_on_time = sum(1 for loan in loan_history if loan['status'] in ['Paid On Time', 'Paid Early'])
        paid_late = sum(1 for loan in loan_history if loan['status'] == 'Paid Late')
        total_loans = len(loan_history)
        defaults = sum(1 for loan in loan_history if loan['status'] == 'Defaulted')
        restructured = sum(1 for loan in loan_history if loan['status'] == 'Restructured')
        active_loans = sum(1 for loan in loan_history if loan['status'] == 'Active')
        total_borrowed = sum(loan['amount'] for loan in loan_history)
        total_paid = sum(loan.get('repayment_amount', 0) for loan in loan_history if loan.get('repayment_amount'))
        avg_loan = total_borrowed / len(loan_history)
    else:
        paid_on_time = 0
        paid_late = 0
        total_loans = 0
        defaults = 0
        restructured = 0
        active_loans = 0
        total_borrowed = 0
        total_paid = 0
        avg_loan = 0
    
    if total_paid > 0:
        base_recommendation = int(total_paid * 0.45)
    else:
        base_recommendation = int(avg_loan * 0.35)
    
    if apex_score >= 70 and defaults == 0:
        recommended = base_recommendation
        max_loan = int(base_recommendation * 1.4)
        return {
            "decision": "Approve",
            "recommended_loan_amount": recommended,
            "max_loan_amount": max_loan,
            "interest_rate_range": "10-14%",
            "repayment_period": "6-12 months",
            "reasoning": [
                f"Good ApexScore of {apex_score}/100 shows reliable payment behavior",
                f"Strong payment record: {paid_on_time}/{total_loans} loans paid on time",
                f"Total successfully repaid: {currency_symbol}{int(total_paid):,}",
                f"Good BSI profile: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"Current outstanding: {currency_symbol}{outstanding_debt:,}"
            ],
            "conditions": [
                "Standard income verification",
                "Employment confirmation",
                f"Light collateral for amounts over {currency_symbol}{int(max_loan*0.6):,}"
            ]
        }
    elif apex_score >= 55 and defaults <= 1:
        recommended = int(base_recommendation * 0.7)
        max_loan = int(base_recommendation * 1.0)
        return {
            "decision": "Approve with Conditions",
            "recommended_loan_amount": recommended,
            "max_loan_amount": max_loan,
            "interest_rate_range": "16-20%",
            "repayment_period": "4-8 months",
            "reasoning": [
                f"Moderate ApexScore of {apex_score}/100 shows acceptable risk",
                f"Payment history: {paid_on_time}/{total_loans} on time, {defaults} defaults, {restructured} restructured",
                f"Successfully repaid: {currency_symbol}{int(total_paid):,}",
                f"BSI assessment: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"Outstanding balance: {currency_symbol}{outstanding_debt:,}"
            ],
            "conditions": [
                "Income and employment verification required",
                f"Collateral worth 100% for amounts over {currency_symbol}{int(recommended*0.5):,}",
                "Monthly repayment schedule",
                "Co-signer recommended for maximum amount"
            ]
        }
    elif apex_score >= 40 and defaults <= 2:
        recommended = int(base_recommendation * 0.4)
        max_loan = int(base_recommendation * 0.6)
        return {
            "decision": "Conditional Approval - High Interest",
            "recommended_loan_amount": recommended,
            "max_loan_amount": max_loan,
            "interest_rate_range": "24-30%",
            "repayment_period": "3-6 months",
            "reasoning": [
                f"Lower ApexScore of {apex_score}/100 indicates elevated risk",
                f"Mixed payment record: {paid_on_time}/{total_loans} on time, {defaults} defaults, {restructured} restructured",
                f"Repayment capacity shown: {currency_symbol}{int(total_paid):,}",
                f"BSI concerns: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})",
                f"High outstanding debt: {currency_symbol}{outstanding_debt:,}"
            ],
            "conditions": [
                f"Maximum loan strictly capped at {currency_symbol}{max_loan:,}",
                "Collateral worth 130% of loan required",
                "Co-signer with good credit mandatory",
                "Bi-weekly or weekly repayment only",
                "Address outstanding defaults before full approval"
            ]
        }
    else:
        recommended = 0
        if base_recommendation > 0:
            max_loan = int(base_recommendation * 0.15)
        else:
            max_loan = 1000
        max_loan = max(500, min(max_loan, 3000))
        return {
            "decision": "High Risk - Micro-loan Only",
            "recommended_loan_amount": recommended,
            "max_loan_amount": max_loan,
            "interest_rate_range": "32-40%",
            "repayment_period": "1-3 months",
            "reasoning": [
                f"Low ApexScore of {apex_score}/100 indicates very high risk",
                f"Poor payment history: {defaults} defaults, only {paid_on_time}/{total_loans} paid successfully",
                f"Outstanding debt of {currency_symbol}{outstanding_debt:,} is concerning",
                f"Weak BSI: Location ({bsi_location}), Device ({bsi_device}), SIM ({bsi_sim})"
            ],
            "conditions": [
                "Standard loans not approved",
                f"Only micro-loans up to {currency_symbol}{max_loan:,} after debt reduction",
                f"Must clear outstanding debt below {currency_symbol}20,000 first",
                "150% collateral mandatory",
                "Guarantor with verified income required",
                "Short-term repayment (weekly/bi-weekly)"
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
        
        repayment_amount = None
        if status in ["Paid On Time", "Paid Early", "Paid Late"]:
            repayment_amount = amount + int(amount * random.uniform(0.05, 0.25))
        
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
            "repayment_amount": repayment_amount
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
    
    outstanding_debt = 0
    for loan in loan_history:
        if loan['status'] == 'Active':
            outstanding_debt += loan['amount']
        elif loan['status'] == 'Defaulted':
            outstanding_debt += loan['amount']
    
    sim_verified = random.choice([True, True, True, False])
    ip_matches_location = random.random() > 0.25
    bsi_location, bsi_device, bsi_sim = calculate_bsi_scores(loan_history, has_defaults, sim_verified, ip_matches_location)
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
    
    banks_used = list(set(loan['institution'] for loan in loan_history))
    bank_accounts = []
    for bank in banks_used[:3]:
        bank_accounts.append({
            "bank_name": bank,
            "account_number": str(random.randint(1000000000, 9999999999)),
            "account_type": random.choice(["Savings", "Current"]),
            "status": random.choice(["Active", "Active", "Active", "Dormant"])
        })
    
    # Generate income data
    monthly_income = random.randint(1000, 15000)
    income_source = random.choice(INCOME_SOURCES)
    income_verification_date = (datetime.datetime.utcnow() - timedelta(days=random.randint(1, 90))).isoformat()
    
    # Generate expenditure breakdown
    total_expenditure = int(monthly_income * random.uniform(0.5, 0.95))
    expenditure_breakdown = {
        "Housing": int(total_expenditure * random.uniform(0.25, 0.35)),
        "Transportation": int(total_expenditure * random.uniform(0.10, 0.15)),
        "Food & Groceries": int(total_expenditure * random.uniform(0.15, 0.20)),
        "Utilities": int(total_expenditure * random.uniform(0.05, 0.10)),
        "Healthcare": int(total_expenditure * random.uniform(0.05, 0.10)),
        "Entertainment": int(total_expenditure * random.uniform(0.05, 0.08)),
        "Debt Repayment": int(outstanding_debt * 0.02) if outstanding_debt > 0 else 0,
        "Savings": max(0, monthly_income - total_expenditure),
        "Other": int(total_expenditure * random.uniform(0.03, 0.07))
    }
    
    # Generate credit report from bureau
    credit_bureau = random.choice(CREDIT_BUREAUS)
    credit_report_date = (datetime.datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat()
    credit_score = random.randint(300, 850)
    
    # Calculate debt-to-income ratio
    monthly_debt_payment = expenditure_breakdown["Debt Repayment"]
    dti_ratio = round((monthly_debt_payment / monthly_income) * 100, 2) if monthly_income > 0 else 0

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
        "financial_profile": {
            "monthly_income": monthly_income,
            "income_source": income_source,
            "income_verification_date": income_verification_date,
            "monthly_expenditure": total_expenditure,
            "expenditure_breakdown": expenditure_breakdown,
            "disposable_income": monthly_income - total_expenditure,
            "debt_to_income_ratio": dti_ratio,
            "currency": c["currency"],
            "currency_symbol": c["symbol"]
        },
        "credit_report": {
            "bureau": credit_bureau,
            "report_date": credit_report_date,
            "credit_score": credit_score,
            "credit_rating": "Excellent" if credit_score >= 750 else "Good" if credit_score >= 650 else "Fair" if credit_score >= 550 else "Poor",
            "total_credit_accounts": len(bank_accounts) + len(loan_history),
            "active_credit_lines": len([l for l in loan_history if l['status'] == 'Active']),
            "derogatory_marks": len([l for l in loan_history if l['status'] == 'Defaulted']),
            "credit_utilization": round((outstanding_debt / (monthly_income * 12)) * 100, 2) if monthly_income > 0 else 0,
            "oldest_account_age_months": random.randint(12, 120),
            "recent_inquiries": random.randint(0, 5)
        },
        "tfd": {
            "currency": c["currency"],
            "currency_symbol": c["symbol"],
            "outstanding_debt": outstanding_debt,
            "loan_history": loan_history
        },
        "bsi": {
            "location_consistency": bsi_location,
            "de
