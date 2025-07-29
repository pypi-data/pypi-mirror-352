from datetime import datetime, timedelta
from enum import Enum
from html.parser import HTMLParser


class UsageInterval(Enum):
    FifteenMinutes = 3
    ThirtyMinutes = 4
    Hourly = 5
    Daily = 6
    Weekly = 8
    Monthly = 9
    # Billing = 7

    @staticmethod
    def durationInMinutes(interval: "UsageInterval") -> int:
        if interval == UsageInterval.FifteenMinutes:
            return 15
        elif interval == UsageInterval.ThirtyMinutes:
            return 30
        elif interval == UsageInterval.Hourly:
            return 60
        elif interval == UsageInterval.Daily:
            return 1440
        elif interval == UsageInterval.Weekly:
            return 10080
        elif interval == UsageInterval.Monthly:
            return 43200
        else:
            raise ValueError(f"Unknown usage interval: {interval}")


class MyMeterUsageValue:
    def __init__(
        self, fromDate: datetime, interval: "UsageInterval", usage_direction: str, consumption: float
    ):
        self.fromDate = fromDate
        self.interval = interval
        self.usage_direction = usage_direction
        self.consumption = consumption

    def __str__(self):
        return f"MyMeterUsageValue(read_date={self.read_date}, usage_direction={self.usage_direction}, consumption={self.consumption})"

    def __repr__(self):
        return f"MyMeterUsageValue({self.read_date}, {self.usage_direction}, {self.consumption})"
    
    @property
    def toDate(self):
        return self.fromDate + timedelta(minutes=UsageInterval.durationInMinutes(self.interval))

# TOKEN_REGEX = re.compile(
#     r'(?:name=\\"__RequestVerificationToken)(?:[\\"\w\s=]*)value=\\"(.*?)\\"|value=\\"(.*?)\\"(?:[\\"\w\s=]*)(?:name=\\"__RequestVerificationToken)'
# )
class RequestVerificationTokenParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.token = None

    def handle_starttag(self, tag, attrs):
        if tag == "input":
            attrs_dict = dict(attrs)
            if (
                attrs_dict.get("name") == "__RequestVerificationToken"
                and "value" in attrs_dict
            ):
                self.token = attrs_dict["value"]

    def get_token(self):
        return self.token
