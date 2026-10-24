import os
import json
import re
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure the Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def sanitize_input(text):
    """
    Security Guardrail: Prompt Injection mitigation.
    Strips dangerous characters and common override phrases from client data.
    """
    text = str(text)
    # Remove common injection attempts
    text = re.sub(r'(?i)(ignore previous instructions|system prompt|bypass|new rules)', '', text)
    # Strip markdown/code formatting characters
    text = text.replace('`', '').replace('{', '').replace('}', '')
    return text

def generate_email(invoice_data, tone_data):
    """
    Calls Gemini API to generate the email subject and body based on tone.
    """
    # Don't generate emails for invoices that aren't due or are escalated
    if tone_data.get("status") != "PROCESS":
        return None

    # Sanitize inputs before they hit the prompt
    safe_client = sanitize_input(invoice_data['client_name'])
    safe_amount = sanitize_input(invoice_data['amount'])
    
    # 1. Structured System Prompt
    system_instruction = f"""
    You are a professional finance collections assistant.
    Generate a payment follow-up email at the TONE LEVEL specified.
    Use ONLY the invoice data provided. Do not invent any numbers.
    Respond ONLY in valid JSON with keys: "subject" and "body".
    No preamble, no markdown fences.

    Tone level: Stage {tone_data['stage']} - {tone_data['tone']}
    CTA: {tone_data['cta']}
    """

    # 2. Clean User Data
    # Formatting date nicely for the email
    formatted_date = invoice_data['due_date'].strftime('%B %d, %Y')
    
    user_message = f"""
    Invoice No: {invoice_data['invoice_no']}
    Client: {safe_client}
    Amount: ${safe_amount}
    Due Date: {formatted_date}
    Days Overdue: {invoice_data['days_overdue']}
    """

    try:
        # Use Gemini 1.5 Flash as justified in your project plan
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=system_instruction,
            # Force JSON output natively
            generation_config={"response_mime_type": "application/json"}
        )
        
        response = model.generate_content(user_message)
        
        # Security Guardrail: Hallucination/Format check
        email_json = json.loads(response.text)
        
        if "subject" not in email_json or "body" not in email_json:
             raise ValueError("Model hallucinated: Missing required JSON keys")
             
        return email_json

    except Exception as e:
        print(f"Error generating email for {invoice_data['invoice_no']}: {e}")
        print("Using fallback email template due to API error...")
        return {
            "subject": f"Follow-up: Overdue Invoice {invoice_data['invoice_no']}",
            "body": f"Dear {safe_client},\n\nThis is a follow-up regarding invoice {invoice_data['invoice_no']} for the amount of ${safe_amount}, which was due on {formatted_date}.\n\n{tone_data['cta']}\n\nBest regards,\nCollections Team"
        }

if __name__ == "__main__":
    # Test the generator with a mock invoice and tone
    import pandas as pd
    from datetime import datetime
    
    mock_invoice = {
        'invoice_no': 'INV-TEST',
        'client_name': 'Test Corp',
        'amount': '1500.00',
        'due_date': pd.to_datetime('2026-05-01'),
        'days_overdue': 10
    }
    mock_tone = {
        "stage": 2, 
        "status": "PROCESS", 
        "tone": "Polite but Firm", 
        "cta": "Please confirm your payment date as soon as possible."
    }
    
    print("Drafting email via Gemini...")
    result = generate_email(mock_invoice, mock_tone)
    print(json.dumps(result, indent=2))