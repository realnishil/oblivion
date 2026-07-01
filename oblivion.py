#!/usr/bin/env python3
"""
Oblivion V1.0 by Nishil Bhimani
--------------------------------
Educational, LOCAL-ONLY password strength / brute-force *simulation* tool.

Everything in this script operates against an in-memory SHA-256 hash that
lives inside this process. There is no networking, no attacking of live
services, and no credential checking against any real system. It exists to
help people visualize why weak passwords fall quickly to simple wordlists,#!/usr/bin/env python3
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
import math
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
          c("https://github.com/nishilxy/Brute-Force-by-Nish", C.BRIGHT_BLUE))
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


# ----------------------------------------------------------------------------
# Advanced mutation engine
#
# These functions mirror, at a conceptual level, the rule-based mutation
# systems used by real-world cracking tools (Hashcat rule files, John the
# Ripper's rules engine). They exist so the simulation can demonstrate WHY
# "clever" substitutions like p@ssw0rd don't meaningfully improve security:
# these transforms are exactly the first things any real attacker's rule set
# tries. Everything below only ever produces candidate strings in memory and
# tests them against the local sample hash defined at the top of this file.
# ----------------------------------------------------------------------------

LEET_MAP = {
    "a": ["a", "@", "4"],
    "e": ["e", "3"],
    "i": ["i", "1", "!"],
    "o": ["o", "0"],
    "s": ["s", "$", "5"],
    "t": ["t", "7"],
    "b": ["b", "8"],
    "g": ["g", "9"],
    "l": ["l", "1"],
}

COMMON_SUFFIXES = ["", "1", "12", "123", "1234", "!", "!!", "@", "#",
                   "2023", "2024", "2025", "2026", "01", "007"]
COMMON_PREFIXES = ["", "The", "My", "I", "Mr", "Mrs"]

KEYBOARD_WALKS = [
    "qwerty", "asdf", "zxcv", "1qaz", "qazwsx", "1q2w3e",
    "qwertyuiop", "asdfghjkl",
]


def case_variants(word, limit=8):
    """Generate common capitalization patterns for a word."""
    variants = {
        word.lower(),
        word.upper(),
        word.capitalize(),
        word[:1].upper() + word[1:].lower() if word else word,
    }
    # alternating case, e.g. pAsSwOrD — a pattern people mistakenly think
    # adds real entropy
    alt = "".join(ch.upper() if i % 2 else ch.lower()
                  for i, ch in enumerate(word))
    variants.add(alt)
    return list(variants)[:limit]


def leet_variants(word, max_variants=32):
    """
    Generate a bounded set of leetspeak substitutions for a word.
    Full combinatorial leet-speak explodes exponentially, so this caps
    output and prioritizes single/double-substitution variants, which
    covers the overwhelming majority of real-world 'clever' passwords.
    """
    word = word.lower()
    variants = {word}
    positions = [i for i, ch in enumerate(word) if ch in LEET_MAP]

    # single-character substitutions
    for pos in positions:
        for sub in LEET_MAP[word[pos]]:
            variants.add(word[:pos] + sub + word[pos + 1:])

    # double-character substitutions (two positions at once)
    for a_idx in range(len(positions)):
        for b_idx in range(a_idx + 1, len(positions)):
            pa, pb = positions[a_idx], positions[b_idx]
            for sub_a in LEET_MAP[word[pa]]:
                for sub_b in LEET_MAP[word[pb]]:
                    candidate = list(word)
                    candidate[pa] = sub_a
                    candidate[pb] = sub_b
                    variants.add("".join(candidate))
                    if len(variants) >= max_variants:
                        return list(variants)[:max_variants]

    return list(variants)[:max_variants]


def rule_based_mutate(base_words, max_words=5000):
    """
    Apply a Hashcat/John-style rule chain to a small seed list:
    case variants -> leetspeak substitutions -> prefix/suffix appends.
    This is the technique real cracking tools use to turn a handful of
    seed words (names, pet names, sports teams, etc.) into tens of
    thousands of realistic guesses.
    """
    out = []
    seen = set()

    def add(word):
        if word not in seen:
            seen.add(word)
            out.append(word)

    for base in base_words:
        for cased in case_variants(base):
            add(cased)
            for leeted in leet_variants(cased, max_variants=12):
                add(leeted)
                if len(out) >= max_words:
                    return out
            if len(out) >= max_words:
                return out

    # apply prefix/suffix rules on top of everything generated so far
    mutated = list(out)
    for word in mutated:
        for prefix in COMMON_PREFIXES:
            for suffix in COMMON_SUFFIXES:
                candidate = f"{prefix}{word}{suffix}"
                add(candidate)
                if len(out) >= max_words:
                    return out

    return out[:max_words]


def mask_attack_generate(mask, max_words=200000):
    """
    Generate candidates from a Hashcat-style mask pattern:
      ?l = lowercase letter    ?u = uppercase letter
      ?d = digit                ?s = common special char
      Any other character in the mask is treated as a literal.

    Example: '?u?l?l?l?l?d?d?d?d' -> Name1234-style guesses.
    Mask attacks are how real tools brute-force *structured* passwords
    (e.g. 'Capital word + 4 digits') far faster than pure random
    brute force, because they skip character combinations that don't
    match the assumed structure.
    """
    charsets = {
        "l": "abcdefghijklmnopqrstuvwxyz",
        "u": "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "d": "0123456789",
        "s": "!@#$%^&*",
    }

    tokens = []
    i = 0
    while i < len(mask):
        if mask[i] == "?" and i + 1 < len(mask) and mask[i + 1] in charsets:
            tokens.append(charsets[mask[i + 1]])
            i += 2
        else:
            tokens.append(mask[i])
            i += 1

    # estimate total keyspace; refuse to silently truncate without warning
    total = 1
    for t in tokens:
        total *= len(t) if len(t) > 1 else 1
    total = max(total, 1)

    out = []
    if total <= max_words:
        # exact, deterministic generation for small keyspaces
        def build(prefix, idx):
            if idx == len(tokens):
                out.append(prefix)
                return
            t = tokens[idx]
            if len(t) == 1:
                build(prefix + t, idx + 1)
            else:
                for ch in t:
                    build(prefix + ch, idx + 1)
        build("", 0)
    else:
        # keyspace too large to enumerate fully in a demo -> random sample
        for _ in range(max_words):
            candidate = "".join(
                random.choice(t) if len(t) > 1 else t for t in tokens
            )
            out.append(candidate)

    return out, total


def hybrid_attack_generate(base_words, mask_suffix="?d?d?d?d", max_words=20000):
    """
    Hybrid attack: dictionary word + mask-generated suffix.
    This is one of the most effective real-world techniques, since most
    people append a short structured pattern (year, PIN, sequence) to a
    memorable word rather than choosing something fully random.
    """
    suffixes, _ = mask_attack_generate(mask_suffix, max_words=200)
    out = []
    for base in base_words:
        for cased in case_variants(base, limit=3):
            for suf in suffixes:
                out.append(cased + suf)
                if len(out) >= max_words:
                    return out
    return out


def run_rule_based_attack():
    print(c("\nRule-based mutation attack (Hashcat/John-style rules).",
             C.BRIGHT_CYAN, C.BOLD))
    print(c("Enter one or more seed words (name, pet, team, etc.). Each "
            "will be expanded through case, leetspeak, and affix rules.",
            C.DIM))
    raw = input("Seed words (comma-separated): ").strip()
    if not raw:
        print(c("At least one seed word required.", C.BRIGHT_RED))
        return []
    base_words = [w.strip() for w in raw.split(",") if w.strip()]
    try:
        max_words = int(input("Max candidates to generate [default 5000]: ") or "5000")
    except ValueError:
        max_words = 5000

    candidates = rule_based_mutate(base_words, max_words=max_words)
    print(c(f"Generated {len(candidates)} rule-mutated candidates. Sample:",
             C.BRIGHT_GREEN))
    for i, w in enumerate(candidates[:20], 1):
        print(f"{i:3d}. {w}")

    run = input("Run simulation with this candidate list now? (y/N): ").strip().lower()
    if run == "y":
        simulate_bruteforce(candidates)
    return candidates


def run_mask_attack():
    print(c("\nMask attack (pattern-based brute force).", C.BRIGHT_CYAN, C.BOLD))
    print(c("Build a pattern using: ?l lowercase  ?u uppercase  ?d digit  "
            "?s special. Any other character is literal.", C.DIM))
    print(c("Example: ?u?l?l?l?l?d?d?d?d  ->  Word1234-style guesses",
             C.DIM))
    mask = input("Mask pattern: ").strip()
    if not mask:
        print(c("Mask required.", C.BRIGHT_RED))
        return []
    try:
        max_words = int(input("Max candidates to generate [default 5000]: ") or "5000")
    except ValueError:
        max_words = 5000

    candidates, total = mask_attack_generate(mask, max_words=max_words)
    print(c(f"Full keyspace for this mask: ~{total:,} combinations",
             C.BRIGHT_BLUE))
    if total > max_words:
        print(c(f"Keyspace exceeds max_words — showing a random sample of "
                f"{len(candidates)} instead of full enumeration.",
                C.BRIGHT_YELLOW))
    print(c(f"Generated {len(candidates)} candidates. Sample:", C.BRIGHT_GREEN))
    for i, w in enumerate(candidates[:20], 1):
        print(f"{i:3d}. {w}")

    run = input("Run simulation with this candidate list now? (y/N): ").strip().lower()
    if run == "y":
        simulate_bruteforce(candidates)
    return candidates


def run_hybrid_attack():
    print(c("\nHybrid attack (dictionary word + mask suffix).",
             C.BRIGHT_CYAN, C.BOLD))
    print(c("Combines memorable base words with a structured suffix "
            "pattern — the most common real-world password shape.",
            C.DIM))
    raw = input("Base words (comma-separated): ").strip()
    if not raw:
        print(c("At least one base word required.", C.BRIGHT_RED))
        return []
    base_words = [w.strip() for w in raw.split(",") if w.strip()]
    mask_suffix = input("Suffix mask [default ?d?d?d?d]: ").strip() or "?d?d?d?d"
    try:
        max_words = int(input("Max candidates to generate [default 5000]: ") or "5000")
    except ValueError:
        max_words = 5000

    candidates = hybrid_attack_generate(base_words, mask_suffix=mask_suffix,
                                         max_words=max_words)
    print(c(f"Generated {len(candidates)} hybrid candidates. Sample:",
             C.BRIGHT_GREEN))
    for i, w in enumerate(candidates[:20], 1):
        print(f"{i:3d}. {w}")

    run = input("Run simulation with this candidate list now? (y/N): ").strip().lower()
    if run == "y":
        simulate_bruteforce(candidates)
    return candidates


# ----------------------------------------------------------------------------
# Markov-chain smart guesser
#
# Instead of guessing randomly, this builds a character transition model
# from a small corpus of example passwords/words and generates candidates
# in an order weighted toward statistically "human-like" sequences. This
# mirrors, at a toy scale, how real password-cracking research (e.g.
# academic Markov-model crackers) prioritizes likely candidates over pure
# brute force.
# ----------------------------------------------------------------------------

MARKOV_SEED_CORPUS = [
    "password", "letmein", "welcome", "monkey", "dragon", "sunshine",
    "princess", "football", "baseball", "iloveyou", "admin", "qwerty",
    "shadow", "master", "superman", "trustno1", "michael", "jennifer",
    "hunter", "ranger", "buster", "soccer", "hockey", "killer", "george",
    "computer", "michelle", "jessica", "pepper", "daniel", "access",
]


def build_markov_model(corpus, order=2):
    """
    Build an order-N character-level Markov model: maps a context of
    `order` previous characters to a weighted list of next characters.
    Also tracks starting contexts so generation begins realistically.
    """
    model = {}
    starts = []
    for word in corpus:
        word = word.lower()
        if len(word) <= order:
            continue
        starts.append(word[:order])
        for i in range(len(word) - order):
            context = word[i:i + order]
            nxt = word[i + order]
            model.setdefault(context, []).append(nxt)
    return model, starts


def markov_generate(model, starts, length_range=(5, 10), max_words=2000, order=2):
    """Generate candidate passwords by walking the Markov chain."""
    if not starts:
        return []
    out = []
    seen = set()
    attempts_cap = max_words * 20  # avoid infinite loop if model is sparse
    tries = 0
    while len(out) < max_words and tries < attempts_cap:
        tries += 1
        target_len = random.randint(*length_range)
        word = random.choice(starts)
        while len(word) < target_len:
            context = word[-order:]
            choices = model.get(context)
            if not choices:
                break
            word += random.choice(choices)
        if len(word) >= 3 and word not in seen:
            seen.add(word)
            out.append(word)
    return out


def run_markov_attack():
    print(c("\nMarkov-chain smart guesser (local simulation).",
             C.BRIGHT_CYAN, C.BOLD))
    print(c("Trains a character-transition model on a small built-in "
            "corpus of common passwords, then generates candidates that "
            "'sound' human rather than pure random noise.", C.DIM))
    try:
        max_words = int(input("How many candidates to generate "
                               "[default 1000]: ") or "1000")
    except ValueError:
        max_words = 1000

    model, starts = build_markov_model(MARKOV_SEED_CORPUS, order=2)
    candidates = markov_generate(model, starts, max_words=max_words)
    print(c(f"Generated {len(candidates)} Markov-weighted candidates. "
            f"Sample:", C.BRIGHT_GREEN))
    for i, w in enumerate(candidates[:15], 1):
        print(f"{i:3d}. {w}")

    run = input("Run simulation with this candidate list now? (y/N): ").strip().lower()
    if run == "y":
        simulate_bruteforce(candidates)


# ----------------------------------------------------------------------------
# Entropy & crack-time estimator
#
# This is the part that actually answers "how complex is this password":
# real strength isn't a heuristic score, it's how large the effective
# search space is, and how long that space takes to exhaust at a given
# guess rate. This models a few realistic guess-rate scenarios (online
# rate-limited login, offline fast hash, offline slow/salted hash).
# ----------------------------------------------------------------------------

GUESS_RATE_SCENARIOS = [
    ("Online, rate-limited login (e.g. 10 guesses/min)", 10 / 60),
    ("Online, no rate limit (e.g. 100 guesses/sec)", 100),
    ("Offline, fast unsalted hash (e.g. MD5, ~10 billion/sec on GPU)", 1e10),
    ("Offline, slow adaptive hash (e.g. bcrypt, ~10,000/sec)", 1e4),
]


def estimate_charset_size(password):
    size = 0
    if any(ch.islower() for ch in password):
        size += 26
    if any(ch.isupper() for ch in password):
        size += 26
    if any(ch.isdigit() for ch in password):
        size += 10
    if any(not ch.isalnum() for ch in password):
        size += 33  # common printable specials
    return max(size, 1)


def format_duration(seconds):
    if seconds < 1:
        return "< 1 second"
    units = [
        ("centuries", 60 * 60 * 24 * 365 * 100),
        ("years", 60 * 60 * 24 * 365),
        ("days", 60 * 60 * 24),
        ("hours", 60 * 60),
        ("minutes", 60),
        ("seconds", 1),
    ]
    for name, unit_seconds in units:
        if seconds >= unit_seconds:
            value = seconds / unit_seconds
            if value > 1e6:
                return f"{value:.2e} {name}"
            return f"{value:,.1f} {name}"
    return f"{seconds:.1f} seconds"


def run_entropy_analyzer():
    print(c("\nPassword Entropy & Crack-Time Estimator (local-only).",
             C.BRIGHT_CYAN, C.BOLD))
    pw = getpass.getpass("Enter password to analyze (hidden): ")
    if not pw:
        print(c("No password entered.", C.BRIGHT_RED))
        return

    charset = estimate_charset_size(pw)
    entropy_bits = len(pw) * math.log2(charset)
    keyspace = charset ** len(pw)

    print(c(f"\nLength: {len(pw)}  |  Estimated charset size: {charset}",
             C.BRIGHT_BLUE))
    print(c(f"Estimated entropy: {entropy_bits:.1f} bits", C.BRIGHT_BLUE, C.BOLD))
    print(c(f"Theoretical keyspace: ~{keyspace:.3e} possible combinations",
             C.DIM))

    print(c("\nWorst-case average time to exhaust the full keyspace "
            "(random guessing, no dictionary shortcuts):", C.BRIGHT_CYAN))
    for label, rate in GUESS_RATE_SCENARIOS:
        seconds = (keyspace / 2) / rate  # average case = half the keyspace
        print(f"  {c(label, C.YELLOW)}: "
              f"{c(format_duration(seconds), C.BRIGHT_GREEN, C.BOLD)}")

    print(c("\nNote: this assumes no dictionary/pattern shortcuts. Real "
            "attackers use rule-based mutation and Markov models (see "
            "menu options 7 & 9) to crack structured or dictionary-based "
            "passwords far faster than this worst-case estimate.", C.DIM))


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
    print(c(c(" -- Advanced algorithms --", C.BRIGHT_MAGENTA, C.BOLD)))
    print(c(" 7)", C.BRIGHT_BLUE), "Rule-based mutation attack (leetspeak, case, affixes)")
    print(c(" 8)", C.BRIGHT_BLUE), "Mask attack (pattern-based brute force)")
    print(c(" 9)", C.BRIGHT_BLUE), "Hybrid attack (dictionary word + mask suffix)")
    print(c("10)", C.BRIGHT_BLUE), "Markov-chain smart guesser")
    print(c("11)", C.BRIGHT_BLUE), "Password entropy & crack-time estimator")
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
        elif choice == "7":
            run_rule_based_attack()
        elif choice == "8":
            run_mask_attack()
        elif choice == "9":
            run_hybrid_attack()
        elif choice == "10":
            run_markov_attack()
        elif choice == "11":
            run_entropy_analyzer()
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
