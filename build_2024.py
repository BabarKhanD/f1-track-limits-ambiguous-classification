import fastf1
import pandas as pd
import os
import re
import time

os.makedirs(r'D:\f1-research\f1cache', exist_ok=True)
os.makedirs(r'D:\f1-research\data', exist_ok=True)
fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

YEAR = 2024
SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'SQ', 'S', 'R']
LABELS_FILE = rf'D:\f1-research\data\labels_{YEAR}.csv'
PROGRESS_FILE = rf'D:\f1-research\data\progress_{YEAR}.csv'

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        df = pd.read_csv(PROGRESS_FILE)
        return set(zip(df['race'], df['session']))
    return set()

def mark_done(race, sess_type):
    row = pd.DataFrame([{'race': race, 'session': sess_type}])
    header = not os.path.exists(PROGRESS_FILE)
    row.to_csv(PROGRESS_FILE, mode='a', header=header, index=False)

def save_rows(rows):
    if not rows:
        return
    df = pd.DataFrame(rows)
    header = not os.path.exists(LABELS_FILE)
    df.to_csv(LABELS_FILE, mode='a', header=header, index=False)

def load_with_retry(year, race, sess_type, max_retries=5):
    for attempt in range(max_retries):
        try:
            session = fastf1.get_session(year, race, sess_type)
            session.load(laps=True, telemetry=False, weather=False)
            return session
        except fastf1.exceptions.RateLimitExceededError:
            print(f"  Rate limit hit, waiting 5 minutes... (attempt {attempt+1})")
            time.sleep(300)
        except Exception as e:
            raise e
    raise Exception("Max retries exceeded")

done_set = load_progress()
print(f"Already completed for {YEAR}: {len(done_set)} race/session combos\n")

schedule = fastf1.get_event_schedule(YEAR)
race_names = [r for r in schedule['EventName'].tolist() if 'Pre-Season' not in r and 'Testing' not in r]

for race in race_names:
    for sess_type in SESSIONS:
        if (race, sess_type) in done_set:
            print(f"{race} [{sess_type}]: already done, skipping")
            continue

        try:
            session = load_with_retry(YEAR, race, sess_type)
            rows = []

            laps = session.laps
            deleted = laps[laps['Deleted'] == True]
            for _, row in deleted.iterrows():
                if 'TRACK LIMITS' in str(row['DeletedReason']).upper():
                    turn_match = re.search(r'TURN\s*(\d+)', str(row['DeletedReason']).upper())
                    turn = turn_match.group(1) if turn_match else ''
                    rows.append({
                        'year': YEAR, 'race': race, 'session': sess_type,
                        'driver': row['Driver'], 'lap': row['LapNumber'],
                        'lap_time': row['LapTime'], 'turn': turn,
                        'label': 'clear_violation', 'reason': row['DeletedReason']
                    })

            msgs = session.race_control_messages
            for _, row in msgs.iterrows():
                m = str(row['Message']).upper()
                if 'OFF TRACK AND CONTINUED' in m or 'NO INVESTIGATION NECESSARY' in m:
                    driver_match = re.search(r'\(([A-Z]{3})\)', m)
                    driver = driver_match.group(1) if driver_match else ''
                    turn_match = re.search(r'TURN\s*(\d+)', m)
                    turn = turn_match.group(1) if turn_match else ''
                    rows.append({
                        'year': YEAR, 'race': race, 'session': sess_type,
                        'driver': driver, 'lap': '', 'lap_time': '',
                        'turn': turn, 'label': 'no_advantage', 'reason': row['Message']
                    })

            save_rows(rows)
            mark_done(race, sess_type)
            print(f"{race} [{sess_type}]: done, {len(deleted)} deletions, {len(rows)} rows saved")
            time.sleep(2)

        except Exception as e:
            print(f"{race} [{sess_type}]: FAILED (not marked done, will retry next run) - {e}")

print(f"\n{YEAR} COMPLETE")