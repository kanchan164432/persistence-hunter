import smtplib
import os
import time
import json
from email.message import EmailMessage
from datetime import datetime

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

STATE_FILE = "state_prime15.json"
HISTORY_FILE = "daily_history_prime15.json"
JACKPOT_FILE = "jackpots_prime15.json"

DEFAULT_START_E = 1
CHUNK_SIZE = 15  # Number of exponent sum levels to evaluate per 4.5-hour run

def load_start_exponent():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                data = json.load(f)
                return data.get("next_exponent_sum", DEFAULT_START_E)
        except Exception:
            pass
    return DEFAULT_START_E

def save_state(next_exponent_sum):
    with open(STATE_FILE, "w") as f:
        json.dump({"next_exponent_sum": next_exponent_sum}, f, indent=2)

def get_persistence_b15(n):
    """Calculates multiplicative persistence in Base 15."""
    steps = 0
    while n >= 15:
        prod = 1
        temp = n
        while temp > 0:
            temp, digit = divmod(temp, 15)
            prod *= digit
        n = prod
        steps += 1
    return steps

def log_jackpot(E, exponents, P1, persistence):
    """Logs discoveries hitting persistence >= 16."""
    entry = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exponent_sum": E,
        "prime_exponents": exponents,
        "P1": str(P1),
        "persistence": persistence
    }
    with open(JACKPOT_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def log_daily_summary(best_p, best_exp, total_checked, end_E):
    entry = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "total_checked": total_checked,
        "max_persistence": best_p,
        "winning_exponents": best_exp,
        "ended_at_E": end_E
    }
    with open(HISTORY_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_report(best_p, best_exp, total_checked, hit_jackpot):
    if not EMAIL_USER or not EMAIL_PASS:
        print("Email credentials missing. Skipping email report.")
        return

    msg = EmailMessage()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    subject = (
        f"🚨 HISTORIC RECORD: Base 15 Persistence {best_p}!" 
        if hit_jackpot 
        else f"Daily Base 15 Report: Max Persistence {best_p}"
    )
    
    body = (
        f"Daily Base 15 Multiplicative Persistence Report - {date_str}\n"
        f"{'-'*50}\n"
        f"Product Trees Checked: {total_checked:,}\n"
        f"Max Persistence Found: {best_p}\n"
        f"Winning Prime Exponents: {best_exp}\n"
    )
    msg.set_content(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465, timeout=10) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("Daily Base 15 report emailed successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def search_base15_prime_tree():
    start_E = load_start_exponent()
    end_E = start_E + CHUNK_SIZE
    max_p = -1
    best_exp = None
    total_checked = 0
    hit_jackpot = False
    
    print(f"Resuming Base 15 Prime Tree Search from E = {start_E} to {end_E}...")
    run_duration = 4.5 * 60 * 60
    start_time = time.time()

    for E in range(start_E, end_E + 1):
        if time.time() - start_time > run_duration:
            print(f"Time limit reached. Saving state at E = {E}...")
            save_state(E)
            log_daily_summary(max_p, best_exp, total_checked, E)
            send_report(max_p, best_exp, total_checked, hit_jackpot)
            return

        for a in range(E + 1):
            for b in range(E + 1 - a):
                for c in range(E + 1 - a - b):
                    # Base 15 Zero-Trap Optimization: 15 = 3 * 5.
                    # If P1 contains both 3 (b > 0) and 5 (c > 0), P1 % 15 == 0 (ends in 0 in Base 15).
                    if b > 0 and c > 0:
                        continue
                        
                    for d in range(E + 1 - a - b - c):
                        for e in range(E + 1 - a - b - c - d):
                            f = E - a - b - c - d - e
                            
                            # Candidate product P1 = 2^a * 3^b * 5^c * 7^d * 11^e * 13^f
                            P1 = (2**a) * (3**b) * (5**c) * (7**d) * (11**e) * (13**f)
                            
                            p = 1 + get_persistence_b15(P1)
                            total_checked += 1

                            # Jackpot threshold set to target persistence >= 16
                            if p >= 16:
                                hit_jackpot = True
                                exps = {"2": a, "3": b, "5": c, "7": d, "11": e, "13": f}
                                log_jackpot(E, exps, P1, p)
                                print(f"🚨 WORLD RECORD: Persistence {p} at E={E}! Exponents: {exps}")

                            if p > max_p:
                                max_p = p
                                best_exp = {"2": a, "3": b, "5": c, "7": d, "11": e, "13": f}
                                print(f"NEW BASE 15 HIGH: Persistence {max_p} at E={E}")

    save_state(end_E + 1)
    log_daily_summary(max_p, best_exp, total_checked, end_E + 1)
    send_report(max_p, best_exp, total_checked, hit_jackpot)
    print(f"Finished chunk. Saved next state E = {end_E + 1}")

if __name__ == "__main__":
    search_base15_prime_tree()
