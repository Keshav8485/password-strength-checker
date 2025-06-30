# 🔐 Password Strength Checker

### 🧑‍💻 Created by: **Keshav Kacholiya**

🚀 **Live App**: [Click here to try it out](https://password-strength-checker-keshav.streamlit.app/)

A beautiful and intelligent web app to check the strength of passwords based on a scoring algorithm and SHA-256 hashing. It also includes a secure password generator for users to create strong passwords instantly.

---

## 🚀 Features

- ✅ Real-time password strength analysis (0–100%)
- ✅ Feedback on how to improve your password
- ✅ SHA-256 hashing for secure representation
- ✅ Random secure password generator
- ✅ Responsive UI built using Streamlit
- ✅ Fully customizable with color-coded feedback

---

## 📊 How It Works

### 🧠 Scoring Algorithm

Each password is evaluated using the following criteria:

| Feature        | Weight (%) | Rule                                       |
|----------------|------------|--------------------------------------------|
| Length         | 25         | At least 12 characters                     |
| Uppercase      | 20         | Must include at least 1 uppercase letter   |
| Lowercase      | 20         | Must include at least 1 lowercase letter   |
| Digits         | 15         | Must include at least 1 digit              |
| Special Chars  | 20         | Must include characters like `@#$%&*!`     |

---

### 🔑 SHA-256 Hashing

We use the SHA-256 hashing algorithm from Python’s standard `hashlib` library to securely represent passwords. This ensures that original passwords are never stored or displayed in plain text.

```python
import hashlib
hashed = hashlib.sha256(password.encode()).hexdigest()
```

This ensures safe handling and display of password values.

---

### 🔐 Password Generator

You can generate random passwords by selecting options like:
- Include uppercase/lowercase
- Include digits
- Include symbols
- Password length (8–32)

Built using the `secrets` module for cryptographic security.

---
## 👨‍💻 Author
**Keshav Kacholiya**  

---

## ⚖️ License

This project is licensed under the [MIT License](LICENSE).  
© 2025 **Keshav Kacholiya**

