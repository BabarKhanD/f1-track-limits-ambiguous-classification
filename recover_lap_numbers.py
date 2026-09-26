import fastf1
import pandas as pd
import os
import time

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

df = pd.read_csv(r'D:\f1-research\data\labels_final.csv')
no_adv = df[df['label'] == 'no_advantage'].copy().reset_index(drop=True)

OUT_FILE = r'D:\f1-research\data\no_advantage_with_laps.csv'
PROGRESS_FILE = r'D:\f1-research\data\recover_progress.csv'

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
            print(f"  Rate limit hit, waiting 5 minutes... (attempt {attempt+1})")
            time.sleep(300)
        except Exception as e:
            raise e
    raise Exception("Max retries exceeded")

done_set = load_progress()
print(f"Already done: {len(done_set)} sessions\n")

grouped = no_adv.groupby(['year', 'race', 'session'])
recovered = 0
failed = 0

for (year, race, sess_type), group in grouped:
    if (year, race, sess_type) in done_set:
        continue
    try:
        session = load_with_retry(year, race, sess_type)
        t0 = session.t0_date
        msgs = session.race_control_messages
        laps = session.laps

        rows = []
        for idx, row in group.iterrows():
            driver = row['driver']
            reason_text = str(row['reason'])

            match = msgs[msgs['Message'].astype(str) == reason_text]
            if match.empty or not driver:
                failed += 1
                rows.append({**row.to_dict(), 'lap': None})
                continue

            msg_time_rel = match.iloc[0]['Time'] - t0
            driver_laps = laps.pick_drivers(driver)
            candidate = driver_laps[driver_laps['Time'] <= msg_time_rel].sort_values('Time').tail(1)

            if not candidate.empty:
                rows.append({**row.to_dict(), 'lap': candidate.iloc[0]['LapNumber']})
                recovered += 1
            else:
                rows.append({**row.to_dict(), 'lap': None})
                failed += 1

        save_rows(rows)
        mark_done(year, race, sess_type)
        print(f"{year} {race} [{sess_type}]: done ({len(rows)} rows)")
        time.sleep(1)

    except Exception as e:
        print(f"{year} {race} [{sess_type}]: FAILED (retry next run) - {e}")

print(f"\nRecovered: {recovered} / Failed: {failed}")