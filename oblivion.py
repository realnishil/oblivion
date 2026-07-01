#!/usr/bin/env python3
"""
Oblivion V1.0 by Nishil Bhimani
--------------------------------
Educational, LOCAL-ONLY password strength / brute-force *simulation* tool.

Everything in this script operates against an in-memory SHA-256 hash that
lives inside this process. There is no networking, no attacking of live
services, and no credential checking against any real system. It exists to
help people visualize why weak passwords fall quickly to simple wordlists,
and why defenses like lockouts, MFA, and slow hashing matter.

Use only on data/accounts you own, and never repurpose this against systems
or accounts you don't have explicit permission to test.
"""

import time
import hashlib
import getpass
import random
import sys
from datetime import datetime

# ----------------------------------------------------------------------------
# Config
# ----------------------------------------------------------------------------
MAX_ATTEMPTS_BEFORE_LOCK = 5
LOCK_DURATION_SECONDS = 30
THROTTLE_SECONDS = 0.5
ATTEMPT_LOG = "sim_attempts.log"

REAL_USERNAME = "testuser"
REAL_PASSWORD_PLAIN = "nish"
REAL_PASSWORD_HASH = hashlib.sha256(REAL_PASSWORD_PLAIN.encode()).hexdigest()


# ----------------------------------------------------------------------------
# Colors (raw ANSI, no external deps)
# ----------------------------------------------------------------------------
class C:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"

    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"


def supports_color():
    return sys.stdout.isatty()


USE_COLOR = supports_color()


def c(text, *codes):
    """Wrap text in ANSI codes if the terminal supports color."""
    if not USE_COLOR:
        return text
    return "".join(codes) + text + C.RESET


# ----------------------------------------------------------------------------
# ASCII banner
# ----------------------------------------------------------------------------
OBLIVION_ART = r"""
   ____  ____  _     _______   _____ ____  _   __
  / __ \/ __ )| |   /  _/ \ \ / /  _// __ \/ | / /
 / / / / __  || |   / / \ \ V / / / / / / /  |/ /
/ /_/ / /_/ / | |__/ /   \ /_/ /_/ / /_/ / /|  /
\____/_____/  |____/_/    (_)/___/\____/_/ |_/
"""


def print_banner():
    if USE_COLOR:
        gradient = [C.BRIGHT_MAGENTA, C.MAGENTA, C.BRIGHT_BLUE, C.BLUE, C.BRIGHT_CYAN]
        lines = OBLIVION_ART.splitlines()
        for i, line in enumerate(lines):
            color = gradient[i % len(gradient)]
            print(c(line, color, C.BOLD))
    else:
        print(OBLIVION_ART)

    print(c("           Oblivion V1.0  ·  by Nishil Bhimani", C.BRIGHT_CYAN, C.BOLD))
    print(c("     Educational brute-force & password-strength simulator",
             C.DIM))
    print()
    print(c("=" * 66, C.DIM))
    print(c(" DISCLAIMER", C.BRIGHT_YELLOW, C.BOLD))
    print(c(" Oblivion is an educational security tool for learning purposes", C.YELLOW))
    print(c(" only. All 'attacks' run against an in-memory sample password —", C.YELLOW))
    print(c(" nothing here touches real accounts, files, or networks.", C.YELLOW))
    print(c(" Only use techniques like this on systems you own or have", C.YELLOW))
    print(c(" explicit written permission to test. Unauthorized use against", C.YELLOW))
    print(c(" systems you don't own is illegal and unethical.", C.YELLOW))
    print(c("=" * 66, C.DIM))
    print(c(" Status: BETA", C.BRIGHT_RED, C.BOLD) +
          c("   ·   ", C.DIM) +
          c("https://github.com/realnishil/oblivion", C.BRIGHT_BLUE))
    print()


# ----------------------------------------------------------------------------
# Core logic
# ----------------------------------------------------------------------------
def log_attempt(username, attempt, success):
    ts = datetime.now().isoformat()
    with open(ATTEMPT_LOG, "a") as f:
        f.write(f"{ts}\t{username}\t{attempt}\t{'SUCCESS' if success else 'FAIL'}\n")


def check_password(password_guess):
    """Simulated password check against in-memory hash. No IO/network."""
    return hashlib.sha256(password_guess.encode()).hexdigest() == REAL_PASSWORD_HASH


def password_strength(password):
    """Simple strength heuristic (educational). Returns (score, notes)."""
    score = 0
    notes = []
    if len(password) >= 12:
        score += 2
    elif len(password) >= 8:
        score += 1
    else:
        notes.append("Too short (use >= 12 chars for strong).")
    if any(c_.islower() for c_ in password):
        score += 1
    else:
        notes.append("Add lowercase letters.")
    if any(c_.isupper() for c_ in password):
        score += 1
    else:
        notes.append("Add uppercase letters.")
    if any(c_.isdigit() for c_ in password):
        score += 1
    else:
        notes.append("Add digits.")
    if any(not c_.isalnum() for c_ in password):
        score += 1
    else:
        notes.append("Add special characters like !@#$.")
    return score, notes


def generate_wordlist(base, max_len=3, digits="0123456789", max_words=10000):
    suffixes = ["", "123", "!", "@", "2023", "2024", "2025", "2026"]
    out = []
    for suf in suffixes:
        candidate = base + suf
        out.append(candidate)
        if len(out) >= max_words:
            break
    for l in range(1, max_len + 1):
        for _ in range(min(100, len(digits) ** l)):
            s = "".join(random.choice(digits) for _ in range(l))
            out.append(base + s)
            if len(out) >= max_words:
                break
        if len(out) >= max_words:
            break
    return out


def simulate_bruteforce(wordlist, username=REAL_USERNAME):
    attempts = 0
    locked_until = 0
    print(c(f"\nStarting simulation against local account '{username}'.",
             C.BRIGHT_CYAN, C.BOLD))
    for pw in wordlist:
        now = time.time()
        if now < locked_until:
            wait = int(locked_until - now)
            print(c(f"[LOCKED] Account locked for {wait} more second(s).",
                     C.BRIGHT_RED, C.BOLD))
            time.sleep(min(wait, 3))
            continue

        attempts += 1
        print(f"Attempt {c(str(attempts), C.BRIGHT_BLUE)}: trying "
              f"{c(repr(pw), C.YELLOW)} ... ", end="", flush=True)
        time.sleep(THROTTLE_SECONDS)

        success = check_password(pw)
        log_attempt(username, pw, success)
        if success:
            print(c("SUCCESS!", C.BRIGHT_GREEN, C.BOLD))
            print(c(f"Password cracked in {attempts} attempts (simulation).",
                     C.BRIGHT_GREEN, C.BOLD))
            return True
        else:
            print(c("fail", C.RED))
            if attempts % MAX_ATTEMPTS_BEFORE_LOCK == 0:
                locked_until = time.time() + LOCK_DURATION_SECONDS
                print(c(f"[DEFENSE] Simulated lockout activated for "
                        f"{LOCK_DURATION_SECONDS}s.", C.BRIGHT_MAGENTA, C.BOLD))
    print(c("Finished wordlist; password not found in the provided list "
            "(simulation).", C.DIM))
    return False


def run_password_checker():
    print(c("\nPassword Strength Checker (local-only).", C.BRIGHT_CYAN, C.BOLD))
    pw = getpass.getpass("Enter password to evaluate (hidden): ")
    score, notes = password_strength(pw)

    if score >= 5:
        score_color = C.BRIGHT_GREEN
    elif score >= 3:
        score_color = C.BRIGHT_YELLOW
    else:
        score_color = C.BRIGHT_RED

    print(c(f"Score: {score}/6", score_color, C.BOLD))
    if notes:
        print(c("Suggestions:", C.YELLOW))
        for n in notes:
            print(c(" - ", C.YELLOW) + n)
    else:
        print(c("Looks reasonably strong (educational heuristic).",
                 C.BRIGHT_GREEN))


def make_wordlist_interactive():
    print(c("\nWordlist generator (simple, local).", C.BRIGHT_CYAN, C.BOLD))
    base = input("Base word (e.g., name or root): ").strip()
    if not base:
        print(c("Base required.", C.BRIGHT_RED))
        return []
    try:
        max_len = int(input("Max digit suffix length (1-4) [default 2]: ") or "2")
    except ValueError:
        max_len = 2
    try:
        max_words = int(input("Max words to generate [default 500]: ") or "500")
    except ValueError:
        max_words = 500

    wl = generate_wordlist(base, max_len=max_len, max_words=max_words)
    print(c(f"Generated {len(wl)} words. Sample:", C.BRIGHT_GREEN))
    for i, w in enumerate(wl[:20], 1):
        print(f"{i:3d}. {w}")
    save = input("Save to file? (y/N): ").strip().lower()
    if save == "y":
        fname = input("Filename to save (e.g., wordlist.txt): ").strip() or "wordlist.txt"
        with open(fname, "w") as f:
            for w in wl:
                f.write(w + "\n")
        print(c(f"Saved to {fname}", C.BRIGHT_GREEN))
    return wl


def load_wordlist_from_file():
    fname = input("Path to wordlist file: ").strip()
    try:
        with open(fname, "r") as f:
            wl = [line.strip() for line in f if line.strip()]
        print(c(f"Loaded {len(wl)} words from {fname}", C.BRIGHT_GREEN))
        return wl
    except Exception as e:
        print(c(f"Failed to load file: {e}", C.BRIGHT_RED))
        return []


def view_log():
    try:
        with open(ATTEMPT_LOG, "r") as f:
            data = f.read().strip()
            if not data:
                print(c("Log is empty.", C.DIM))
            else:
                print(c("\n--- Attempt log (most recent last) ---",
                         C.BRIGHT_CYAN, C.BOLD))
                for line in data.splitlines()[-50:]:
                    print(line)
    except FileNotFoundError:
        print(c("Log file not found. No attempts logged yet.", C.DIM))


def print_safety_and_defenses():
    print(c("\nSafety & Defense (educational):", C.BRIGHT_CYAN, C.BOLD))
    tips = [
        "Always obtain explicit written permission before testing systems you don't own.",
        "Use rate limiting, progressive delays, and account lockouts to defend against brute-force.",
        "Enforce multi-factor authentication (MFA).",
        "Use slow hash functions (bcrypt, scrypt, Argon2) for password storage.",
        "Require long, random passphrases; avoid common words and predictable patterns.",
        "Monitor and alert on unusual login attempts and velocity.",
        "Use CAPTCHA or device fingerprinting to limit automated attacks.",
    ]
    for t in tips:
        print(c(" - ", C.BRIGHT_GREEN) + t)


# ----------------------------------------------------------------------------
# Menu
# ----------------------------------------------------------------------------
def print_menu():
    print(c("\nOblivion is a tool to guess/crack valid login/password pairs "
            "(simulation).", C.DIM))
    print(c("\nMenu:", C.BRIGHT_CYAN, C.BOLD))
    print(c(" 1)", C.BRIGHT_BLUE), "Simulate brute-force attack (use generated wordlist)")
    print(c(" 2)", C.BRIGHT_BLUE), "Load wordlist from file and simulate")
    print(c(" 3)", C.BRIGHT_BLUE), "Generate wordlist interactively")
    print(c(" 4)", C.BRIGHT_BLUE), "Password strength checker")
    print(c(" 5)", C.BRIGHT_BLUE), "View local attempt log")
    print(c(" 6)", C.BRIGHT_BLUE), "Show safety & defensive tips")
    print(c(" 0)", C.BRIGHT_RED), "Exit")


def main_menu():
    print_banner()

    while True:
        print_menu()
        choice = input(c("\nChoose an option: ", C.BRIGHT_YELLOW)).strip()
        if choice == "1":
            base = input("Base for auto wordlist (e.g., 'password' or 'john'): ").strip() or "password"
            wl = generate_wordlist(base, max_len=2, max_words=500)
            simulate_bruteforce(wl)
        elif choice == "2":
            wl = load_wordlist_from_file()
            if wl:
                simulate_bruteforce(wl)
        elif choice == "3":
            wl = make_wordlist_interactive()
            if wl:
                ask = input("Run simulation with this list now? (y/N): ").strip().lower()
                if ask == "y":
                    simulate_bruteforce(wl)
        elif choice == "4":
            run_password_checker()
        elif choice == "5":
            view_log()
        elif choice == "6":
            print_safety_and_defenses()
        elif choice == "0":
            print(c("Exiting. Remember: test only on systems you own or "
                    "have permission to test.", C.BRIGHT_CYAN))
            break
        else:
            print(c("Invalid choice. Try again.", C.BRIGHT_RED))


if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        print(c("\nInterrupted. Bye.", C.BRIGHT_RED))
        sys.exit(0)
