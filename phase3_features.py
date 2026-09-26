import fastf1
import pandas as pd
import os
import time

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

df = pd.read_csv(r'D:\f1-research\data\telemetry_features_clean.csv')

OUT_FILE = r'D:\f1-research\data\phase3_features.csv'
PROGRESS_FILE = r'D:\f1-research\data\phase3_progress.csv'

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        pdf = pd.read_csv(PROGRESS_FILE)
        return set(zip(pdf['year'], pdf['race'], pdf['session']))
    return set()

def mark_done(year, race, sess_type):
    row = pd.DataFrame([{'year': year, 'race': race, 'session': sess_type}])
    header = not os.path.exists(PROGRESS_FILE)
    row.to_csv(PROGRESS_FILE, mode='a', header=header, index=False)

def save_rows(rows):
    if not rows:
        return
    rdf = pd.DataFrame(rows)
    header = not os.path.exists(OUT_FILE)
    rdf.to_csv(OUT_FILE, mode='a', header=header, index=False)

def load_with_retry(year, race, sess_type, max_retries=5):
    for attempt in range(max_retries):
        try:
            session = fastf1.get_session(year, race, sess_type)
            session.load(laps=True, telemetry=False, weather=False)
            return session
        except fastf1.exceptions.RateLimitExceededError:
            print("  Rate limit hit, waiting 5 minutes...")
            time.sleep(300)
        except Exception as e:
            raise e
    raise Exception("Max retries exceeded")

done_set = load_progress()
print(f"Already done: {len(done_set)} sessions\n")

grouped = df.groupby(['year', 'race', 'session'])

for (year, race, sess_type), group in grouped:
    if (year, race, sess_type) in done_set:
        continue
    try:
        session = load_with_retry(year, race, sess_type)
        laps = session.laps
        session_avg_speed = laps['SpeedFL'].dropna().mean()
        session_max_speed = laps['SpeedFL'].dropna().max()

        rows = []
        for idx, row in group.iterrows():
            r = row.to_dict()
            r['session_avg_speed'] = session_avg_speed
            r['session_max_speed'] = session_max_speed
            r['speed_ratio'] = row['max_speed'] / session_max_speed if session_max_speed else None
            r['avg_speed_ratio'] = row['avg_speed'] / session_avg_speed if session_avg_speed else None
            r['is_sprint'] = 1 if sess_type == 'S' else 0
            r['is_qualifying'] = 1 if sess_type in ('Q', 'SQ') else 0
            r['is_race'] = 1 if sess_type == 'R' else 0
            r['is_practice'] = 1 if sess_type in ('FP1', 'FP2', 'FP3') else 0
            r['post_2022_regs'] = 1 if int(year) >= 2022 else 0
            rows.append(r)

        save_rows(rows)
        mark_done(year, race, sess_type)
        print(f"{year} {race} [{sess_type}]: {len(rows)} rows")
        time.sleep(1)

    except Exception as e:
        print(f"{year} {race} [{sess_type}]: FAILED (retry next run) - {e}")

print("\nDONE")