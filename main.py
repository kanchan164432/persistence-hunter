import smtplib
import os
import time
import json
from email.message import EmailMessage
from datetime import datetime

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

STATE_FILE = "state.json"
VALID_DIGITS = ['2', '3', '4', '6', '7', '8', '9']
DIGIT_MAP = {d: i for i, d in enumerate(VALID_DIGITS)}

# Search range boundaries to stay within high-persistence candidate lengths
MIN_DIGITS = 15
MAX_DIGITS = 35

def get_start_candidate():
    """Loads state, or defaults/resets candidate to the 15-35 digit Goldilocks zone."""
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                cand = data.get("last_candidate", "2" * MIN_DIGITS)
                # Reset automatically if state drifted past 35 digits into the zero-trap range
                if len(cand) > MAX_DIGITS or len(cand) < MIN_DIGITS:
                    return "2" * MIN_DIGITS
                return cand
        except Exception:
            pass
    return "2" * MIN_DIGITS

def save_state(last_candidate):
    """Saves the last processed candidate string for the next execution."""
    with open(STATE_FILE, "w") as f:
        json.dump({"last_candidate": last_candidate}, f, indent=2)

def next_candidate(current_str):
    """Generates next sorted candidate string. Wraps to MIN_DIGITS if MAX_DIGITS is exceeded."""
    chars = list(current_str)
    for i in range(len(chars) - 1, -1, -1):
        if chars[i] != '9':
            next_digit = VALID_DIGITS[DIGIT_MAP[chars[i]] + 1]
            for j in range(i, len(chars)):
                chars[j] = next_digit
            return "".join(chars)
    
    # Increase length, but wrap around to MIN_DIGITS if we exceed MAX_DIGITS
    next_len = len(chars) + 1
    if next_len > MAX_DIGITS:
        return "2" * MIN_DIGITS
    return "2" * next_len

def get_persistence(n):
    """Calculates multiplicative persistence using fast integer arithmetic."""
    steps = 0
    while n >= 10:
        prod = 1
        temp = n
        while temp > 0:
            temp, digit = divmod(temp, 10)
            prod *= digit
        n = prod
        steps += 1
    return steps

def log_jackpot(number, persistence):
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "number": str(number),
        "persistence": persistence
    }
    with open("jackpots.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_daily_summary(best_number, best_persistence, total_checked, end_candidate):
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_checked": total_checked,
        "max_persistence": best_persistence,
        "winning_number": str(best_number),
        "ended_at_candidate": end_candidate
    }
    with open("daily_history.json", "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_report(best_number, best_persistence, total_checked, hit_jackpot):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email credentials missing. Skipping email report.")
        return

    msg = EmailMessage()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    subject = f"🚨 ALERT: Found Persistence {best_persistence}!" if hit_jackpot else f"Daily Report: Max Persistence {best_persistence}"
    
    body = (
        f"Daily Multiplicative Persistence Report - {date_str}\n"
        f"{'-'*40}\n"
        f"Numbers Checked: {total_checked:,}\n"
        f"Max Persistence Found: {best_persistence}\n"
        f"Winning Number: {best_number}\n"
    )
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("Daily report emailed successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def search_and_report():
    max_p = -1
    best_num = None
    total_checked = 0
    hit_jackpot = False
    
    current_str = get_start_candidate()
    print(f"Resuming search from candidate ({len(current_str)} digits): {current_str}")

    # Set duration to 4.5 hours (leaves 1.5 hours safety buffer for GitHub Actions)
    run_duration = 4.5 * 60 * 60 
    start_time = time.time()
    
    while time.time() - start_time < run_duration:
        current_str = next_candidate(current_str)
        candidate = int(current_str)
        
        p = get_persistence(candidate)
        
        if p >= 12:
            hit_jackpot = True
            log_jackpot(candidate, p)
            print(f"CRITICAL FIND: Persistence {p} on number {candidate}")
            
        if p > max_p:
            max_p = p
            best_num = candidate
            
        total_checked += 1

    print("Time limit reached. Saving state and logs...")
    save_state(current_str)
    log_daily_summary(best_num, max_p, total_checked, current_str)
    send_report(best_num, max_p, total_checked, hit_jackpot)

if __name__ == "__main__":
    search_and_report()
