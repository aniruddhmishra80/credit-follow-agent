import json
import os
from datetime import datetime

def log_action(invoice_no, client_name, stage, tone, subject, send_status, log_file="audit_log.json"):
    """Appends an email action to the JSON audit log."""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "invoice_no": invoice_no,
        "client_name": client_name,
        "stage": stage,
        "tone": tone,
        "subject": subject,
        "send_status": send_status
    }
    
    # Read existing data or start a new list
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r') as f:
                logs = json.load(f)
        except json.JSONDecodeError:
            logs = []
    else:
        logs = []
        
    logs.append(log_entry)
    
    with open(log_file, 'w') as f:
        json.dump(logs, f, indent=4)

if __name__ == "__main__":
    # Test the logger
    log_action("INV-TEST", "Test Corp", 2, "Polite but Firm", "Invoice Overdue", "dry-run")
    print("Test logged to audit_log.json")