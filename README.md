# 💀 OBLIVION V6.6 
[![MIT License](https://img.shields.io/badge/LICENSE-MIT-black?style=for-the-badge&logo=opensourceinitiative&logoColor=00ff88)](LICENSE)

<div align="center">

```text
   ▄█████▄  ▀██████▄  ██▓     ██▓ ██▒   █▓ ██▓ ▒█████   ███▄    █
 ██▒   ██▒   ▒██▀ ▀█ ██▒    ▓██▒▓██░   █▒▓██▒▒██▒  ██▒ ██ ▀█   █
 ██░   ██▒   ░██   █▌██░    ▒██▒ ▓██  █▒░▒██▒▒██░  ██▒▓██  ▀█ ██▒
 ██   ▄██░  ░▓█▄   ▌██░    ░██░  ▒██ █░░░██░▒██   ██░▓██▒  ▐▌██▒
 ░███████▒  ░▒████▓ ███████░██░   ▒▀█░  ░██░░ ████▓▒░▒██░   ▓██░
 ░▒▒ ▓░▒░▒   ▒▒▓  ▒ ▒░▓  ░░▓     ░ ▐░  ░▓  ░ ▒░▒░▒░ ░ ▒░   ▒ ▒
 ░░▒ ▒ ░ ▒   ░ ▒  ▒ ░ ▒  ░ ▒ ░   ░ ░░   ▒ ░  ░ ▒ ▒░ ░ ░░   ░ ▒░
 ░ ░ ░ ░ ░   ░ ░  ░ ░ ░    ▒ ░     ░░   ▒ ░░ ░ ░ ▒     ░   ░ ░
   ░ ░         ░      ░  ░ ░        ░   ░      ░ ░           ░
 ░           ░                        ░

                    OBLIVION V6.6
        Secure • Modular • Multi-Format Framework
```

![Python](https://img.shields.io/badge/Python-3.10+-00ff88?style=for-the-badge)
![Version](https://img.shields.io/badge/Version-6.6-ff0055?style=for-the-badge)
![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-00ccff?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

### ⚠️ Educational & Authorized Security Testing Only

</div>

---

# 🧠 What is OBLIVION?

**OBLIVION V6.6** is a modular password auditing and security testing framework designed for:

* Password strength analysis
* Hash verification and recovery testing
* File password auditing
* Wordlist generation and mutation
* Rule-based password transformations
* Hashcat integration
* Reporting and analytics
* CTF training environments
* Security research labs

The framework contains multiple attack engines, reporting systems, password intelligence utilities, plugin support, checkpoint recovery, and batch automation.

---

# 🔥 Core Features

## ⚡ Hash Auditing

Supported algorithms:

| Algorithm     | Supported |
| ------------- | --------- |
| MD5           | ✅         |
| SHA1          | ✅         |
| SHA256        | ✅         |
| SHA512        | ✅         |
| NTLM          | ✅         |
| bcrypt        | ✅         |
| MySQL         | ✅         |
| APR1          | ✅         |
| Django PBKDF2 | ✅         |

### Capabilities

* Hash identification
* Hash verification
* Dictionary attacks
* Brute force attacks
* Rule mutations
* Checkpoint recovery
* Multi-core processing

---

## 📁 File Password Auditing

Supported formats:

| Format           | Supported |
| ---------------- | --------- |
| ZIP              | ✅         |
| 7Z               | ✅         |
| RAR              | ✅         |
| PDF              | ✅         |
| Microsoft Office | ✅         |
| GPG              | ✅         |
| KeePass          | ✅         |
| SSH Keys         | ✅         |
| PKCS12           | ✅         |
| PEM Keys         | ✅         |
| VeraCrypt        | ✅         |

---

## ⚙️ Rule Engine

Automatically mutates words:

```text
password
Password
PASSWORD
p@ssword
passwordpassword
drowssap
PassWord
```

Built-in rules:

* Uppercase
* Lowercase
* Reverse
* Capitalize
* Duplicate
* Toggle Case
* Leetspeak
* Character Insertions
* Character Deletions

---

## 🚀 Multi-Core Cracking Engine

OBLIVION utilizes:

```python
multiprocessing
```

for CPU intensive workloads.

Benefits:

* Faster execution
* Better CPU utilization
* Parallel hash verification
* Reduced runtime

---

## 💾 Checkpoint Recovery

Never lose progress.

Features:

* Automatic save states
* Resume interrupted sessions
* Restore attack progress
* Crash recovery

---

## 📊 Reporting Engine

Generate reports in:

* JSON
* CSV
* Markdown
* HTML

Reports include:

```text
Target
Password Found
Algorithm
Attempts
Execution Time
```

---

## 📈 Analytics & Statistics

Built-in:

* Password entropy analysis
* Wordlist profiling
* Character frequency analysis
* Crack time estimation
* Password scoring

---

## 🎮 CTF Mode

Train like a real security professional.

Features:

* Challenge creation
* Local challenge database
* Scoring system
* Progress tracking

---

## 🔌 Plugin System

Extend OBLIVION using Python plugins.

Example:

```python
class MyPlugin(Plugin):
    def run(self,args):
        print("Hello from plugin")
```

Drop plugin into:

```text
plugins/
```

and OBLIVION loads it automatically.

---

# 📦 Installation

## Clone Repository

```bash
git clone https://github.com/realnishil/oblivion.git

cd oblivion
```

---

## Create Virtual Environment

### Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

### Windows

```powershell
python -m venv venv

venv\Scripts\activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 📋 Required Dependencies

```bash
pip install bcrypt
pip install passlib
pip install py7zr
pip install rarfile
pip install pypdf
pip install msoffcrypto-tool
pip install python-gnupg
pip install pykeepass
pip install cryptography
pip install requests
pip install paramiko
pip install aiohttp
pip install numpy
pip install matplotlib
pip install flask
pip install flask-limiter
pip install tqdm
pip install rich
pip install pymysql
pip install psycopg2-binary
pip install pysnmp
```

---

# 🛠 Optional External Tools

Install for maximum functionality.

## Hashcat

```bash
sudo apt install hashcat
```

## VeraCrypt

```bash
sudo apt install veracrypt
```

## 7zip

```bash
sudo apt install p7zip-full
```

## UnRAR

```bash
sudo apt install unrar
```

## OpenSSL

```bash
sudo apt install openssl
```

---

# 🚀 Running OBLIVION

```bash
python3 oblivion.py
```

or

```bash
python3 oblivion_testing_5.py
```

---

# 📂 Project Structure

```text
OBLIVION/
│
├── plugins/
├── reports/
├── wordlists/
├── oblivion.py
├── requirements.txt
├── README.md
│
├── oblivion.log
├── oblivion_results.json
├── oblivion_report.json
├── oblivion_report.csv
├── oblivion_report.md
└── oblivion_report.html
```

---

# 🔍 Example Workflow

## Step 1

Load target hash.

```text
5f4dcc3b5aa765d61d8327deb882cf99
```

## Step 2

Select algorithm.

```text
MD5
```

## Step 3

Choose wordlist.

```text
rockyou.txt
```

## Step 4

Run attack.

```text
Dictionary Attack
```

## Step 5

Review report.

```text
oblivion_report.html
```

---

# 🧩 Plugin Development

Create:

```python
from oblivion import Plugin

class CustomPlugin(Plugin):

    def run(self,args):
        print("Plugin Loaded")
```

Save as:

```text
plugins/custom.py
```

Restart framework.

---

# 🏆 Why OBLIVION?

### Compared to Simple Password Tools

| Feature               | OBLIVION |
| --------------------- | -------- |
| Multi-Core Processing | ✅        |
| Hash Detection        | ✅        |
| Rule Engine           | ✅        |
| Checkpoint Recovery   | ✅        |
| Reporting             | ✅        |
| Batch Processing      | ✅        |
| Plugin Support        | ✅        |
| Hashcat Integration   | ✅        |
| CTF Mode              | ✅        |
| Password Intelligence | ✅        |

---

# 🔒 Security Notes

OBLIVION is intended for:

✅ Security Research

✅ Education

✅ Home Labs

✅ CTF Competitions

✅ Authorized Assessments

---

Not intended for:

❌ Unauthorized Access

❌ Illegal Activities

❌ Systems Without Permission

❌ Malicious Use

---



# 👨‍💻 Author

## Nishil Bhimani

```text
Student • Cybersecurity Enthusiast
Reverse Engineering
OSINT
Pentesting
Forensics
CTF Player
```

GitHub:

```text
https://github.com/realnishil
```

---

<div align="center">

## 💀 OBLIVION V6.6

### "Knowledge is Power. Authorization is Mandatory."

⭐ Star the repository if you found it useful.

</div>
