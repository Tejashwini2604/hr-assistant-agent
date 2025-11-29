# hris_tools.py

import os
import requests
from dotenv import load_dotenv

load_dotenv()
HRIS_API_KEY = os.getenv("HRIS_API_KEY")
HRIS_API_URL = os.getenv("HRIS_API_URL")

# --- Security Note: The actual user ID must be securely passed from the front-end session ---
# For demonstration, we'll assume the LLM provides an ID.

def check_pto_balance(employee_id: str) -> dict:
    """Retrieves the employee's current paid time off (PTO) balance, 
    including vacation, sick, and casual days from the HRIS."""
    
    # 1. ACTUAL API CALL LOGIC GOES HERE:
    # headers = {"Authorization": f"Bearer {HRIS_API_KEY}"}
    # response = requests.get(f"{HRIS_API_URL}/balances/{employee_id}", headers=headers)
    # data = response.json()
    
    # 2. Mock Data for current development:
    if employee_id == "E1001":
        return {"vacation": 15, "sick": 8, "casual": 3}
    else:
        return {"error": "Employee ID not found or API failure."}

def submit_leave_request(employee_id: str, start_date: str, end_date: str, leave_type: str) -> dict:
    """Submits a formal leave request to the HRIS for manager approval."""
    
    # 1. ACTUAL API CALL LOGIC GOES HERE:
    # payload = {...}
    # response = requests.post(f"{HRIS_API_URL}/requests", json=payload)
    
    # 2. Mock Data for current development:
    if leave_type.lower() == "vacation":
        return {"status": "success", "message": f"Vacation request for {start_date} to {end_date} submitted for approval."}
    else:
        return {"status": "error", "message": "Submission failed. Check dates."}

# You would add get_benefits_summary, check_policy_eligibility, etc., here.

# A dictionary to easily map tool names to the actual functions
HRIS_TOOL_MAP = {
    "check_pto_balance": check_pto_balance,
    "submit_leave_request": submit_leave_request,
}