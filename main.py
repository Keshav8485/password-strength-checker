import re
import hashlib

def check_password_strength(password):
    total_score = 0
    feedback = []

    # Criteria breakdown (total: 100)
    criteria = {
        'length': 20,
        'uppercase': 20,
        'lowercase': 20,
        'digit': 20,
        'special': 20
    }

    # Length check
    if len(password) >= 12:
        total_score += criteria['length']
    elif len(password) >= 8:
        total_score += criteria['length'] * 0.75
        feedback.append("✅ But consider using more than 12 characters.")
    else:
        feedback.append("❌ Too short. Minimum 8 characters recommended.")

    # Uppercase
    if re.search(r"[A-Z]", password):
        total_score += criteria['uppercase']
    else:
        feedback.append("❌ Add at least one uppercase letter.")

    # Lowercase
    if re.search(r"[a-z]", password):
        total_score += criteria['lowercase']
    else:
        feedback.append("❌ Add at least one lowercase letter.")

    # Digit
    if re.search(r"\d", password):
        total_score += criteria['digit']
    else:
        feedback.append("❌ Include at least one digit.")

    # Special characters
    if re.search(r"[!@#$%^&*()_+{}[\]:;<>,.?/~\-]", password):
        total_score += criteria['special']
    else:
        feedback.append("❌ Use at least one special character (!@# etc).")

    return int(total_score), feedback

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def print_strength_bar(score):
    bar_length = 30
    filled_length = int(round(bar_length * score / 100))
    bar = '█' * filled_length + '-' * (bar_length - filled_length)
    print(f"🔒 Strength: [{bar}] {score}%")

if __name__ == "__main__":
    pwd = input("🔐 Enter your password: ")
    score, suggestions = check_password_strength(pwd)

    print_strength_bar(score)

    if score < 60:
        print("⚠️ Your password is weak. Suggestions:")
        for s in suggestions:
            print(" -", s)
    elif score < 85:
        print("✅ Decent password, but there's room to improve:")
        for s in suggestions:
            print(" -", s)
    else:
        print("🎉 Strong password!")

    print("\n🔑 SHA-256 Hash:", hash_password(pwd))
