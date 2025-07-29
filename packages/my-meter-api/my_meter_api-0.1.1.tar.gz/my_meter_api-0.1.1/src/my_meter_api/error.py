import json
import requests


class MyMeterError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f"MyMeterError: {self.message}"

    def __repr__(self):
        return f"MyMeterError({self.message})"


class MyMeterHttpError(MyMeterError):
    def __init__(self, message: str, status_code: int):
        super().__init__(message)
        self.status_code = status_code

    def __str__(self):
        return f"MyMeterHttpError: {self.message} (Status Code: {self.status_code})"

    def __repr__(self):
        return f"MyMeterHttpError({self.message}, {self.status_code})"


class MyMeterInternalError(MyMeterError):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return f"MyMeterInternalError: {self.message}"

    def __repr__(self):
        return f"MyMeterInternalError({self.message})"


class MyMeterApiError(MyMeterError):
    def __init__(self, title: str, code: str, details: str):
        super().__init__(f"{title} (Code: {code}) - {details}")
        self.title = title
        self.code = code
        self.details = details

    def __str__(self):
        return f"MyMeterApiError: {self.title} (Code: {self.code}) - {self.details}"

    def __repr__(self):
        return f"MyMeterApiError({self.title}, {self.code}, {self.details})"

    # Parse a application/problem+json response from the MyMeter API
    @staticmethod
    def from_response(response: requests.Response):
        try:
            # Parse the JSON response
            data = response.json()
            title = data.get("title", "Unknown Error")
            code = data.get("status", "Unknown Status")
            details = data.get("detail", "No details provided")
            return MyMeterApiError(title, code, details)
        except json.JSONDecodeError:
            return MyMeterApiError(
                "Invalid JSON Response",
                "JSONDecodeError",
                "Could not parse the error response.",
            )


class MyMeterParseError(MyMeterError):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return f"MyMeterParseError: {self.message}"

    def __repr__(self):
        return f"MyMeterParseError({self.message})"


class MyMeterInvalidAuthenticationError(MyMeterError):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return f"MyMeterInvalidAuthenticationError: {self.message}"

    def __repr__(self):
        return f"MyMeterInvalidAuthenticationError({self.message})"


