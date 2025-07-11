import streamlit as st
import pandas as pd

# Dummy excluded NPI set (from LEIE)
excluded_npis = {"1972902351", "1922348218"}

# Functions
def validate_npi(npi):
    npi = str(npi)
    if len(npi) != 10 or not npi.isdigit():
        return "Invalid", 100
    if npi.startswith("0"):
        return "Inactive", 40
    return "Valid", 0

def match_cpt(cpt_code):
    valid_cpts = {'99213', '93306'}
    if str(cpt_code) in valid_cpts:
        return "Match", 0
    return "Mismatch", 30

def check_exclusion(npi):
    if str(npi) in excluded_npis:
        return "Excluded", 90
    return "Not Excluded", 0

def assess_provider(row):
    npi_status, score_npi = validate_npi(row['NPI'])
    cpt_status, score_cpt = match_cpt(row['CPT'])
    exclusion_status, score_excl = check_exclusion(row['NPI'])

    total_score = score_npi + score_cpt + score_excl
    return pd.Series([npi_status, cpt_status, exclusion_status, total_score])

# UI
st.title("Phantom Provider Risk Scoring App")
st.write("Upload a CSV file with columns: NPI, CPT, State")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file:
    df = pd.read_csv(uploaded_file, dtype=str)
    df.fillna("", inplace=True)
    
    df[['NPI_Status', 'CPT_Status', 'Exclusion_Status', 'Risk_Score']] = df.apply(assess_provider, axis=1)
    
    st.success("Processing complete.")
    st.dataframe(df)

    # Download button
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Download Results", csv, "scored_output.csv", "text/csv")
