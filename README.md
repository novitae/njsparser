# NJSParser
A powerful **parser** and **explorer** for any website built with [NextJS](https://nextjs.org).
- Parses flight data (from the **`self.__next_f.push`** scripts).
- Parses next data from **`__NEXT_DATA__`** script.
- Parses **build manifests**.
- Searches for **build id**.
- Many other things ...

It uses only **lxml**, **orjson**, **pydantic** to garantee a fast and efficient data parsing and processing.
## Installation:
```
pip install njsparser
```
## Use
### CLI
You can use the cli from 3 different commands:
- `njsp`
- `njsparser`
- `python3 -m njsparser.cli`
It has only one functionality of displaying informations about the website, like this:
![](./src/Capture%20d’écran%202024-12-27%20à%2013.01.10.png)
For more informations, use the `--help` argument with the command.
### Parsing `__next_f`.
The data you find in `__next_f` is called flight data, and contains data under react format. You can parse it easily with `njsparser` the way it follows.

*We will build a parser for the [flight data example](examples/flight_data.py)*

1. In the website you want to parse, make sure you see the `self.__next_f.push` in the begining of script contained the data you search for. Here I am searching for the description `"I should really have a better hobby, but this is it..."` (in blue) in [my page](https://mediux.pro/user/r3draid3r04), and I can also see the `self.__next_f.push` (in green). ![](./src/Capture%20d’écran%202024-12-12%20à%2015.44.11.png)
2. Then I will do this simple script, to parse, then dump the flight data of my website, and see what objects I am searching for:
   ```py
   import requests
   import njsparser
   import json

   # Here I get my page's html
   response = requests.get("https://mediux.pro/user/r3draid3r04").text
   # Then I parse it with njsparser
   fd = njsparser.BeautifulFD(response)
   # Then I will write to json the content of the flight data
   with open("fd.json", "w") as write:
       # I use the njsparser.default function to support the dump of the flight data objects.
       json.dump(fd, write, indent=4, default=njsparser.default)
   ```
3. In my dumped flight data, I will search for the same string: ![](./src/Capture%20d’écran%202024-12-12%20à%2015.51.01.png)
4. Then I will do to the closed `"value"` root to my found string, and look at the value of `"cls"`. Here it is `"Data"`: ![](./src/Capture%20d’écran%202024-12-12%20à%2015.51.17.png)
5. Now that I know the `"cls"` (class) of object my data is contained in, I can search for it in my `BeautifulFD` object:
   ```py
   import requests
   import njsparser
   import json

   # Here I get my page's html
   response = requests.get("https://mediux.pro/user/r3draid3r04").text
   # Then I parse it with njsparser
   fd = njsparser.BeautifulFD(response)
   # Then I iterate over the different classes `Data` in my flight data.
   for data in fd.find_iter([njsparser.T.Data]):
       # Then I make sure that the content of my data is not None, and
       # check if the key `"user"` is in the data's content. If it is,
       # then i break the loop of searching.
       if data.content is not None and "user" in data.content:
           break
   else:
       # If i didn't find it, i raise an error
       raise ValueError

   # Now i have the data of my user
   user = data.content["user"]
   # And I can print the string i was searching for before
   print(user["tagline"])
   ```

More informations:
- If your object is inside another object (e.g. `"Data"` in a `"DataParent"`, or in a `"DataContainer"`), the `.find_iter` will also find it recursively (except if you set `recursive=False`).
- Make sure you use the correct flight data classes attributes when fetching their data. The class `"Data"` has a `.content` attribute. If you use `.value`, you will end up with the raw value and will have to parse it yourself. If you work with a `"DataParent"` object, instead of using `.value` (that will give you `["$", "$L16", None, {"children": ["$", "$L17", None, {"profile": {}}]}])`, use `.children` (that will give you a `"Data"` object with a `.content` of `{"profile": {}}`). Check for the [type file](njsparser/parser/types.py) to see what classes you're interested in, and their attributes.
- You can also use `.find` on `BeautifulFD` to return the only first occurence of your query, or None if not found.

### Parsing `<script id='__NEXT_DATA__'>`
Just do:
```py
import njsparser

html_text = ...
data = njsparser.get_next_data(html_text)
```
If the page contains any script `<script id='__NEXT_DATA__'>`, it will return the json loaded data, otherwise will return `None`.