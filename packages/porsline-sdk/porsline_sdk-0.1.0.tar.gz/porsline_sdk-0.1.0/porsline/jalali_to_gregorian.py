import jdatetime
from datetime import datetime

def jconvert(jalali_str: str) -> datetime:
    """
    Converts Jalali date string like '1404/02/28-10: 32: 16' to a Gregorian datetime object.
    """
    cleaned = jalali_str.replace(' ', '')  # e.g., '1404/02/28-10:32:16'
    try:
        date_part, time_part = cleaned.split('-')
        year, month, day = map(int, date_part.split('/'))
        hour, minute, second = map(int, time_part.split(':'))
        jalali_dt = jdatetime.datetime(year, month, day, hour, minute, second)
        return jalali_dt.togregorian().isoformat()
    except Exception as e:
        raise ValueError(f"Invalid Jalali datetime format: {jalali_str}") from e
