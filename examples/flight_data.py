import requests
import njsparser
import json

response = requests.get(
    "https://mediux.pro/user/r3draid3r04",
    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15"},
)
fd = njsparser.BeautifulFD(response.text)
assert fd, "no flight data found"
for data in fd.find_iter([njsparser.Data]):
    if data.content is not None and "user" in data.content:
        break
else:
    exit("Did not find any dict :'(")
print(
    json.dumps(
        {
            key: value for key, value in data.content["user"].items()
            if isinstance(value, (bool, int)) or (isinstance(value, str) and len(value) < 100)
        },
        indent=4
    )
)