# MyMeter API

This API can be used to interact with the private API used by the MyMeter application used by some power companies to expose usage data to customers.

**NOTE**: This API is undocumented and could change or break at any time.

## Usage

All functionality is encapsulated within the `MyMeterApi` class. It requires four parameters: `baseUrl`, `rememberMeCookie`, `sidCookie`, and `cookieRequestVerificationToken`.

- `baseUrl` is simply the URL of your power company's MyMeter instance (i.e. "https://mymeter.example.com")
- `rememberMeCookie`, `sidCookie`, and `cookieRequestVerificationToken` are the values of your `MM_RememberMe`, `MM_SID`, and `__RequestVerificationToken` cookies respectively

Once you have an instance of `MyMeterApi`, just call `downloadUsage` with your meter number, the date range you want, and the interval you want to be returned. The API client will automatically perform the CSRF process, and then download and parse a usage CSV, returning an array of `MyMeterUsageValue` objects.

## Running the example

```
cp .env.example .env

# Fill out .env with your configuration

uv sync --dev

uv run ./example.py
```
