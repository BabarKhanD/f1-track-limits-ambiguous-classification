import fastf1
import pandas as pd
import os
import re

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

YEARS = [2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
SESSIONS = ['FP1', 'FP2', 'FP3', 'Q', 'SQ', 'S', 'R']

TRACK_LIMIT_PHRASES = [
    'OFF TRACK AND CONTINUED',
    'NO INVESTIGATION NECESSARY',
]

def is_dismissed_track_limit(m):
    if 'NO FURTHER ACTION' in m and ('TRACK LIMIT' in m or 'OFF TRACK' in m or 'OFF THE TRACK' in m):
        return True
    for phrase in TRACK_LIMIT_PHRASES:
        if phrase in m:
            return True
    return False

all_rows = []

for YEAR in YEARS:
    schedule = fastf1.get_event_schedule(YEAR)
    race_names = [r for r in schedule['EventName'].tolist() if 'Pre-Season' not in r and 'Testing' not in r]

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
                    if is_dismissed_track_limit(m):
                        driver_match = re.search(r'\(([A-Z]{3})\)', m)
                        driver = driver_match.group(1) if driver_match else ''
                        turn_match = re.search(r'TURN\s*(\d+)', m)
                        turn = turn_match.group(1) if turn_match else ''
                        all_rows.append({
                            'year': YEAR, 'race': race, 'session': sess_type,
                            'driver': driver, 'lap': '', 'lap_time': '',
                            'turn': turn, 'label': 'no_advantage', 'reason': row['Message']
                        })

                print(f"{YEAR} {race} [{sess_type}]: ok")

            except Exception as e:
                print(f"{YEAR} {race} [{sess_type}]: skipped - {e}")

df = pd.DataFrame(all_rows)
df.to_csv(r'D:\f1-research\data\labels_relabeled.csv', index=False)
print(f"\nTOTAL: {len(df)} rows")
print(df['label'].value_counts())
print("\nBy year:")
print(df.groupby(['year', 'label']).size())