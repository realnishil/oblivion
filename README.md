```
 ██████╗ ██████╗ ██╗     ██╗██╗   ██╗██╗ ██████╗ ███╗   ██╗
██╔═══██╗██╔══██╗██║     ██║██║   ██║██║██╔═══██╗████╗  ██║
██║   ██║██████╔╝██║     ██║██║   ██║██║██║   ██║██╔██╗ ██║
██║   ██║██╔══██╗██║     ██║╚██╗ ██╔╝██║██║   ██║██║╚██╗██║
╚██████╔╝██████╔╝███████╗██║ ╚████╔╝ ██║╚██████╔╝██║ ╚████║
 ╚═════╝ ╚═════╝ ╚══════╝╚═╝  ╚═══╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝
```

<div align="center">

### 🕳️ A local, educational brute-force *simulation* tool 🕳️

![Version](https://img.shields.io/badge/version-1.0--beta-blueviolet?style=for-the-badge)
![Status](https://img.shields.io/badge/status-beta-orange?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.x-3776AB?style=for-the-badge&logo=python&logoColor=white)
![License](https://img.shields.io/badge/license-Educational--Use-yellow?style=for-the-badge)
![Made by](https://img.shields.io/badge/made%20by-Nishil%20Bhimani-ff69b4?style=for-the-badge)

**⚠️ EDUCATIONAL PURPOSES ONLY ⚠️**

</div>

---

## 📖 About

**Oblivion** is a self-contained, local sandbox for learning how brute-force
login attacks work — and, more importantly, how to **defend** against them.

Every "attack" in this tool runs against an **in-memory hash defined in the
script itself**. Nothing here connects to a network, a real login form, or
any external system. It's a safe playground for understanding the mechanics
of credential guessing, lockouts, throttling, and password hygiene.

> 🚫 This tool does **not** attack real systems, accounts, or services of
> any kind — simulated or otherwise external to the script.

---

## ✨ Features

| # | Feature | Description |
|---|---------|-------------|
| 🎯 | **Brute-force simulation** | Watch guesses fly against a local hash with realistic throttling & lockouts |
| 📂 | **Wordlist loader** | Bring your own wordlist file and run it through the simulator |
| 🛠️ | **Wordlist generator** | Build custom candidate lists from a base word + digit/symbol suffixes |
| 🔐 | **Password strength checker** | Score any password (0–6) with actionable suggestions |
| 📜 | **Attempt log viewer** | Review a timestamped history of every simulated attempt |
| 🛡️ | **Defense tips** | Built-in cheat sheet of real-world anti-brute-force best practices |

---

## 🚀 Getting Started

```bash
# Clone the repo
git clone https://github.com/nishilxy/Brute-Force-by-Nish.git
cd Brute-Force-by-Nish

# Run it
python3 testbfone.py
```

No external dependencies required — pure Python standard library. 🐍

---

## 🧭 Menu Overview

```
┌──────────────────────────────────────────────────┐
│                  OBLIVION MENU                    │
├──────────────────────────────────────────────────┤
│  1) Simulate brute-force attack (auto wordlist)   │
│  2) Load wordlist from file & simulate            │
│  3) Generate wordlist interactively                │
│  4) Password strength checker                      │
│  5) View local attempt log                          │
│  6) Show safety & defensive tips                    │
│  0) Exit                                            │
└──────────────────────────────────────────────────┘
```

---

## 🛡️ Defense Tips (Baked In)

- ✅ Rate limiting, progressive delays & account lockouts
- ✅ Multi-factor authentication (MFA)
- ✅ Slow hashing algorithms (bcrypt / scrypt / Argon2)
- ✅ Long, random passphrases over short complex ones
- ✅ Monitoring & alerting on unusual login velocity
- ✅ CAPTCHA / device fingerprinting on public endpoints

---

## ⚠️ Disclaimer

> Oblivion is provided **strictly for educational purposes**. It must only
> be used on systems, accounts, and data that you own or have **explicit
> written permission** to test. Unauthorized use against systems you do
> not own is **illegal** and unethical. The author assumes no liability
> for misuse.

---

<div align="center">

### 👤 Author

**Nishil Bhimani**

🔗 [github.com/nishilxy](https://github.com/nishilxy)

---

*"Understanding the attack is the first step to building the defense."*

![Made with Python](https://img.shields.io/badge/built%20with-🐍%20Python-informational?style=flat-square)
![Educational Tool](https://img.shields.io/badge/purpose-🎓%20Educational-success?style=flat-square)

</div>
