import re
import hashlib
import streamlit as st
import secrets
import string

# Page config
st.set_page_config(
    page_title="🔐 Password Strength Checker",
    page_icon="🔒",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for styling (now includes anchor link hiding)
st.markdown(
    """
    <style>
    /* Hide anchor links next to headers */
    .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a, .stMarkdown h4 a {
        display: none !important;
    }
    .reportview-container {
        background-color: #f5f5f5;
        color: #333;
    }
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        border-radius: 8px;
        padding: 0.5em 1em;
    }
    .stProgress > div > div > div {
        background-color: #4CAF50;
    }
    .footer {
        text-align: center;
        margin-top: 2em;
        color: #777;
    }
    /* Generator styled inline without white box */
    .generator h3 {
        display: inline;
        margin-right: 0.5em;
    }
    </style>
    """, unsafe_allow_html=True
)

# Title and description
st.markdown(
    """
    <div style='text-align: center;'>
      <h1 style='color: #4CAF50;'>🔐 Password Strength Checker</h1>
      <p>Analyze your password security & get instant feedback!</p>
      <hr>
    </div>
    """,
    unsafe_allow_html=True
)

# Function: Check strength
def check_password_strength(password):
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
                feedback.append("Use at least 12 characters for maximum points.")
            elif name == 'uppercase':
                feedback.append("Add uppercase letters.")
            elif name == 'lowercase':
                feedback.append("Add lowercase letters.")
            elif name == 'digits':
                feedback.append("Include digits.")
            elif name == 'special':
                feedback.append("Include special characters like !@#$.")
    return int(score), breakdown, feedback

# Main input section
password_input = st.text_input("Enter your password:", type="password")

if password_input:
    score, breakdown, suggestions = check_password_strength(password_input)

    # Display results
    st.markdown(f"### 💯 Overall Strength: **{score}%**")
    st.progress(score)

    # Breakdown
    st.markdown("### 🔍 Score Breakdown")
    cols = st.columns(len(breakdown))
    for idx, (k, v) in enumerate(breakdown.items()):
        cols[idx].metric(k.capitalize(), f"{v}%")

    # Feedback
    if suggestions:
        st.markdown("### 🛠️ Suggestions to Improve")
        for s in suggestions:
            st.write(f"- {s}")
    else:
        st.success("🎉 Your password meets all criteria!")

    # Hashed output
    hashed = hashlib.sha256(password_input.encode()).hexdigest()
    st.markdown("---")
    st.markdown(f"### 🔑 SHA-256 Hash:\n```{hashed}```")

# Random Generator below content
st.markdown(
    """
    <h3 class='generator'>💡 Need a secure password?</h3>
    <p>We can generate one for you:</p>
    """,
    unsafe_allow_html=True
)

length = st.slider("Length", 8, 32, 16)
use_upper = st.checkbox("Include Uppercase", True)
use_lower = st.checkbox("Include Lowercase", True)
use_digits = st.checkbox("Include Digits", True)
use_special = st.checkbox("Include Special Characters", True)
if st.button("Generate Password"):
    alphabet = ''
    if use_upper:
        alphabet += string.ascii_uppercase
    if use_lower:
        alphabet += string.ascii_lowercase
    if use_digits:
        alphabet += string.digits
    if use_special:
        alphabet += string.punctuation
    if not alphabet:
        st.error("Select at least one character set!")
    else:
        pw = ''.join(secrets.choice(alphabet) for _ in range(length))
        st.success(f"🔑 Generated Password: `{pw}`")

# Footer with author
st.markdown("<div class='footer'>© 2025 Keshav Kacholiya</div>", unsafe_allow_html=True)