# paradigms project.py
import streamlit as st
from datetime import date
import re
import os
import subprocess
import sys

import hy  # Enables Hy (Lisp) integration
from logic import should_submit_form

st.set_page_config(layout="centered")

# Initialize session state
if 'selected_hospital' not in st.session_state:
    st.session_state.selected_hospital = None
if 'phone_input' not in st.session_state:
    st.session_state.phone_input = "+971 "

# Constants
SPECIALTY_OPTIONS = [
    "Cancer", "Allergy & Immunology", "Dentistry", "Dermatology",
    "Digestive Diseases", "Endocrinology", "Executive Health Program",
    "Gynecology", "Heart, Vascular & Thoracic", "Imaging",
    "Infectious Disease", "Nephrology", "Neurology/Neurosurgery",
    "Ophthalmology (Eye)", "Otolaryngology (ENT)", "Pain Medicine",
    "Physical Medicine & Rehabilitation", "Plastic Surgery",
    "Preventative Medicine", "Primary Care", "Psychiatry & Behavioral Health",
    "Pulmonary Medicine", "Rheumatology", "Urology", "Other"
]

INSURANCE_OPTIONS = [
    "Aafiya", "ADNIC", "Aetna", "AXA Insurance", "Daman",
    "Damana – SAICO Health - Saudi Arabian Insurance Company",
    "Dubai Insurance Company", "Emirates Airlines", "FMC Network",
    "GMMI", "INAYAH - National Life and General Insurance", "MedNet",
    "MetLife", "MSH International", "NAS", "National General Insurance (NGI)",
    "Neuron", "NEXtCARE", "Oman Insurance Company / BUPA Global / Sukoon",
    "Thiqa", "Tricare / ISOS", "Whealth International"
]

# Utilities
def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)

def validate_emirates_id(eid):
    return eid.isdigit() and len(eid) == 15

def format_phone_input(phone):
    phone = re.sub(r"[^\d+]", "", phone)
    return "+971" + phone[-9:] if not phone.startswith("+971") else phone

# Sidebar hospital selection
with st.sidebar:
    st.title("Hospital Options")
    hospitals = ["Cleveland Clinic Abu Dhabi"]
    for hospital in hospitals:
        if st.button(hospital):
            st.session_state.selected_hospital = hospital
            st.session_state.phone_input = "+971 "

# Main UI
if not st.session_state.selected_hospital:
    st.write("Please select a hospital from the sidebar.")
else:
    st.title(f"{st.session_state.selected_hospital} Patient Registration")

    if st.session_state.selected_hospital == "Cleveland Clinic Abu Dhabi":
        col1, col2 = st.columns(2)
        with col1:
            first_name = st.text_input("First Name*")
        with col2:
            last_name = st.text_input("Last Name*")

        email = st.text_input("Email Address*")
        dob = st.date_input("Date of Birth*", min_value=date(1900, 1, 1), max_value=date.today())
        gender = st.radio("Gender*", ["Male", "Female"], horizontal=True)
        phone = st.text_input("Phone Number* (e.g. +971 050 123 4567)", value=st.session_state.phone_input, max_chars=16)

        has_emirates_id = st.radio("Do you have your Emirates ID?", ["Yes", "No"], horizontal=True)
        if has_emirates_id == "Yes":
            emirates_id = st.text_input("Enter your 15-digit Emirates ID*", max_chars=15)
        else:
            emirates_id = ""

        first_time_visit = st.radio("Is this your first time visiting our hospital?", ["Yes", "No"], horizontal=True)

        specialty = st.selectbox("Select the service/specialty you need*", SPECIALTY_OPTIONS)

        payment_method = st.radio("How will you pay for treatment?", ["Insurance", "Self-pay"], horizontal=True)
        if payment_method == "Insurance":
            insurance_provider = st.selectbox("Select your Insurance Provider*", INSURANCE_OPTIONS)
        else:
            insurance_provider = ""

        if st.button("Submit"):
            errors = []
            if not first_name: errors.append("First name is required.")
            if not last_name: errors.append("Last name is required.")
            if not email or not validate_email(email): errors.append("Valid email is required.")
            if len(re.sub(r"[^\d]", "", phone)[4:]) != 9:
                errors.append("Phone must be +971 followed by exactly 9 digits.")
            if has_emirates_id == "Yes" and not validate_emirates_id(emirates_id):
                errors.append("Valid 15-digit Emirates ID is required.")
            if not specialty: errors.append("Please select a specialty.")
            if payment_method == "Insurance" and not insurance_provider:
                errors.append("Please select your insurance provider.")

            if errors:
                for error in errors:
                    st.error(error)
            else:
                st.success("Form submitted successfully!")
                with open(".env", "w") as f:
                    f.write(f"FIRST_NAME={first_name}\n")
                    f.write(f"LAST_NAME={last_name}\n")
                    f.write(f"EMAIL={email}\n")
                    f.write(f"DOB={dob.strftime('%Y-%m-%d')}\n")
                    f.write(f"GENDER={gender}\n")
                    f.write(f"PHONE={format_phone_input(phone)}\n")
                    f.write(f"HAS_EMIRATES_ID={has_emirates_id}\n")
                    if has_emirates_id == "Yes":
                        f.write(f"EMIRATES_ID={emirates_id}\n")
                    f.write(f"FIRST_TIME_VISIT={first_time_visit}\n")
                    f.write(f"SPECIALTY={specialty}\n")
                    f.write(f"PAYMENT_METHOD={payment_method}\n")
                    if payment_method == "Insurance":
                        f.write(f"INSURANCE_PROVIDER={insurance_provider}\n")

                # Use Lisp logic to determine if the form should be submitted
                if should_submit_form(first_time_visit, specialty, payment_method):
                    try:
                        subprocess.Popen(["py", "browser_user.py"])
                    except Exception as e:
                        st.error(f"Could not start process: {e}")
                else:
                    st.warning("Conditions not met to submit the form based on eligibility logic.")

    else:
        st.info("Form coming soon for this hospital.")
        if st.button("Back"):
            st.session_state.selected_hospital = None
            st.rerun()
