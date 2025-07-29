# tests/test_core.py

import pytest
from ifcdate.core import unix_to_ifc, ifc_to_unix, date_to_unix, is_leap_year
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
    unix = date_to_unix(gregorian)
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
