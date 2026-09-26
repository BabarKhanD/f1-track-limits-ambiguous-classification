import fastf1
import os

os.makedirs(r'D:\f1-research\f1cache', exist_ok=True)
fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

session = fastf1.get_session(2021, 'Abu Dhabi', 'R')
session.load(laps=True, telemetry=False, weather=False)

result = session.laps[['Driver', 'LapNumber', 'LapTime', 'Deleted', 'DeletedReason']]
result.to_csv(r'D:\f1-research\results\test_output.csv', index=False)
print(result.head())
print("Saved to results folder")