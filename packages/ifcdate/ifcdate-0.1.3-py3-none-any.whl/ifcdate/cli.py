# ifcdate/cli.py
import argparse
import time
from datetime import datetime, UTC
from .core import unix_to_ifc, ifc_to_unix, date_to_unix

def print_fancy(unix_time):
    dt = datetime.fromtimestamp(unix_time, UTC)
    ifc = unix_to_ifc(unix_time)
    print("="*40)
    print(f"Gregorian Date : {dt.strftime('%Y-%m-%d %H:%M:%S UTC')}")
    print(f"Unix Timestamp : {unix_time}")
    print(f"IFC Date       : {ifc}")
    print("="*40)

def main():
    parser = argparse.ArgumentParser(
        description="Convert between Unix, Gregorian, and IFC dates.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument("-d", "--date", help="Gregorian date (YYYY-MM-DD)")
    parser.add_argument("-u", "--unix", type=int, help="Unix timestamp")
    parser.add_argument("-i", "--ifc", help="IFC date (YYYY-MM-DD)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose output")
    args = parser.parse_args()

    try:
        if args.date:
            unix_time, _ = date_to_unix(args.date)
            print(f"DEBUG: args.unix = {args.unix}")
            print_fancy(unix_time) if args.verbose else print(unix_to_ifc(unix_time))
        elif args.unix is not None:
            print_fancy(args.unix) if args.verbose else print(unix_to_ifc(args.unix))
        elif args.ifc:
            unix_time = ifc_to_unix(args.ifc)
            print_fancy(unix_time) if args.verbose else print(args.ifc)
        else:
            unix_time = int(time.time())
            print_fancy(unix_time) if args.verbose else print(unix_to_ifc(unix_time))
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
