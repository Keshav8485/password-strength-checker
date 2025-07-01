# main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import hashlib
import requests
import secrets
import string

app = FastAPI()

# CORS middleware for browser-based access (use restrictive origin in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class PasswordInput(BaseModel):
    password: str

@app.get("/")
def root():
    return {
        "message": "Welcome to the Password Strength Checker API!",
        "routes": {
            "/analyze": "POST - Analyze password strength",
            "/generate": "POST - Generate a secure password"
        }
    }

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
