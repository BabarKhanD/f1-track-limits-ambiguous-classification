import fastf1

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

session = fastf1.get_session(2025, 'Australian Grand Prix', 'R')
session.load(laps=True, telemetry=False, weather=False)

msgs = session.race_control_messages[['Time', 'Message']]
for _, row in msgs.iterrows():
    print(row['Message'])