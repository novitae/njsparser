import requests
from njsparser import get_next_data
import json

response = requests.get(
    "https://www.lego.com/en-us/product/the-botanical-garden-21353",
    headers={"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.1.1 Safari/605.1.15"},
)
# Gets the content of the `@id='__NEXT_DATA__'` script.
next_data = get_next_data(value=response.text)
print("build Id:", next_data["buildId"])
product = next_data["props"]["pageProps"]["__APOLLO_STATE__"]["SingleVariantProduct:cc5f6935-215b-4d56-9a5f-4ad1c23d634e"]
print(
    json.dumps(
        {
            key: value for key, value in product.items()
            if isinstance(value, (bool, int)) or (isinstance(value, str) and len(value) < 100)
        },
        indent=4
    )
)