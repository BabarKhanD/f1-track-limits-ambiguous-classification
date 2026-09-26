import fastf1
import pandas as pd

fastf1.Cache.enable_cache(r'D:\f1-research\f1cache')

df = pd.read_csv(r'D:\f1-research\data\labels_final.csv')
no_adv = df[df['label'] == 'no_advantage']
row = no_adv.iloc[0]

print("CSV row values:")
print("year:", row['year'], "race:", row['race'], "session:", row['session'])
print("driver:", repr(row['driver']))
print("reason:", repr(row['reason']))

session = fastf1.get_session(row['year'], row['race'], row['session'])
session.load(laps=True, telemetry=False, weather=False)

msgs = session.race_control_messages
print("\nFirst 5 actual messages from session (repr to see exact formatting):")
for m in msgs['Message'].head(5):
    print(repr(m))

print("\nDoes any message contain the driver code?")
print(msgs[msgs['Message'].str.contains(str(row['driver']), na=False)][['Time','Message']])