import fastf1
import pandas as pd

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

session = fastf1.get_session(2018, 'Bahrain Grand Prix', 'FP2')
session.load(laps=True, telemetry=True, weather=True)

reason_text = 'CAR 44 (HAM) OFF TRACK AND CONTINUED AT TURN 1'
driver = 'HAM'

msgs = session.race_control_messages
match = msgs[msgs['Message'].astype(str) == reason_text]
msg_time_abs = match.iloc[0]['Time']

print("t0_date:", session.t0_date, type(session.t0_date))
print("msg_time_abs:", msg_time_abs, type(msg_time_abs))

msg_time_rel = msg_time_abs - session.t0_date
print("msg_time_rel:", msg_time_rel, type(msg_time_rel))

laps = session.laps
driver_laps = laps.pick_drivers(driver)
print("\nDriver laps 'Time' column (first 10):")
print(driver_laps[['LapNumber', 'Time']].head(10))

print("\nComparison test:")
print(driver_laps['Time'] <= msg_time_rel)