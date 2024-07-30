# NJSParser
#### Python NextJS data parser from HTML.

*Still in dev + I have never read any single docs about NextJS, just reversed based from some websites, so there might be stuff and cases missing, feel free to open issues.*

**📥 Install with `git install git+https://github.com/novitae/njsparser`**.

Use like:
```py
Last login: Tue Jul 30 08:55:37 on ttys000
n@ns-MacBook-Pro ~ % cd njsparser
n@ns-MacBook-Pro njsparser % py
Python 3.11.9 (main, Apr  2 2024, 08:25:04) [Clang 15.0.0 (clang-1500.3.9.4)] on darwin
Type "help", "copyright", "credits" or "license" for more information.
>>> # I import everything from njsparser.
>>> from njsparser import *
>>> import ujson
>>>
>>> # Then i am opening a page that has not nextjs in it.
>>> with open("lego.html", "r") as read:
...     has_nextjs(read.read())
...
False
>>> # And here a page that has some nextjs in it.
>>> # I am adding `return_elements=True` so I can get the elements that were
>>> # found during the search, and avoir doing it again.
>>> with open("mintstars_found.html", "r") as read:
...     has, elements = has_nextjs(read.read(), return_elements=True)
...
>>> # We can then see that it contains some nextjs, and that it found 18 elements.
>>> has, len(elements)
(True, 18)
>>> print(ujson.dumps(elements, indent=2))
[
  "1:HL[\"\/_next\/static\/media\/2d141e1a38819612-s.p.woff2\",\"font\",{\"crossOrigin\":\"\",\"type\":\"font\/woff2\"}]\n2:HL[\"\/_next\/static\/css\/4d38074da0a0fb69.css\",\"style\"]\n3:HL[\"\/_next\/static\/css\/46d2f1b70d0e73f2.css\",\"style\"]\n4:HL[\"\/_next\/static\/css\/5ef1019dd2f2a6a4.css\",\"style\"]\n",
  ... # And 17 more
]
>>> # And here I can parse all the elements
>>> parsed = parse_nextjs_from_elements(elements)
>>> # Here's a part of them:
>>> print(ujson.dumps(parsed[6:8], indent=2))
[
  {
    "value": [
      61343,
      [],
      ""
    ],
    "value_class": "I",
    "index": 10
  },
  {
    "value": [
      70207,
      [
        "2516",
        "static\/chunks\/f7333993-c82449f819646307.js",
        "3814",
        "static\/chunks\/3a91511d-8661183a1ab711c7.js",
        "7903",
        "static\/chunks\/7903-74b438fb77d6adff.js",
        "4666",
        "static\/chunks\/4666-6e1ed75c2f62bfa8.js",
        "998",
        "static\/chunks\/998-221a0f85b7ba0e1e.js",
        "9790",
        "static\/chunks\/9790-476b34183b3c4b8c.js",
        "7589",
        "static\/chunks\/7589-ff7e58f6b3069806.js",
        "9371",
        "static\/chunks\/9371-6ce8dd2e9670386e.js",
        "9857",
        "static\/chunks\/9857-1545e07304236cfe.js",
        "4649",
        "static\/chunks\/4649-3c443475360b8388.js",
        "2322",
        "static\/chunks\/2322-0cc1d6ebdb7a7926.js",
        "5885",
        "static\/chunks\/5885-ce226ae4555f0b39.js",
        "1397",
        "static\/chunks\/1397-d6d57deb7a638be6.js",
        "8613",
        "static\/chunks\/8613-cf1649cfac2fab0c.js",
        "3185",
        "static\/chunks\/app\/layout-5f9563461a5a92b8.js"
      ],
      "Providers"
    ],
    "value_class": "I",
    "index": 13
  }
]
>>> # You can do all of this from an HTML string, with:
>>> parse_nextjs_from_text(text=text)
...
>>> # Or from an lxml tree, with:
>>> from lxml import etree
>>> tree = etree.HTML(text=text)
>>> parse_nextjs_from_tree(tree=tree)
...
>>> # If no nextjs is found in both of these examples, there result will be None.
>>> # You can filter the result to have only some elements of certains classes:
>>> parse_nextjs_from_tree(tree=tree, classes_filter=[None, "E"])
...
```