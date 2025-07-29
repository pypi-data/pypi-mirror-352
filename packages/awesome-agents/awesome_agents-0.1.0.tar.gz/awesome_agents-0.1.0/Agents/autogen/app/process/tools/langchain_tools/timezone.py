from zoneinfo import ZoneInfo
from datetime import datetime

dt = datetime.now(ZoneInfo("America/New_York"))
print(dt)