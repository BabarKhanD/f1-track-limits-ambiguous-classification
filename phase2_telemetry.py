import fastf1
import pandas as pd
import os
import time

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

df = pd.read_csv(r'D:\f1-research\data\dataset_phase1_complete.csv')

OUT_FILE = r'D:\f1-research\data\telemetry_features.csv'
PROGRESS_FILE = r'D:\f1-research\data\phase2_progress.csv'

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
            session.load(laps=True, telemetry=True, weather=False)
            return session
        except fastf1.exceptions.RateLimitExceededError:
            print(f"  Rate limit hit, waiting 5 minutes...")
            time.sleep(300)
        except Exception as e:
            raise e
    raise Exception("Max retries exceeded")

done_set = load_progress()
print(f"Already done: {len(done_set)} sessions\n")

grouped = df.groupby(['year', 'race', 'session'])
success = 0
fail = 0

for (year, race, sess_type), group in grouped:
    if (year, race, sess_type) in done_set:
        continue
    try:
        session = load_with_retry(year, race, sess_type)
        laps = session.laps
        rows = []

        for idx, row in group.iterrows():
            try:
                driver = row['driver']
                lap_num = row['lap']
                lap = laps.pick_drivers(driver).pick_laps(int(lap_num))
                if lap.empty:
                    fail += 1
                    continue
                lap = lap.iloc[0]
                tel = lap.get_telemetry()
                if tel.empty:
                    fail += 1
                    continue

                rows.append({
                    'year': row['year'], 'race': row['race'], 'session': row['session'],
                    'driver': driver, 'lap': lap_num, 'turn': row['turn'],
                    'label': row['label'],
                    'max_speed': tel['Speed'].max(),
                    'min_speed': tel['Speed'].min(),
                    'avg_speed': tel['Speed'].mean(),
                    'max_throttle': tel['Throttle'].max(),
                    'avg_brake': tel['Brake'].mean(),
                    'brake_points': int((tel['Brake'] == True).sum()) if tel['Brake'].dtype == bool else int((tel['Brake'] > 0).sum()),
                    'num_points': len(tel),
                })
                success += 1
            except Exception as e:
                fail += 1
                continue

        save_rows(rows)
        mark_done(year, race, sess_type)
        print(f"{year} {race} [{sess_type}]: {len(rows)} rows extracted")
        time.sleep(1)

    except Exception as e:
        print(f"{year} {race} [{sess_type}]: SESSION FAILED (retry next run) - {e}")

print(f"\nSuccess: {success} / Fail: {fail}")