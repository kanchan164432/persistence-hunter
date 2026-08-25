import random
import smtplib
import os
import time
from email.message import EmailMessage
from datetime import datetime

EMAIL_USER = os.environ.get("EMAIL_USER")
EMAIL_PASS = os.environ.get("EMAIL_PASS")

def get_persistence(n):
    steps = 0
    while n >= 10:
        prod = 1
        for digit in str(n):
            prod *= int(digit)
        n = prod
        steps += 1
    return steps

def send_report(best_number, best_persistence, total_checked):
    msg = EmailMessage()
    date_str = datetime.now().strftime("%Y-%m-%d")
    
    body = (
        f"Daily Multiplicative Persistence Report - {date_str}\n"
        f"{'-'*40}\n"
        f"Numbers Checked: {total_checked:,}\n"
        f"Max Persistence Found: {best_persistence}\n"
        f"Winning Number: {best_number}\n"
    )
    msg.set_content(body)
    msg['Subject'] = f"Daily Report: Max Persistence {best_persistence}"
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(EMAIL_USER, EMAIL_PASS)
            server.send_message(msg)
        print("Daily report emailed successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")

def search_and_report():
    valid_digits = "2346789"  # Skipping 0, 1, and 5 for optimization
    max_p = -1
    best_num = None
    total_checked = 0
    
    # Run for 5.5 hours (GitHub shuts down free jobs at 6 hours)
    run_duration = 5.5 * 60 * 60 
    start_time = time.time()
    
    print("Starting daily hunt...")
    while time.time() - start_time < run_duration:
        # Generate random length between 20 and 100 digits
        length = random.randint(20, 100)
        digits = sorted([random.choice(valid_digits) for _ in range(length)])
        candidate = int("".join(digits))
        
        p = get_persistence(candidate)
        
        # Track the highest persistence seen
        if p > max_p:
            max_p = p
            best_num = candidate
            
        total_checked += 1

    print("Time limit reached. Sending daily report...")
    send_report(best_num, max_p, total_checked)

if __name__ == "__main__":
    search_and_report()
