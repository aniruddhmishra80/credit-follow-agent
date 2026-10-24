import pandas as pd
from datetime import datetime

def load_data(file_path="sample_data.csv"):
    try:
        df = pd.read_csv(file_path)
        
        # Convert due_date to a datetime object
        df['due_date'] = pd.to_datetime(df['due_date'])
        
        # Calculate days overdue
        # We normalize today to midnight to avoid time-of-day math issues
        today = pd.to_datetime(datetime.today().date())
        df['days_overdue'] = (today - df['due_date']).dt.days
        
        # Return as a list of dictionaries for easy processing in the pipeline
        return df.to_dict(orient='records')
        
    except FileNotFoundError:
        print(f"Error: {file_path} not found.")
        return []

if __name__ == "__main__":
    # Test the loader
    invoices = load_data()
    for inv in invoices:
        print(f"{inv['invoice_no']} | Overdue: {inv['days_overdue']} days")