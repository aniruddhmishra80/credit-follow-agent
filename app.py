import streamlit as st
import pandas as pd
import json
import os
import time
from main import run_agent

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Credit Follow-up Agent Pro", 
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- HELPER FUNCTIONS ---
@st.cache_data
def load_input_data():
    try:
        df = pd.read_csv("sample_data.csv")
        # Calculate a quick overdue status for the UI
        df['due_date'] = pd.to_datetime(df['due_date'])
        today = pd.to_datetime('today').normalize()
        df['days_overdue'] = (today - df['due_date']).dt.days
        df['UI_Status'] = df['days_overdue'].apply(
            lambda x: "🟢 Not Due" if x <= 0 else ("🔴 ESCALATE" if x > 30 else "🟡 Overdue")
        )
        return df
    except FileNotFoundError:
        return pd.DataFrame()

def load_audit_logs():
    if os.path.exists("audit_log.json"):
        try:
            with open("audit_log.json", "r") as f:
                logs = json.load(f)
                return pd.DataFrame(logs)
        except json.JSONDecodeError:
            return pd.DataFrame()
    return pd.DataFrame()

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2830/2830284.png", width=60) # Placeholder icon
    st.title("Agent Controls")
    st.markdown("Configure the AI pipeline before execution.")
    
    st.divider()
    
    # Advanced Toggle with styling
    st.subheader("Security & Testing")
    dry_run = st.toggle("🛡️ DRY_RUN Mode", value=True, help="Intercepts emails and prints to console. Turn off to use SMTP.")
    os.environ["DRY_RUN"] = str(dry_run).lower()
    
    if dry_run:
        st.info("Safe Mode: Emails will NOT be sent.")
    else:
        st.warning("Live Mode: Real emails will be dispatched.")

    st.divider()
    
    # Run Button
    if st.button("🚀 Run AI Pipeline", type="primary", use_container_width=True):
        with st.status("Initializing AI Agent...", expanded=True) as status:
            st.write("Loading data...")
            time.sleep(0.5) # Slight pause for UI effect
            st.write("Connecting to Gemini LLM...")
            
            # Actually run the agent
            run_agent()
            
            status.update(label="Pipeline Execution Complete!", state="complete", expanded=False)
        st.toast('Emails processed successfully!', icon='✅')
        time.sleep(1) # Give toast a moment to show before rerun
        st.rerun()

# --- MAIN DASHBOARD ---
st.title("🏦 Automated Credit Follow-up System")
st.markdown("LLM-powered pipeline for analyzing overdue invoices and generating contextual outreach.")

# Load Data
df_input = load_input_data()
df_logs = load_audit_logs()

# --- KPI METRICS ROW ---
if not df_input.empty:
    col1, col2, col3, col4 = st.columns(4)
    total_invoices = len(df_input)
    overdue_count = len(df_input[df_input['days_overdue'] > 0])
    total_value = df_input['amount'].sum()
    emails_sent = len(df_logs[df_logs['send_status'] == 'sent']) if not df_logs.empty else 0
    
    col1.metric("Total Invoices", total_invoices)
    col2.metric("Invoices Overdue", overdue_count, delta=f"{(overdue_count/total_invoices)*100:.0f}%", delta_color="inverse")
    col3.metric("Total Value at Risk", f"${total_value:,.2f}")
    col4.metric("Emails Sent Today", emails_sent)

st.divider()

# --- TABBED INTERFACE ---
tab1, tab2, tab3 = st.tabs(["📊 Live Data", "📋 Audit Logs", "⚙️ System Architecture"])

with tab1:
    st.subheader("Current Invoice Ledger")
    if not df_input.empty:
        # Interactive Dataframe
        st.dataframe(
            df_input,
            column_config={
                "amount": st.column_config.NumberColumn("Amount ($)", format="$%.2f"),
                "UI_Status": st.column_config.TextColumn("Status"),
            },
            hide_index=True,
            use_container_width=True
        )
    else:
        st.error("Could not find sample_data.csv")

with tab2:
    col_log1, col_log2 = st.columns([3, 1])
    with col_log1:
        st.subheader("Communication Audit Trail")
    with col_log2:
        if st.button("🗑️ Clear Logs"):
            if os.path.exists("audit_log.json"):
                os.remove("audit_log.json")
                st.rerun()

    if not df_logs.empty:
        # Sort by newest first
        df_logs = df_logs.sort_values(by="timestamp", ascending=False)
        
        # Style the dataframe based on status
        def color_status(val):
            color = '#28a745' if val == 'sent' else '#ffc107' if val == 'dry-run' else '#dc3545'
            return f'color: {color}; font-weight: bold'
            
        styled_logs = df_logs[['timestamp', 'invoice_no', 'client_name', 'stage', 'tone', 'send_status']].style.map(color_status, subset=['send_status'])
        
        st.dataframe(styled_logs, hide_index=True, use_container_width=True)
        
        # Expandable detailed view
        with st.expander("View Raw JSON Output"):
            st.json(df_logs.to_dict(orient="records"))
    else:
        st.info("No communications have been logged yet. Run the pipeline to generate logs.")

with tab3:
    st.subheader("Agent Pipeline Architecture")
    st.markdown("""
    This prototype utilizes a deterministic sequential pipeline to ensure maximum reliability and prevent LLM hallucinations.
    
    1. **Data Ingestion:** `pandas` parses the ledger and calculates overdue metrics.
    2. **Logic Gate:** `tone_selector.py` routes the invoice to a specific escalation stage (1-4) or flags it for manual review.
    3. **Generation:** **Gemini 2.5 Flash** generates a personalized email payload enforced as strict JSON.
    4. **Dispatch & Log:** The system routes the email to SMTP (or intercepts it in `DRY_RUN` mode) and logs the immutable event to `audit_log.json`.
    """)