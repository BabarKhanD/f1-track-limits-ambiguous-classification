import fastf1
import pandas as pd
import os
import re

os.makedirs(r'D:\f1-research\f1cache', exist_ok=True)
fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

YEAR = 2019
SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'SQ', 'S', 'R']

schedule = fastf1.get_event_schedule(YEAR)
race_names = schedule['EventName'].tolist()

all_rows = []

for race in race_names:
    for sess_type in SESSIONS:
        try:
            session = fastf1.get_session(YEAR, race, sess_type)
            session.load(laps=True, telemetry=False, weather=False)

            laps = session.laps
            deleted = laps[laps['Deleted'] == True]
            for _, row in deleted.iterrows():
                if 'TRACK LIMITS' in str(row['DeletedReason']).upper():
                    turn_match = re.search(r'TURN\s*(\d+)', str(row['DeletedReason']).upper())
                    turn = turn_match.group(1) if turn_match else ''
                    all_rows.append({
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
                    all_rows.append({
                        'year': YEAR, 'race': race, 'session': sess_type,
                        'driver': driver, 'lap': '', 'lap_time': '',
                        'turn': turn, 'label': 'no_advantage', 'reason': row['Message']
                    })

            print(f"{race} [{sess_type}]: done, {len(deleted)} deletions")

        except Exception as e:
            print(f"{race} [{sess_type}]: skipped - {e}")

df = pd.DataFrame(all_rows)
df.to_csv(r'D:\f1-research\data\labels_2019.csv', index=False)
print(f"\nTotal rows: {len(df)}")
print("Saved to data/labels_2019.csv")