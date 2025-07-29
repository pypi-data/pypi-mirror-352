from datetime import datetime, timedelta
from enum import Enum

class UsageDirection(Enum):
    Delivered = "Delivered"
    Received = "Received"

    @staticmethod
    def fromString(direction: str) -> "UsageDirection":
        if direction == "Delivered":
            return UsageDirection.Delivered
        elif direction == "Received":
            return UsageDirection.Received
        else:
            raise ValueError(f"Unknown usage direction: {direction}")

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
    
    @staticmethod
    def fromString(interval: str) -> "UsageInterval":
        if interval == "FifteenMinutes":
            return UsageInterval.FifteenMinutes
        elif interval == "ThirtyMinutes":
            return UsageInterval.ThirtyMinutes
        elif interval == "Hourly":
            return UsageInterval.Hourly
        elif interval == "Daily":
            return UsageInterval.Daily
        elif interval == "Weekly":
            return UsageInterval.Weekly
        elif interval == "Monthly":
            return UsageInterval.Monthly
        else:
            raise ValueError(f"Unknown usage interval: {interval}")
    
    def __str__(self):
        if self == UsageInterval.FifteenMinutes:
            return "Fifteen Minutes"
        elif self == UsageInterval.ThirtyMinutes:
            return "Thirty Minutes"
        else:
            return self.name

class MyMeterUsageValue:
    def __init__(
        self, fromDate: datetime, interval: "UsageInterval", usage_direction: "UsageDirection", consumption: float
    ):
        self.fromDate = fromDate
        self.interval = interval
        self.usage_direction = usage_direction
        self.consumption = consumption

    def __str__(self):
        return f"{self.usage_direction.value} {self.consumption} kWh from {self.fromDate} to {self.toDate} ({self.interval.name} interval)"

    def __repr__(self):
        return f"MyMeterUsageValue({self.read_date}, {self.interval}, {self.usage_direction}, {self.consumption})"
    
    @property
    def toDate(self):
        return self.fromDate + timedelta(minutes=UsageInterval.durationInMinutes(self.interval))

