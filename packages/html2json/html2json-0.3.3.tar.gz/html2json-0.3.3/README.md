[![PyPi version](https://img.shields.io/pypi/v/html2json.svg)](https://pypi.python.org/pypi/html2json/)
[![PyPi pyversions](https://img.shields.io/pypi/pyversions/html2json.svg)](https://pypi.python.org/pypi/html2json/)
[![PyPi license](https://img.shields.io/pypi/l/html2json.svg)](https://pypi.python.org/pypi/html2json/)

Convert a HTML webpage to JSON data using a template defined in JSON.

Installation Guide
----

This package is available on PyPi. Just use `pip install -U html2json` to install it. Then you can import it using `from html2json import collect`.

- Note that starting version 0.3.0, at least Python 3.9 is required.

API
----

The method is `collect(html, template)`. `html` is the HTML of page loaded as string, and `template` is the JSON of template loaded as Python objects.

Note that the HTML must contain the root node, like `<html>...</html>` or `<div>...</div>`.

Template Syntax
----

| For detailed syntax examples, please refer to unit tests (with 100% coverage).

The basic syntax is `keyName: [selector, attr, [listOfRegexes]]`.
    1. `selector` is a CSS selector (supported by [lxml](http://lxml.de/)).
        - When the selector is `null`, the root node itself is matched.
        - When the selector cannot be matched, `null` is returned.
        - When the selector matches single element, a string is returned.
        - When the selector matches multiple elements, a list of string is returned.
        - If only selector is needed, you can just specify a string instead of list.
    2. `attr` matches the attribute value. It can be `null` to match either the inner text or the outer text when the inner text is empty.
        - Optional when only selector is needed.
    3. The list of regexes `[listOfRegexes]` supports two forms of regex operations. The operations with in the list are executed sequentially.
        - Replacement: `s/regex/replacement/g`. `g` is optional for multiple replacements.
        - Extraction: `/regex/`.
        - Note that you can use any character as separator instead of `/`.
        - Optional when only selector and/or attribute are needed.

For example:

```json
{
    "Color": ["head link:nth-of-type(1)", "href", ["/\\w+(?=\\.css)/"]],
}
```

Starting version 0.3.1, besides value, key can also matched like `"[selector, ...]": ...`. Note that key must be a string for valid JSON.

- When the selector cannot be matched, key is not added to JSON.
- When the selector matches single element, returned string is used as key.
- When the selector matches multiple elements, list of returned strings are used as multiple keys.

Starting version 0.3.1, you can also replace certain part of value's selector with current key using syntax `...{key}...`. This is especially useful when key is dynamic.

<br/>

As JSON, nested structure can be easily constructed.

```json
{
    "Cover": {
        "URL": [".cover img", "src", []],
        "Number of Favorites": [".cover .favorites", "value", []]
    },
}
```

<br/>

An alternative simplified syntax `keyName: [subRoot, subTemplate]` can be used.
    1. `subRoot` a CSS selector of the new root for each sub entry.
    2. `subTemplate` is a sub-template for each entry, recursively.

For example, the previous example can be simplified as follow.

```json
{
    "Cover": [".cover", {
        "URL": ["img", "src", []],
        "Number of Favorites": [".favorites", "value", []]
    }],
}
```

<br/>

To extract a list of sub-entries following the same sub-template, the list syntax is `keyName: [[subRoot, subTemplate]]`. Please note the difference (surrounding `[` and `]`) from the previous syntax above.
    1. `subRoot` is the CSS selector of the new root for each sub entry.
    2. `subTemplate` is the sub-template for each entry, recursively.
        - Optional or `null` to match entire sub-root

For example:

```json
{
    "Comments": [[".comments", {
        "From": [".from", null, []],
        "Content": [".content", null, []],
        "Photos": [["img", {
            "URL": ["", "src", []]
        }]]
    }]]
}
```
