# ifcdate/core.py
from datetime import datetime, timezone, UTC

def is_leap_year(year):
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def unix_to_ifc(unix_time: int) -> str:
    dt = datetime.fromtimestamp(unix_time, timezone.utc)
    year = dt.year

    start_of_year = datetime(year, 1, 1, tzinfo=timezone.utc)
    day_of_year = (dt - start_of_year).days + 1  # +1 because Jan 1 = day 1

    # Adjust for leap year day and year day:
    is_leap = is_leap_year(year)

    if day_of_year == 365 and not is_leap:
        # Year Day
        month = 13
        day = 29
    elif is_leap and day_of_year == 366:
        # Leap Day
        month = 13
        day = 30
    else:
        # Regular days in months
        # Adjust day_of_year if after Year Day or Leap Day
        if is_leap and day_of_year > 365:
            day_of_year -= 1
        elif not is_leap and day_of_year > 364:
            day_of_year -= 1

        month = (day_of_year - 1) // 28 + 1
        day = ((day_of_year - 1) % 28) + 1

    return f"{year}-{month:02d}-{day:02d}"

def ifc_to_unix(ifc_string):
    try:
        parts = list(map(int, ifc_string.strip().split("-")))
        if len(parts) != 3:
            raise ValueError("IFC date must be YYYY-MM-DD")
        year, month, day = parts
        leap = is_leap_year(year)
        if month == 13 and day in (29, 30) and (day == 30 and not leap):
            if day == 30:
                raise ValueError("Leap Day only exists in leap years")
        elif month < 1 or month > 13 or day < 1 or (month < 13 and day > 28) or day > 30:
            raise ValueError("Invalid IFC date")

        day_of_year = (month - 1) * 28 + (day - 1)
        start_of_year = datetime(year, 1, 1, tzinfo=UTC)
        return int((start_of_year + timedelta(days=day_of_year)).timestamp())
    except Exception as e:
        raise ValueError(f"Invalid IFC date: {e}")

def date_to_unix(date_string):
    dt = datetime.strptime(date_string, "%Y-%m-%d")
    return int(dt.replace(tzinfo=UTC).timestamp())
