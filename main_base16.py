import time
import json
import os

STATE_FILE = "state_prime16.json"

# Set past recorded history limit for Base 16 (E = 200)
DEFAULT_START_E = 201
CHUNK_SIZE = 20  # Exponent levels per run

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

def get_persistence_b16(n):
    steps = 0
    while n >= 16:
        prod = 1
        temp = n
        while temp > 0:
            temp, digit = divmod(temp, 16)
            prod *= digit
        n = prod
        steps += 1
    return steps

def search_base16_beyond_history():
    start_E = load_start_exponent()
    end_E = start_E + CHUNK_SIZE
    max_p = -1
    total_evaluated = 0
    
    print(f"Resuming Base 16 search BEYOND history from Exponent Sum E = {start_E} to {end_E}...")
    run_duration = 4.5 * 60 * 60
    start_time = time.time()

    for E in range(start_E, end_E + 1):
        if time.time() - start_time > run_duration:
            print(f"Time limit reached. Saving state at E = {E}...")
            save_state(E)
            return

        for a in range(E + 1):
            if a >= 4:  # Eliminates products divisible by 16 (hexadecimal zero)
                continue
            for b in range(E + 1 - a):
                for c in range(E + 1 - a - b):
                    for d in range(E + 1 - a - b - c):
                        for e in range(E + 1 - a - b - c - d):
                            f = E - a - b - c - d - e
                            
                            P1 = (2**a) * (3**b) * (5**c) * (7**d) * (11**e) * (13**f)
                            p = 1 + get_persistence_b16(P1)
                            total_evaluated += 1

                            if p > max_p:
                                max_p = p
                                print(f"NEW BASE 16 HIGH: Persistence {max_p} at E={E}")
                                
                            if p >= 9:
                                print(f"🚨 WORLD RECORD! Base 16 Persistence {p} found!")

    save_state(end_E + 1)
    print(f"Finished chunk. Next run starts at E = {end_E + 1}")

if __name__ == "__main__":
    search_base16_beyond_history()
