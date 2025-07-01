# app.py

import streamlit as st
import requests

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

    # Use localhost for local dev or replace with deployed URL:
    API_BASE = "http://127.0.0.1:8000"
    # API_BASE = "https://password-strength-checker-8ix5.onrender.com"

    password_input = st.text_input("Enter your password:", type="password")
    st.caption("⚠️ Avoid personal info in passwords (name, birthdate, etc.).")

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
                st.error(f"🔓 Found in {count:,} data breaches. Avoid using this password.")
            else:
                st.success("✅ Password not found in any known breach.")

            st.markdown("### 🔍 Breakdown")
            cols = st.columns(len(breakdown))
            for i, (k, v) in enumerate(breakdown.items()):
                cols[i].metric(k.capitalize(), f"{v}%")

            if suggestions:
                st.markdown("### 🛠️ Suggestions")
                for s in suggestions:
                    st.write(f"- {s}")
            else:
                st.success("🎉 All password criteria met!")

            st.markdown("### 🔑 SHA-256 Hash")
            st.code(hashed)

        except Exception as e:
            st.error(f"API error: {e}")

    st.markdown("## 🔁 Generate a Secure Password")
    if st.button("Generate Password"):
        try:
            gen = requests.post(f"{API_BASE}/generate")
            gen.raise_for_status()
            pw = gen.json()["password"]
            st.success(f"🔑 {pw}")
        except Exception as e:
            st.error(f"Error: {e}")

    st.markdown("<div class='footer'>© 2025 Keshav Kacholiya</div>", unsafe_allow_html=True)

if __name__ == "__main__":
    run_streamlit_app()
