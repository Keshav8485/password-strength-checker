# --- IMPORTS ---
# Common imports for both Streamlit and FastAPI
import requests
import re
import hashlib
import secrets
import string

# FastAPI specific imports
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Streamlit specific import
import streamlit as st


# ==============================================================================
# --- 1. FASTAPI BACKEND API (for your browser extension) ---
# ==============================================================================

app = FastAPI()

# --- THIS IS THE CRUCIAL FIX FOR THE CORS ERROR ---
# This middleware will add the necessary headers to the API responses
# to tell the browser that it's okay for your extension to access it.
origins = [
    # You can specify the exact extension origin for better security in production
    # "chrome-extension://ccpndadplfabgkahiljhdeomdjeicded", 
    "*" # Using "*" is fine for local development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers
)
# ----------------------------------------------------

class PasswordInput(BaseModel):
    password: str

@app.post("/analyze")
def analyze_password(data: PasswordInput):
    password = data.password

    criteria = {
        'length': {'weight': 25, 'func': lambda s: min(len(s)/12, 1)},
        'uppercase': {'weight': 20, 'func': lambda s: 1 if re.search(r'[A-Z]', s) else 0},
        'lowercase': {'weight': 20, 'func': lambda s: 1 if re.search(r'[a-z]', s) else 0},
        'digits': {'weight': 15, 'func': lambda s: 1 if re.search(r'\d', s) else 0},
        'special': {'weight': 20, 'func': lambda s: 1 if re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?/~\\-]', s) else 0}
    }

    score = 0
    breakdown = {}
    feedback = []

    for name, crit in criteria.items():
        val = crit['func'](password)
        part = val * crit['weight']
        breakdown[name] = int(part)
        score += part
        if val == 0:
            if name == 'length':
                feedback.append("Use at least 12 characters.")
            elif name == 'uppercase':
                feedback.append("Add uppercase letters.")
            elif name == 'lowercase':
                feedback.append("Add lowercase letters.")
            elif name == 'digits':
                feedback.append("Include digits.")
            elif name == 'special':
                feedback.append("Include special characters.")

    # Check breach via HIBP API
    sha1pwd = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1pwd[:5], sha1pwd[5:]
    breached = False
    count = 0
    try:
        res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}")
        if res.status_code == 200:
            for line in res.text.splitlines():
                hash_suffix, c = line.split(':')
                if hash_suffix == suffix:
                    breached = True
                    count = int(c)
                    break
    except:
        pass

    # SHA‑256 hash
    hashed = hashlib.sha256(password.encode()).hexdigest()

    return {
        "score": int(score),
        "breakdown": breakdown,
        "feedback": feedback,
        "breached": breached,
        "breach_count": count,
        "sha256": hashed
    }

@app.post("/generate")
def generate_password():
    alphabet = string.ascii_letters + string.digits + "!@#_"
    pw = ''.join(secrets.choice(alphabet) for _ in range(12))
    return {"password": pw}


# ==============================================================================
# --- 2. STREAMLIT FRONTEND (your original web app) ---
# ==============================================================================
# This part of the code will only run when you use the `streamlit run` command.
# It is separate from the FastAPI server.

def run_streamlit_app():
    st.set_page_config(
        page_title="🔐 Password Strength Checker",
        page_icon="🔒",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # --- CSS Styling ---
    st.markdown("""
    <style>
        .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a { display: none !important; }
        .reportview-container { background-color: #f5f5f5; color: #333; }
        .stButton > button { background-color: #4CAF50; color: white; border-radius: 8px; padding: 0.5em 1em; }
        .stProgress > div > div > div { background-color: #4CAF50; }
        .footer { text-align: center; margin-top: 2em; color: #777; }
        .generator h3 { display: inline; margin-right: 0.5em; }
    </style>
    """, unsafe_allow_html=True)

    # --- Header ---
    st.markdown("""
    <div style='text-align: center;'>
      <h1 style='color: #4CAF50;'>🔐 Password Strength Checker</h1>
      <p>Analyze your password security & get instant feedback!</p>
      <hr>
    </div>
    """, unsafe_allow_html=True)

    API_BASE = "http://127.0.0.1:8000"

    # --- Password Strength Checker ---
    password_input = st.text_input("Enter your password:", type="password")
    st.caption("⚠️ Do not use your name or date of birth in the password. They are very easy to crack.")

    if password_input:
        try:
            response = requests.post(f"{API_BASE}/analyze", json={"password": password_input})
            response.raise_for_status()
            result = response.json()

            score = result["score"]
            breakdown = result["breakdown"]
            suggestions = result["feedback"]
            breached = result["breached"]
            count = result["breach_count"]
            hashed = result["sha256"]

            st.markdown(f"### 💯 Overall Strength: **{score}%**")
            st.progress(score)

            if breached:
                st.error(f"🔓 This password was found in {count:,} known data breaches! Please avoid using it.")
            else:
                st.success("✅ Not found in known breaches.")

            st.markdown("### 🔍 Score Breakdown")
            cols = st.columns(len(breakdown))
            for idx, (k, v) in enumerate(breakdown.items()):
                cols[idx].metric(k.capitalize(), f"{v}%")

            if suggestions:
                st.markdown("### 🛠️ Suggestions to Improve")
                for s in suggestions:
                    st.write(f"- {s}")
            else:
                st.success("🎉 Your password meets all criteria!")

            st.markdown("---")
            st.markdown(f"### 🔑 SHA-256 Hash:\n```{hashed}```")

        except Exception as e:
            st.error(f"API Error: Could not connect to the backend server. Make sure it's running. Details: {e}")

    # --- Password Generator ---
    st.markdown("## 💡 Need a secure password?")
    if st.button("Generate Password"):
        try:
            gen = requests.post(f"{API_BASE}/generate")
            gen.raise_for_status()
            pw = gen.json()["password"]
            st.success(f"🔑 Generated Password: `{pw}`")
        except Exception as e:
            st.error(f"API Error: Could not connect to the backend server. Make sure it's running. Details: {e}")

    # --- Footer ---
    st.markdown("<div class='footer'>© 2025 Keshav Kacholiya</div>", unsafe_allow_html=True)


# This allows you to run the Streamlit app with `streamlit run app.py`
if __name__ == "__main__":
    run_streamlit_app()
