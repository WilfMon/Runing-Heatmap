import datetime
from garminconnect import Garmin

with open("Data/scripts/creds.txt", "r", encoding="utf-8") as file:
    creds = (file.read()).split("\n")
    
print(creds)
today = datetime.date.today().isoformat()

try:
    print("Trying to login to Garmin Connect...")
    api = Garmin(creds[0], creds[1])
    api.login()
except Exception as e:
    print(f"Authentication failed: {e}")
    exit()
    
try:
    start_date = "2026-01-01"
    end_date = today
    activities = api.get_activities_by_date(start_date, end_date)
    
    print(f"\n--- Found {len(activities)} activities ---")
    for act in activities:
        print(f"ID: {act['activityId']} | Name: {act['activityName']} | Type: {act['activityType']['typeKey']}")
        
        activity_id = act['activityId']
        
        fit_data = api.download_activity(activity_id, dl_fmt=api.ActivityDownloadFormat.ORIGINAL)
        
        with open(f"Data/zipped/{activity_id}.zip", "wb") as f:
            f.write(fit_data)
        
except Exception as e:
    print(f"Could not fetch activities: {e}")