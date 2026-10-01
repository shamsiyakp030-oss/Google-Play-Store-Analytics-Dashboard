from datetime import datetime
import pytz



def check_time(start_hour, end_hour):

    india = pytz.timezone(
        "Asia/Kolkata"
    )

    current_time = datetime.now(
        india
    )

    hour = current_time.hour


    if start_hour <= hour < end_hour:
        return True

    return False