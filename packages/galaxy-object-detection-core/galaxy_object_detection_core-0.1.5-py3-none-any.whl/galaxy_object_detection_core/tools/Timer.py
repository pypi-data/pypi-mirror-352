from datetime import datetime
import pytz

# ----------------- TIMER -----------------
class Timer:
    @staticmethod
    def get_jakarta_time_current():
        jakarta_tz = pytz.timezone("Asia/Jakarta")
        return datetime.now(jakarta_tz).strftime("%Y-%m-%d %H-%M-%S")
