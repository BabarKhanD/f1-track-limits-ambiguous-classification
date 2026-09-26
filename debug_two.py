import fastf1
import pandas as pd

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

session = fastf1.get_session(2018, 'Bahrain Grand Prix', 'FP2')
session.load(laps=True, telemetry=False, weather=False)

reason_text = 'CAR 44 (HAM) OFF TRACK AND CONTINUED AT TURN 1'
driver = 'HAM'

msgs = session.race_control_messages
match = msgs[msgs['Message'].astype(str) == reason_text]
print("Exact match found:", not match.empty)
print(match)

if not match.empty:
    msg_time = match.iloc[0]['Time']
    print("\nmsg_time:", msg_time, type(msg_time))

    laps = session.laps
    print("\nLaps columns:", laps.columns.tolist())

    driver_laps = laps.pick_drivers(driver)
    print("\nDriver laps found:", len(driver_laps))
    print(driver_laps[['LapNumber', 'LapStartDate']].head(10))