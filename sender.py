import time
import os
import mailtrap as mt
from dotenv import load_dotenv

load_dotenv()

def dispatch_email(to_email, subject, body):
    """
    Sends the email via Mailtrap Testing Sandbox API.
    """
    is_dry_run = os.getenv("DRY_RUN", "true").lower() == "true"
    
    if is_dry_run:
        print("\n" + "="*60)
        print("[DRY RUN] MODE - EMAIL INTERCEPTED AND PRINTED TO CONSOLE")
        print("="*60)
        print(f"To:      {to_email}")
        print(f"Subject: {subject}")
        print("-" * 60)
        print(body)
        print("="*60 + "\n")
        return "dry-run"
    else:
        print(f"[START] Dispatching test email to {to_email} via Mailtrap Sandbox...")
        
        token = os.getenv("MAILTRAP_API_TOKEN")
        if not token:
            print("[ERROR] MAILTRAP_API_TOKEN missing in .env file.")
            return "failed"
        
        try:
            mail = mt.Mail(
                sender=mt.Address(email="hello@example.com", name="Credit Agent"),
                to=[mt.Address(email=to_email)],
                subject=subject, 
                text=body,
                category="Integration Test",
            )

            # Use Mailtrap's Testing Sandbox with the inbox ID provided
            client = mt.MailtrapClient(
                token=token, 
                sandbox=True, 
                inbox_id="4615669"
            )
            time.sleep(1.5) # Prevent "Too many emails per second" error
            client.send(mail)
            
            print(f"[SUCCESS] Sent successfully to Mailtrap Sandbox Inbox (To: {to_email})")
            return "sent"
            
        except Exception as e:
            print(f"[ERROR] Mailtrap API failed: {e}")
            return "failed"

if __name__ == "__main__":
    dispatch_email(
        to_email="test_recipient@example.com", 
        subject="Test from Agent", 
        body="Mailtrap integration successful!"
    )