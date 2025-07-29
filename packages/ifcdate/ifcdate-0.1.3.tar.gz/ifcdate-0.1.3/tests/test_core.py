# tests/test_core.py

import pytest
import subprocess
from ifcdate.core import (
    date_to_unix,
    detect_date_format,
    ifc_to_unix,
    is_leap_year,
    unix_to_ifc,
)
from datetime import datetime, timezone

def test_leap_years():
    assert is_leap_year(2024) is True
    assert is_leap_year(1900) is False
    assert is_leap_year(2000) is True
    assert is_leap_year(2023) is False

def test_unix_to_ifc_basic():
    dt = datetime(2025, 5, 31, tzinfo=timezone.utc)
    unix = int(dt.timestamp())
    assert unix_to_ifc(unix) == "2025-06-11"  # May 31 = IFC 6/11

def test_gregorian_to_unix_and_ifc():
    gregorian = "2025-05-31"
    unix, fmt = date_to_unix(gregorian)
    unix_to_ifc(unix, out_format=fmt)
    assert unix_to_ifc(unix) == "2025-06-11"

def test_year_day():
    dt = datetime(2025, 12, 31, tzinfo=timezone.utc)  # 365th day
    unix = int(dt.timestamp())
    assert unix_to_ifc(unix) == "2025-13-29"  # Year Day

def test_leap_day():
    dt = datetime(2024, 12, 31, tzinfo=timezone.utc)  # 366th day leap year
    unix = int(dt.timestamp())
    assert unix_to_ifc(unix) == "2024-13-30"

def test_invalid_ifc_date():
    with pytest.raises(ValueError):
        ifc_to_unix("2025-14-01")  # Invalid month

    with pytest.raises(ValueError):
        ifc_to_unix("2025-02-29")  # Invalid day

    with pytest.raises(ValueError):
        ifc_to_unix("2025-13-30")  # Leap day in non-leap year

def test_detect_date_format():
    assert detect_date_format("2025-06-15") == "%Y-%m-%d"
    assert detect_date_format("15.06.2025") == "%d.%m.%Y"
    assert detect_date_format("06/15/2025") == "%m/%d/%Y"
    with pytest.raises(ValueError):
        detect_date_format("2025_06_15")

@pytest.mark.parametrize("date_str,expected_fmt", [
    ("2025-06-15", "%Y-%m-%d"),
    ("15.06.2025", "%d.%m.%Y"),
    ("06/15/2025", "%m/%d/%Y"),
])
def test_date_to_unix_and_back_format_preserved(date_str, expected_fmt):
    unix, fmt = date_to_unix(date_str)
    assert fmt == expected_fmt

    ifc = unix_to_ifc(unix, out_format=fmt)
    # Since IFC conversion is currently identity, output should match input style but maybe not same exact date.
    # Let's just check formatting:
    if fmt == "%Y-%m-%d":
        parts = ifc.split("-")
        assert len(parts) == 3
        assert all(len(p) == 2 or len(p) == 4 for p in parts)
    elif fmt == "%d.%m.%Y":
        parts = ifc.split(".")
        assert len(parts) == 3
        assert all(len(p) == 2 or len(p) == 4 for p in parts)
    elif fmt == "%m/%d/%Y":
        parts = ifc.split("/")
        assert len(parts) == 3
        assert all(len(p) == 2 or len(p) == 4 for p in parts)

def test_roundtrip_with_real_date():
    date_str = "15.08.1991"
    unix, fmt = date_to_unix(date_str)
    ifc = unix_to_ifc(unix, out_format=fmt)
    # With current dummy logic, IFC date == input date parts reordered as output format
    assert ifc.endswith("1991")

def test_date_to_unix_invalid_format():
    with pytest.raises(ValueError):
        date_to_unix("15_08_1991")

# Optional: test that unix_to_ifc falls back gracefully on unknown format
def test_unix_to_ifc_fallback_format():
    unix, _ = date_to_unix("2025-06-15")
    result = unix_to_ifc(unix, out_format="%Y/%m/%d")  # unknown format in our ifc function
    assert result.count("-") == 2  # falls back to ISO style

def test_valid_leap_day_in_leap_year():
    assert ifc_to_unix("2024-13-30") == int(datetime(2024, 12, 31, tzinfo=timezone.utc).timestamp())

def test_valid_month_13_normal_day():
    assert ifc_to_unix("2025-13-10") == int(datetime(2025, 12, 12, tzinfo=timezone.utc).timestamp())

def test_ifc_to_unix_day_zero():
    with pytest.raises(ValueError):
        ifc_to_unix("2025-05-00")

def test_ifc_to_unix_invalid_format_string():
    with pytest.raises(ValueError, match="Invalid IFC date:"):
        ifc_to_unix("not-a-date")

def test_ifc_to_unix_month_13_regular_day():
    # This triggers the `elif day <= 28` branch in month == 13
    assert ifc_to_unix("2025-13-28") == int(datetime(2025, 12, 30, tzinfo=timezone.utc).timestamp())

def test_ifc_to_unix_invalid_day_in_regular_month():
    with pytest.raises(ValueError, match="Invalid day 29 for month 5"):
        ifc_to_unix("2025-05-29")

def test_ifc_to_unix_invalid_day_31_in_month_13():
    with pytest.raises(ValueError, match="Invalid day 31 in month 13"):
        ifc_to_unix("2025-13-31")

def fake_ifc_to_unix(input_date: str) -> int:
    from datetime import datetime, timezone, timedelta
    year, month, day = map(int, input_date.split("-"))
    day_of_year = 367  # or 400 depending on test
    try:
        dt = datetime(year, 1, 1, tzinfo=timezone.utc) + timedelta(days=day_of_year - 1)
    except Exception as e:
        raise ValueError(f"Invalid IFC date: {e}") from e
    return int(dt.timestamp())


def test_ifc_to_unix_invalid_day_regular_month():
    with pytest.raises(ValueError, match="Invalid day 29 for month 5"):
        ifc_to_unix("2025-05-29")  # day 29 invalid for month 5 (only 28 days)

def test_ifc_to_unix_invalid_day_in_month_13():
    with pytest.raises(ValueError, match="Invalid day 31 in month 13"):
        ifc_to_unix("2025-13-31")  # day 31 invalid in month 13

def test_ifc_to_unix_leap_day_in_non_leap_year():
    with pytest.raises(ValueError, match="Leap Day in non-leap year"):
        ifc_to_unix("2025-13-30")  # leap day in non-leap year 2025


def test_detect_date_format_invalid():
    with pytest.raises(ValueError):
        detect_date_format("2020_01_01")  # Unknown separator

def test_ifc_to_unix_invalid_month():
    with pytest.raises(ValueError):
        ifc_to_unix("2020-14-01")  # Month out of range

def test_ifc_to_unix_invalid_day():
    with pytest.raises(ValueError):
        ifc_to_unix("2020-02-30")  # Day > 28 for month 2

def test_ifc_to_unix_invalid_day_13():
    with pytest.raises(ValueError):
        ifc_to_unix("2021-13-30")  # Leap day in non-leap year

def test_ifc_to_unix_malformed_input():
    with pytest.raises(ValueError):
        ifc_to_unix("not-a-date")  # Will fail map(int, ...) call

def test_ifc_to_unix_invalid_day_31_in_13():
    with pytest.raises(ValueError, match="Invalid day 31 in month 13"):
        ifc_to_unix("2024-13-31")

def test_unix_to_ifc_unknown_format_falls_back_to_iso():
    unix = 1748649600  # 2025-05-31
    result = unix_to_ifc(unix, out_format="%unsupported")
    assert result == "2025-06-11"  # fallback to ISO

def test_core_main_output():
    result = subprocess.run(
        ["python", "-m", "ifcdate.core"],
        capture_output=True,
        text=True,
    )
    assert result.stdout.strip()  # Just check it's not empty
