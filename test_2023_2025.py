import fastf1
import os
import time

os.makedirs(r'D:\f1-research\f1cache', exist_ok=True)
fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

YEARS = [2023, 2024, 2025]
RACES_TO_TEST = 4

results = {}

for YEAR in YEARS:
    schedule = fastf1.get_event_schedule(YEAR)
    race_names = schedule['EventName'].tolist()[:RACES_TO_TEST]

    year_results = []
    passed_any = False
    for race in race_names:
        try:
            session = fastf1.get_session(YEAR, race, 'R')
            session.load(laps=True, telemetry=False, weather=False)
            _ = session.laps
            _ = session.race_control_messages
            year_results.append((race, 'PASS'))
            passed_any = True
            print(f"{YEAR} {race}: PASS")
        except Exception as e:
            year_results.append((race, f'FAIL - {e}'))
            print(f"{YEAR} {race}: FAIL - {e}")
        time.sleep(2)

    results[YEAR] = year_results
    passes = sum(1 for r in year_results if r[1] == 'PASS')
    print(f"\n{YEAR}: {passes}/{RACES_TO_TEST} passed\n")

print("\n========== FINAL PROGRESS REPORT ==========")
for YEAR, year_results in results.items():
    passes = sum(1 for r in year_results if r[1] == 'PASS')
    print(f"{YEAR}: {passes}/{RACES_TO_TEST} passed")
    for race, status in year_results:
        print(f"   {race}: {status}")