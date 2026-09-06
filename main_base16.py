import smtplib
import os
import time
import json
from email.message import EmailMessage
from datetime import datetime

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

STATE_FILE = "state_base16.json"
HISTORY_FILE = "daily_history_base16.json"
JACKPOT_FILE = "jackpots_base16.json"

# Valid Base 16 search digits (excluding '0' and '1')
VALID_HEX_DIGITS = ['2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
HEX_DIGIT_MAP = {d: i for i, d in enumerate(VALID_HEX_DIGITS)}
HEX_VAL_MAP = {
    '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
    'A': 10, 'B': 11, 'C': 12, 'D': 13, 'E': 14, 'F': 15
}

# Hexadecimal candidate search range
MIN_HEX_LEN = 8
MAX_HEX_LEN = 30

def get_start_candidate():
    """Loads saved state or initializes to the starting Hex candidate length."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                cand = data.get("last_candidate", "2" * MIN_HEX_LEN)
                if len(cand) > MAX_HEX_LEN or len(cand) < MIN_HEX_LEN:
                    return "2" * MIN_HEX_LEN
                return cand
        except Exception:
            pass
    return "2" * MIN_HEX_LEN

def save_state(last_candidate):
    """Saves current Hex candidate position to state_base16.json."""
    with open(STATE_FILE, "w") as f:
        json.dump({"last_candidate": last_candidate}, f, indent=2)

def next_candidate(current_str):
    """Generates the next lexicographically sorted Hex candidate string."""
    chars = list(current_str)
    for i in range(len(chars) - 1, -1, -1):
        if chars[i] != 'F':
            next_digit = VALID_HEX_DIGITS[HEX_DIGIT_MAP[chars[i]] + 1]
            for j in range(i, len(chars)):
                chars[j] = next_digit
            return "".join(chars)
    
    # Increase digit length, wrap around if MAX_HEX_LEN is reached
    next_len = len(chars) + 1
    if next_len > MAX_HEX_LEN:
        return "2" * MIN_HEX_LEN
    return "2" * next_len

def get_base16_persistence(cand_str):
    """Calculates multiplicative persistence in Base 16."""
    # Step 1: Product of hex digits from candidate string
    prod = 1
    for char in cand_str:
        prod *= HEX_VAL_MAP[char]
    
    steps = 1
    # Subsequent steps: Hexadecimal digit extraction via integer modulo 16
    while prod >= 16:
        temp = prod
        prod = 1
        while temp > 0:
            temp, digit = divmod(temp, 16)
            prod *= digit
        steps += 1
    return steps

def log_jackpot(cand_str, persistence):
    """Logs brand new world records (Persistence >= 9 in Base 16)."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "hex_candidate": cand_str,
        "persistence": persistence
    }
    with open(JACKPOT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_daily_summary(best_cand, best_persistence, total_checked, end_candidate):
    """Appends execution metrics to daily_history_base16.json."""
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_checked": total_checked,
        "max_persistence": best_persistence,
        "winning_hex_candidate": str(best_cand),
        "ended_at_candidate": end_candidate
    }
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_report(best_cand, best_persistence, total_checked, hit_jackpot):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email credentials missing. Skipping email report.")
        return

    msg = EmailMessage()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    subject = (
        f"🚨 WORLD RECORD: Base 16 Persistence {best_persistence}!" 
        if hit_jackpot 
        else f"Daily Base 16 Report: Max Persistence {best_persistence}"
    )
    
    body = (
        f"Daily Base 16 Multiplicative Persistence Report - {date_str}\n"
        f"{'-'*45}\n"
        f"Hex Candidates Checked: {total_checked:,}\n"
        f"Max Base 16 Persistence Found: {best_persistence}\n"
        f"Winning Hex Candidate: {best_cand}\n"
    )
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("Daily Base 16 report emailed successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def search_and_report():
    max_p = -1
    best_cand = None
    total_checked = 0
    hit_jackpot = False
    
    current_str = get_start_candidate()
    print(f"Resuming Base 16 search from candidate ({len(current_str)} hex digits): {current_str}")

    run_duration = 4.5 * 60 * 60 
    start_time = time.time()
    
    while time.time() - start_time < run_duration:
        current_str = next_candidate(current_str)
        
        p = get_base16_persistence(current_str)
        
        # Base 16 known world record is 8. Anything >= 9 is a brand new world record!
        if p >= 9:
            hit_jackpot = True
            log_jackpot(current_str, p)
            print(f"CRITICAL FIND: Base 16 Persistence {p} on candidate {current_str}")
            
        if p > max_p:
            max_p = p
            best_cand = current_str
            
        total_checked += 1

    print("Time limit reached. Saving Base 16 state and logs...")
    save_state(current_str)
    log_daily_summary(best_cand, max_p, total_checked, current_str)
    send_report(best_cand, max_p, total_checked, hit_jackpot)

if __name__ == "__main__":
    search_and_report()
