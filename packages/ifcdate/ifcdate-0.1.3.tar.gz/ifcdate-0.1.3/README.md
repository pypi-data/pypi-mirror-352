# UnixToIFCTime

A Python script to convert Unix timestamps to the International Fixed Calendar (IFC) format and vice versa.

**Note:** This implementation deviates from the original IFC proposal by adding leap year days (Year Day and Leap Day) to the end of the year, rather than placing them within the calendar as originally suggested.

## Features

- Converts Unix timestamps to IFC dates.
- Accepts date input in `YYYY-MM-DD` format and outputs the corresponding IFC date.
- Supports leap years and special days (Leap Day, Year Day).

## Usage

```bash
python unixToIfcTime.py [-d DATE] [-u UNIXTIME]