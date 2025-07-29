import csv
import datetime
from html.parser import HTMLParser
import requests

from my_meter_api.error import MyMeterApiError, MyMeterHttpError, MyMeterInternalError, MyMeterInvalidAuthenticationError, MyMeterParseError
from my_meter_api.util import MyMeterUsageValue, UsageDirection, UsageInterval


# TOKEN_REGEX = re.compile(
#     r'(?:name=\\"__RequestVerificationToken)(?:[\\"\w\s=]*)value=\\"(.*?)\\"|value=\\"(.*?)\\"(?:[\\"\w\s=]*)(?:name=\\"__RequestVerificationToken)'
# )
class _RequestVerificationTokenParser(HTMLParser):
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

class MyMeterApi:
    def __init__(
        self,
        baseUrl: str,
        rememberMeCookie: str,
        sidCookie: str,
        cookieRequestVerificationToken: str,
    ):
        self.baseUrl = baseUrl
        self.rememberMeCookie = rememberMeCookie
        self.sidCookie = sidCookie
        self.cookieRequestVerificationToken = cookieRequestVerificationToken

    def getFormRequestVerificationToken(self) -> str:
        headers = {
            "Cookie": f"MM_SID={self.sidCookie}; MM_RememberMe={self.rememberMeCookie}; __RequestVerificationToken={self.cookieRequestVerificationToken}",
        }
        response = requests.get(f"{self.baseUrl}/Dashboard", headers=headers)
        if response.status_code != 200:
            raise MyMeterHttpError(
                f"Failed to get request verification token: {response.text}",
                response.status_code,
            )
        parser = _RequestVerificationTokenParser()
        parser.feed(response.text)
        formRequestVerificationToken = parser.get_token()
        if not formRequestVerificationToken:
            raise MyMeterParseError(
                "Failed to parse request verification token from the response."
            )
        return formRequestVerificationToken

    def makeBody(
        self,
        meterNumber: str,
        startDate: datetime.date,
        endDate: datetime.date,
        usageInterval: UsageInterval,
        requestVerificationToken: str,
    ) -> str:
        values = {
            "HasMultipleUsageTypes": "false",
            "FileFormat": "download-usage-csv",
            "SelectedFormat": "2",
            "ThirdPartyPODID": "",
            "SelectedServiceType": "1",
            "Meters[0].Value": meterNumber,
            "Meters[0].Selected": "true",
            "SelectedInterval": str(usageInterval.value),
            "SelectedUsageType": "1",
            "Start": startDate.strftime("%Y-%m-%d"),
            "End": endDate.strftime("%Y-%m-%d"),
            "ColumnOptions[0].Value": "ReadDate",
            "ColumnOptions[0].Name": "ReadDate",
            "ColumnOptions[0].Checked": "false",
            "ColumnOptions[1].Value": "UsageDirection",
            "ColumnOptions[1].Name": "UsageDirection",
            "ColumnOptions[1].Checked": "false",
            "ColumnOptions[2].Value": "Consumption",
            "ColumnOptions[2].Name": "Consumption",
            "ColumnOptions[2].Checked": "false",
            "RowOptions[0].Value": "ReadDate",
            "RowOptions[0].Name": "Read%20Date",
            "RowOptions[0].Desc": "false",
            "RowOptions[1].Value": "UsageDirection",
            "RowOptions[1].Name": "Usage%20Direction",
            "RowOptions[1].Desc": "false",
            "RowOptions[2].Value": "Consumption",
            "RowOptions[2].Name": "kWh",
            "RowOptions[2].Desc": "false",
            "__RequestVerificationToken": requestVerificationToken,
        }
        return "&".join(
            f"{key}={value}" for key, value in values.items() if value is not None
        )

    def downloadUsageRaw(
        self,
        meterNumber: str,
        startDate: datetime.date,
        endDate: datetime.date,
        usageInterval: UsageInterval,
        formRequestVerificationToken: str,
    ):
        body = self.makeBody(
            meterNumber, startDate, endDate, usageInterval, formRequestVerificationToken
        )
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Cookie": f"MM_SID={self.sidCookie}; __RequestVerificationToken={self.cookieRequestVerificationToken}; MM_RememberMe={self.rememberMeCookie}",
        }
        response = requests.post(
            f"{self.baseUrl}/Usage/Download",
            data=body,
            headers=headers,
            # cookies={
            #     "MM_RememberMe": self.rememberMeCookie,
            #     "MM_SID": self.sidCookie,
            #     "__RequestVerificationToken": self.requestVerificationToken,
            # },
            allow_redirects=False,
        )
        return response

    def parseUsageRaw(self, raw_data: str, interval: "UsageInterval") -> list[MyMeterUsageValue]:
        usage_values = []
        csv_reader = csv.reader(raw_data.splitlines(), delimiter=",")
        next(csv_reader)
        for row in csv_reader:
            if len(row) < 3:
                continue
            try:
                read_date = datetime.datetime.strptime(row[0], "%m/%d/%Y %I:%M:%S %p")
                usage_direction = row[1].strip()
                consumption = float(row[2])
                usage_values.append(
                    MyMeterUsageValue(read_date, interval, UsageDirection.fromString(usage_direction), consumption)
                )
            except ValueError as e:
                print(f"Error parsing row {row}: {e}")
                continue
        return usage_values

    def downloadUsage(
        self,
        meterNumber: str,
        startDate: datetime.date,
        endDate: datetime.date,
        usageInterval: UsageInterval = UsageInterval.FifteenMinutes,
    ) -> list[MyMeterUsageValue]:
        formRequestVerificationToken = self.getFormRequestVerificationToken()
        response = self.downloadUsageRaw(
            meterNumber, startDate, endDate, usageInterval, formRequestVerificationToken
        )
        if response.status_code == 401:
            raise MyMeterInvalidAuthenticationError(
                "Invalid authentication. Please check your cookies."
            )
        if response.status_code == 403:
            raise MyMeterInvalidAuthenticationError(
                "Access forbidden. Please check your permissions."
            )
        if "application/problem+json" in response.headers.get("Content-Type", ""):
            raise MyMeterApiError.from_response(response)
        if response.status_code != 200:
            raise MyMeterHttpError(
                f"Failed to download usage data: {response.text}",
                response.status_code,
            )
        if "text/csv" not in response.headers.get("Content-Type", ""):
            raise MyMeterInternalError(
                "Unexpected content type received. Expected text/csv."
            )
        return self.parseUsageRaw(response.text, usageInterval)
