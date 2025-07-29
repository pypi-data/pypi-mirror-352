from datetime import datetime, timezone, timedelta

def detect_date_format(date_string: str) -> str:
    """Detect date format from common separators."""
    if "-" in date_string:
        return "%Y-%m-%d"
    if "." in date_string:
        return "%d.%m.%Y"
    if "/" in date_string:
        return "%m/%d/%Y"
    raise ValueError(f"Unknown date format: {date_string}")

def date_to_unix(date_string: str) -> tuple[int, str]:
    """Convert date string to Unix timestamp and return detected format."""
    fmt = detect_date_format(date_string)
    dt = datetime.strptime(date_string, fmt).replace(tzinfo=timezone.utc)
    return int(dt.timestamp()), fmt

def is_leap_year(year: int) -> bool:
    """Return True if year is leap year in Gregorian calendar."""
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)

def ifc_to_unix(input_date: str) -> int:
    try:
        year, month, day = map(int, input_date.split("-"))
    except Exception as e:
        raise ValueError(f"Invalid IFC date: {e}") from e

    if not (1 <= month <= 13):
        raise ValueError(f"Invalid IFC month: {month}")
    if day < 1:
        raise ValueError(f"Invalid IFC day: {day}")

    if month == 13:
        if day == 29:
            day_of_year = 365
        elif day == 30:
            if not is_leap_year(year):
                raise ValueError(f"Leap Day in non-leap year {year}")
            day_of_year = 366
        elif day <= 28:
            day_of_year = (month - 1) * 28 + day
        else:
            raise ValueError(f"Invalid day {day} in month 13")
    else:
        if day > 28:
            raise ValueError(f"Invalid day {day} for month {month}")
        day_of_year = (month - 1) * 28 + day

    dt = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
    return int(dt.timestamp())

def unix_to_ifc(unix_time: int, out_format: str = "%Y-%m-%d") -> str:
    """Convert Unix timestamp to IFC date string in requested format."""
    dt = datetime.fromtimestamp(unix_time, timezone.utc)
    year = dt.year
    day_of_year = dt.timetuple().tm_yday

    if is_leap_year(year):
        if day_of_year == 366:
            ifc_month, ifc_day = 13, 30  # Leap Day
        elif day_of_year == 365:
            ifc_month, ifc_day = 13, 29  # Year Day
        else:
            ifc_month = (day_of_year - 1) // 28 + 1
            ifc_day = (day_of_year - 1) % 28 + 1
    else:
        if day_of_year == 365:
            ifc_month, ifc_day = 13, 29  # Year Day
        else:
            ifc_month = (day_of_year - 1) // 28 + 1
            ifc_day = (day_of_year - 1) % 28 + 1

    formats = {
        "%Y-%m-%d": f"{year:04d}-{ifc_month:02d}-{ifc_day:02d}",
        "%d.%m.%Y": f"{ifc_day:02d}.{ifc_month:02d}.{year:04d}",
        "%m/%d/%Y": f"{ifc_month:02d}/{ifc_day:02d}/{year:04d}",
    }
    return formats.get(out_format, formats["%Y-%m-%d"])

if __name__ == "__main__":
    date_str = "01.01.1970"
    unix, fmt = date_to_unix(date_str)
    print(unix_to_ifc(unix, out_format=fmt))
