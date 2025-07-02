# app.py (Final version with correct copy-to-clipboard)

import streamlit as st
import requests
import re
import hashlib
import secrets
import string
from st_copy_to_clipboard import st_copy_to_clipboard  # <-- CORRECT IMPORT

# --- Helper Functions (No changes needed here) ---

def analyze_password_logic(password: str):
    # (This function is unchanged)
    criteria = {
        'length': {'weight': 25, 'func': lambda s: min(len(s)/12, 1)},
        'uppercase': {'weight': 20, 'func': lambda s: 1 if re.search(r'[A-Z]', s) else 0},
        'lowercase': {'weight': 20, 'func': lambda s: 1 if re.search(r'[a-z]', s) else 0},
        'digits': {'weight': 15, 'func': lambda s: 1 if re.search(r'\d', s) else 0},
        'special': {'weight': 20, 'func': lambda s: 1 if re.search(r'[!@#$%^&*()_+{}\[\]:;<>,.?/~\\-]', s) else 0}
    }
    score, breakdown, feedback = 0, {}, []
    for name, crit in criteria.items():
        val = crit['func'](password)
        part = val * crit['weight']
        breakdown[name], score = int(part), score + part
        if val == 0:
            if name == 'length': feedback.append("Use at least 12 characters.")
            elif name == 'uppercase': feedback.append("Add uppercase letters.")
            elif name == 'lowercase': feedback.append("Add lowercase letters.")
            elif name == 'digits': feedback.append("Include digits.")
            elif name == 'special': feedback.append("Include special characters.")
    sha1pwd = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix, suffix = sha1pwd[:5], sha1pwd[5:]
    breached, count = False, 0
    try:
        res = requests.get(f"https://api.pwnedpasswords.com/range/{prefix}", timeout=5)
        if res.status_code == 200:
            for line in res.text.splitlines():
                hash_suffix, c = line.split(':')
                if hash_suffix == suffix:
                    breached, count = True, int(c)
                    break
    except requests.RequestException: pass
    hashed = hashlib.sha256(password.encode()).hexdigest()
    return {"score": int(score), "breakdown": breakdown, "feedback": feedback, "breached": breached, "breach_count": count, "sha256": hashed}

def generate_password_logic():
    # (This function is unchanged)
    alphabet = string.ascii_letters + string.digits + "!@#_"
    pw = ''.join(secrets.choice(alphabet) for _ in range(12))
    return {"password": pw}


# --- Streamlit UI ---

st.set_page_config(
    page_title="🔐 Password Strength Checker",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS Styling with fix to hide heading links
st.markdown("""
<style>
    h1 a, h2 a, h3 a, h4 a, h5 a, h6 a {
        display: none !important;
        visibility: hidden !important;
    }
    .reportview-container { background-color: #f5f5f5; color: #333; }
    .stButton > button { background-color: #4CAF50; color: white; border-radius: 8px; padding: 0.5em 1em; }
    .stProgress > div > div > div { background-color: #4CAF50; }
    .footer { text-align: center; margin-top: 2em; color: #777; }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div style='text-align: center;'>
  <h1 style='color: #4CAF50;'>🔐 Password Strength Checker</h1>
  <p>Analyze your password security & get instant feedback!</p>
  <hr>
</div>
""", unsafe_allow_html=True)

password_input = st.text_input("Enter your password:", type="password")
st.caption("⚠️ Avoid personal info in passwords (name, birthdate, etc.).")

if password_input:
    try:
        result = analyze_password_logic(password_input)
        score, breakdown, suggestions, breached, count, hashed = result.values()
        
        # ... (display results, no changes here) ...
        st.markdown(f"### 💯 Overall Strength: **{score}%**")
        st.progress(score)
        if breached: st.error(f"🔓 Found in {count:,} data breaches. Avoid using this password.")
        else: st.success("✅ Password not found in any known breach.")
        st.markdown("### 🔍 Breakdown")
        cols = st.columns(len(breakdown))
        for i, (k, v) in enumerate(breakdown.items()):
            cols[i].metric(k.capitalize(), f"{v}%")
        if suggestions:
            st.markdown("### 🛠️ Suggestions")
            for s in suggestions:
                st.write(f"- {s}")
        else: st.success("🎉 All password criteria met!")
        
        # --- Corrected Copy Button for SHA Hash ---
        st.markdown("### 🔑 SHA-256 Hash")
        st.code(hashed, language=None)
        st_copy_to_clipboard(hashed, "Copy Hash")

    except Exception as e:
        st.error(f"An error occurred: {e}")

st.markdown("## 🔁 Generate a Secure Password")
if st.button("Generate Password"):
    result = generate_password_logic()
    pw = result["password"]
    st.success("✅ Secure password generated!")
    st.code(pw, language=None)
    # --- Corrected Copy Button for Generated Password ---
    st_copy_to_clipboard(pw, "Copy Password")

st.markdown("<div class='footer'>© 2025 Keshav Kacholiya</div>", unsafe_allow_html=True)
