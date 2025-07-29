import datetime

from lib import MyMeterApi
from lib.error import MyMeterError
from lib.util import UsageInterval


def main():
    from dotenv import dotenv_values

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
    startDate = now - datetime.timedelta(days=30)
    endDate = now
    usageInterval = UsageInterval.FifteenMinutes

    api = MyMeterApi(
        baseUrl, rememberMeCookie, sidCookie, cookieRequestVerificationToken
    )

    try:
        usage_data = api.downloadUsage(
            meterNumber, startDate.date(), endDate.date(), usageInterval
        )
        for value in usage_data:
            print(value)
        print(f"Downloaded {len(usage_data)} usage values.")
    except MyMeterError as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()