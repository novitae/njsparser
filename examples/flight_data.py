import requests
import njsparser
import json

response = requests.get(
    "https://mediux.pro/user/r3draid3r04",
    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15"},
)
flight_data = njsparser.get_flight_data(value=response.text)
assert flight_data is not None
for filtered_flight_data in njsparser.finditer_in_flight_data(flight_data, [njsparser.Data]):
    if filtered_flight_data.content is not None:
        break
else:
    exit("Did not find any dict :'(")
print(
    json.dumps(
        {
            key: value for key, value in filtered_flight_data.content["user"].items()
            if isinstance(value, (bool, int)) or (isinstance(value, str) and len(value) < 100)
        },
        indent=4
    )
)