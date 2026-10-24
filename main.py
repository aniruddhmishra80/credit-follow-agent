from data_loader import load_data
from tone_selector import get_tone_stage
from email_generator import generate_email
from sender import dispatch_email
from audit_logger import log_action

def run_agent():
    print("Starting Credit Follow-up Agent...\n")
    invoices = load_data()
    
    stats = {"Sent": 0, "Escalated": 0, "Skipped": 0}
    
    for inv in invoices:
        print(f"Processing {inv['invoice_no']} ({inv['client_name']}) - {inv['days_overdue']} days overdue...")
        
        # 1. Get Tone Stage
        tone_data = get_tone_stage(inv['days_overdue'])
        
        if tone_data['status'] == "NOT_DUE":
            print("  -> Invoice not yet due. Skipping.\n")
            stats["Skipped"] += 1
            continue
            
        if tone_data['status'] == "ESCALATE":
            print("  -> [ALERT] 30+ days overdue! Flagging for manual ESCALATION.\n")
            log_action(inv['invoice_no'], inv['client_name'], tone_data['stage'], "ESCALATED", "N/A", "escalated")
            stats["Escalated"] += 1
            continue
            
        # 2. Generate Email via Gemini
        print(f"  -> Drafting {tone_data['tone']} email...")
        email_content = generate_email(inv, tone_data)
        
        if not email_content:
            print("  -> AI Generation failed. Skipping.\n")
            stats["Skipped"] += 1
            continue
            
        # 3. Send / Dry-Run Email
        send_status = dispatch_email(inv['contact_email'], email_content['subject'], email_content['body'])
        
        # 4. Log to Audit
        log_action(
            inv['invoice_no'], 
            inv['client_name'], 
            tone_data['stage'], 
            tone_data['tone'], 
            email_content['subject'], 
            send_status
        )
        print("  -> Logged to audit.\n")
        stats["Sent"] += 1

    print("="*40)
    print(f"Run Complete! Sent: {stats['Sent']} | Escalated: {stats['Escalated']} | Skipped: {stats['Skipped']}")
    print("="*40)

if __name__ == "__main__":
    run_agent()