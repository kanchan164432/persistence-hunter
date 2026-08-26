# Multiplicative Persistence Hunter

An automated, background mathematical search engine built in Python to hunt for numbers with a **multiplicative persistence of 12 or greater** in base 10. The project runs on a daily schedule using GitHub Actions, saves its progress state to resume seamlessly across runs, and sends daily status reports and jackpot alerts via email.

---

## Key Features

* **Optimized Search Loop:** Evaluates candidates in sorted lexicographical order, ignoring redundant permutations and unviable digits (`0`, `1`, and `5`).
* **State Persistence:** Stores the last evaluated candidate in `state.json` and commits it back to the repository so each run resumes precisely where the previous one stopped.
* **Automated Daily Runs:** Uses GitHub Actions to execute a 5.5-hour search shift every 24 hours at 12:00 UTC.
* **Automated Email Reports:** Sends a summary email at the end of each run via Gmail SMTP detailing total numbers checked, maximum persistence found, and the winning candidate.
* **Jackpot Logging:** Automatically logs any discovery of persistence $\ge 12$ into a dedicated `jackpots.json` file.

---

## Project Structure

```text
.
├── .github/
│   └── workflows/
│       └── daily_run.yml     # GitHub Actions schedule and environment setup
├── main.py                   # Core calculation, state management, and email logic
├── state.json                # Tracks last candidate evaluated across runs
├── daily_history.json        # Log of daily summaries and top candidates
└── jackpots.json             # Dedicated log for numbers with persistence >= 12

```

---

## Prerequisites & Setup

### 1. Gmail App Password

To allow the Python script to send email notifications securely:

1. Enable **2-Step Verification** on your Google Account.
2. Navigate to **Google Account Settings** $\rightarrow$ **Security** $\rightarrow$ search for **App Passwords**.
3. Generate a new password (e.g., named "Persistence Hunter") and copy the 16-character string.

### 2. GitHub Secrets Configuration

In your GitHub repository:

1. Go to **Settings** $\rightarrow$ **Secrets and variables** $\rightarrow$ **Actions**.
2. Add the following repository secrets:
* `EMAIL_USER`: Your complete Gmail address.
* `EMAIL_PASS`: The 16-character Gmail App Password generated above.



### 3. Repository Permissions

To allow the workflow bot to update `state.json` and logs:

1. Go to **Settings** $\rightarrow$ **Actions** $\rightarrow$ **General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Click **Save**.

---

## How It Works

1. **Initialization:** `main.py` checks for `state.json`. If missing, it starts at `"22222222222222222222"` (20 digits of `2`).
2. **Execution:** The script runs for 5.5 hours, sequentially incrementing candidate digits using valid characters (`2, 3, 4, 6, 7, 8, 9`).
3. **Logging & Storage:**
* Updates daily stats in `daily_history.json`.
* Appends candidates with persistence $\ge 12$ to `jackpots.json`.
* Updates `state.json` with the current position.


4. **Notification & Commit:** Sends a summary email, and GitHub Actions commits all updated `.json` files back to the repository.

---

## Local Testing

To run a quick local check:

1. Set your environment variables:
```bash
export EMAIL_USER="your-email@gmail.com"
export EMAIL_PASS="your-app-password"

```


2. Run the script manually:
```bash
python main.py

```
