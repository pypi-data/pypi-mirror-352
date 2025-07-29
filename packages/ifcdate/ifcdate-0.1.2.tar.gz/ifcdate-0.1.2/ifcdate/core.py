from datetime import datetime, timezone

def detect_date_format(date_string: str) -> str:
    """Detect date format based on common separators."""
    if "-" in date_string:
        return "%Y-%m-%d"
    elif "." in date_string:
        return "%d.%m.%Y"
    elif "/" in date_string:
        return "%m/%d/%Y"
    else:
        raise ValueError("Unknown date format")

def date_to_unix(date_string: str) -> tuple[int, str]:
    """Convert date string to Unix timestamp; return timestamp and detected format."""
    fmt = detect_date_format(date_string)
    dt = datetime.strptime(date_string, fmt)
    dt = dt.replace(tzinfo=timezone.utc)
    return int(dt.timestamp()), fmt

def is_leap_year(year: int) -> bool:
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def ifc_to_unix(input_date: str) -> int:
    """
    Convert an IFC date string (YYYY-MM-DD) to Unix timestamp (int).
    Validates IFC date format and translates IFC calendar back to Gregorian.
    """
    try:
        year_str, month_str, day_str = input_date.split("-")
        year = int(year_str)
        month = int(month_str)
        day = int(day_str)
    except Exception:
        raise ValueError("Invalid IFC date format")

    # Validate IFC month and day
    if month < 1 or month > 13:
        raise ValueError("Invalid IFC month")
    if day < 1:
        raise ValueError("Invalid IFC day")

    # Handle Year Day and Leap Day
    if month == 13:
        if day == 29:
            # Year Day - day after 364 days
            day_of_year = 365
        elif day == 30:
            # Leap Day (only in leap years)
            if not is_leap_year(year):
                raise ValueError("Leap Day in non-leap year")
            day_of_year = 366
        elif day > 28:
            raise ValueError("Invalid day in month 13")
        else:
            # Normal day in month 13 (1-28)
            day_of_year = (month - 1) * 28 + day
    else:
        if day > 28:
            raise ValueError("Invalid day for month <13")
        day_of_year = (month - 1) * 28 + day

    # Convert day_of_year to Gregorian date
    try:
        dt = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
    except Exception as e:
        raise ValueError(f"Invalid IFC date: {e}")

    return int(dt.timestamp())

def unix_to_ifc(unix_time: int, out_format: str = "%Y-%m-%d") -> str:
    dt = datetime.fromtimestamp(unix_time, timezone.utc)
    year = dt.year
    day_of_year = dt.timetuple().tm_yday  # 1-based day of year

    # IFC has 13 months of 28 days each (364 days), plus 1 or 2 extra days (Year Day and Leap Day)
    # Calculate IFC month and day:
    if is_leap_year(year):
        # Leap year with 366 days
        if day_of_year == 366:
            # Leap Day (extra day after last month)
            ifc_month = 13
            ifc_day = 30
        elif day_of_year == 365:
            # Year Day (extra day after 13th month)
            ifc_month = 13
            ifc_day = 29
        else:
            # Normal day within 13 months
            ifc_month = (day_of_year - 1) // 28 + 1
            ifc_day = (day_of_year - 1) % 28 + 1
    else:
        # Normal year with 365 days
        if day_of_year == 365:
            # Year Day
            ifc_month = 13
            ifc_day = 29
        else:
            ifc_month = (day_of_year - 1) // 28 + 1
            ifc_day = (day_of_year - 1) % 28 + 1

    # Format IFC date string according to requested output format
    if out_format == "%Y-%m-%d":
        return f"{year:04d}-{ifc_month:02d}-{ifc_day:02d}"
    elif out_format == "%d.%m.%Y":
        return f"{ifc_day:02d}.{ifc_month:02d}.{year:04d}"
    elif out_format == "%m/%d/%Y":
        return f"{ifc_month:02d}/{ifc_day:02d}/{year:04d}"
    else:
        return f"{year:04d}-{ifc_month:02d}-{ifc_day:02d}"

# Example usage inside your core (can also be moved to CLI or scripts)
if __name__ == "__main__":
    date_str = "01.01.1970"
    unix, input_fmt = date_to_unix(date_str)
    ifc_date = unix_to_ifc(unix, out_format=input_fmt)
    print(ifc_date)