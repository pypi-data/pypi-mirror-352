import datetime

from my_meter_api.MyMeterApi import MyMeterApi
from my_meter_api.error import MyMeterError
from my_meter_api.util import UsageDirection, UsageInterval
import sys


def main():
    from dotenv import dotenv_values # type: ignore

    config = dotenv_values(".env")
    baseUrl = config.get("BASE_URL", None)
    rememberMeCookie = config.get("REMEMBER_ME_COOKIE", None)
    sidCookie = config.get("SID_COOKIE", None)
    meterNumber = config.get("METER_NUMBER", None)
    cookieRequestVerificationToken = config.get("REQUEST_VERIFICATION_TOKEN", None)

    if not all([baseUrl, rememberMeCookie, sidCookie, meterNumber]):
        print("Please set the required environment variables in the .env file.")
        return

    now = datetime.datetime.now()
    default_start = now - datetime.timedelta(days=30)
    default_end = now
    default_usage = UsageInterval.Daily

    # Parse command line arguments: start, end, usage
    # Usage: python example.py [start] [end] [usage]
    # Dates in YYYY-MM-DD, usage in ['Daily', 'Hourly', ...]
    args = sys.argv[1:]
    try:
        startDate = datetime.datetime.strptime(args[0], "%Y-%m-%d") if len(args) > 0 else default_start
    except Exception:
        startDate = default_start
    try:
        endDate = datetime.datetime.strptime(args[1], "%Y-%m-%d") if len(args) > 1 else default_end
    except Exception:
        endDate = default_end
    try:
        usageInterval = UsageInterval[args[2]] if len(args) > 2 and args[2] in UsageInterval.__members__ else default_usage
    except Exception:
        usageInterval = default_usage

    api = MyMeterApi(
        baseUrl, rememberMeCookie, sidCookie, cookieRequestVerificationToken
    )

    try:
        usage_data = api.downloadUsage(
            meterNumber, startDate.date(), endDate.date(), usageInterval
        )
        for value in usage_data:
            if value.usage_direction == UsageDirection.Delivered:
                interval_seconds = (value.toDate - value.fromDate).total_seconds()
                if interval_seconds < 24 * 3600:
                    # Less than a day: show time to time on day (AM/PM)
                    print(
                        f"Used: {value.consumption:.4f} kWh from {value.fromDate.strftime('%I:%M %p')} to {value.toDate.strftime('%I:%M %p')} on {value.fromDate.strftime('%d/%m/%Y')}"
                    )
                elif interval_seconds == 24 * 3600:
                    # Exactly one day: show on day
                    print(
                        f"Used: {value.consumption:.4f} kWh on {value.fromDate.strftime('%d/%m/%Y')}"
                    )
                else:
                    # More than a day: show from day to day
                    print(
                        f"Used: {value.consumption:.4f} kWh from {value.fromDate.strftime('%d/%m/%Y')} to {value.toDate.strftime('%d/%m/%Y')}"
                    )
        print(f"Downloaded {len(usage_data)} usage values.")
    except MyMeterError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()