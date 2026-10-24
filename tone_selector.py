def get_tone_stage(days_overdue):
    """
    Maps days overdue to a specific follow-up stage, tone, and CTA.
    Returns ESCALATE for 30+ days and NOT_DUE for negative days.
    """
    if days_overdue <= 0:
         return {"stage": 0, "status": "NOT_DUE", "tone": None, "cta": None}
    
    elif 1 <= days_overdue <= 7:
        return {
            "stage": 1, 
            "status": "PROCESS", 
            "tone": "Friendly Reminder", 
            "cta": "Please let us know when to expect payment or if you need another copy of the invoice."
        }
        
    elif 8 <= days_overdue <= 14:
        return {
            "stage": 2, 
            "status": "PROCESS", 
            "tone": "Polite but Firm", 
            "cta": "Please confirm your payment date as soon as possible."
        }
        
    elif 15 <= days_overdue <= 21:
        return {
            "stage": 3, 
            "status": "PROCESS", 
            "tone": "Urgent Request", 
            "cta": "Immediate payment is required to avoid potential late fees."
        }
        
    elif 22 <= days_overdue <= 30:
        return {
            "stage": 4, 
            "status": "PROCESS", 
            "tone": "Final Warning", 
            "cta": "Please pay immediately to avoid service suspension and further collection actions."
        }
        
    else: # 31+ days
        return {"stage": 5, "status": "ESCALATE", "tone": None, "cta": None}

if __name__ == "__main__":
    # Test the selector
    test_days = [-2, 3, 10, 18, 25, 35]
    for d in test_days:
        print(f"Days {d:2d} -> {get_tone_stage(d)}")