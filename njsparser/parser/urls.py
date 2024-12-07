from urllib.parse import urlparse

from ..utils import make_tree, _supported_tree

_N = "/_next"
_NS = f"{_N}/static/"

def get_next_static_urls(value: _supported_tree):
    """Lists all the paths found on the page that contains a `/_next/static/`
    part.

    Args:
        value (_supported_tree): The page to list the paths from.

    Returns:
        list[str] | None: The list of paths, or None if none are found.
    """
    tree = make_tree(value=value)
    result: list[str] = [
        *tree.xpath(f"//*[contains(@href, '{_NS}')]/@href"),
        *tree.xpath(f"//*[contains(@src, '{_NS}')]/@src"),
    ]
    return result or None

def get_base_path(value: _supported_tree | list[str], *, remove_domain: bool = None):
    """Returns the base path of the `/_next/static/` paths. As an example:

    If your page doesn't contain any base path to it, the paths will look
    like `'/_next/static/chunks/blabla.js'`, and the full url will look like
    `'https://www.your.site/_next/static/chunks/blabla.js'`. This function
    would return `''` for this case.

    But if it contains a base path, it might look something like
    `'/hello/_next/static/chunks/blabla.js'`. The prefix would be `'/hello'`
    in this case. The full url would look like
    `'https://www.your.site/hello/_next/static/chunks/blabla.js'`. The
    function will return `/hello` in this case.

    If the paths are absolutes (already containing the domain, like on
    `'https://example.com/hello/_next/static/blabla.png'`), you can set the
    `remove_domain` argument to `True` to remove it, and get only the base
    path. Will return `'/hello'` instead of `'https://example.com/hello'`.

    Args:
        value (_supported_tree | list[str]): The page you want to get the
            nextjs paths prefixes from, or directly the list of paths you
            found.
        remove_domain (bool, optional): Removes the domain at the base of
            the url if there is(`'https://www.hello.com/hi'` -> `'/hi'`).
            Default to False.

    Raises:
        AssertionError: One of the path doesn't contain the `/_next/static/`
            nextjs static path.
        AssertionError: One of the found start of the prefix is not matching
            the ones previously found.

    Returns:
        str | None: Will return the string path, or None if the value is
            a page we didn't find any static nextjs path in it.
    """
    if isinstance(value, list):
        assert all(isinstance(item, str) for item in value)
        paths = value
    else:
        if (paths := get_next_static_urls(value=value)) is None:
            return
    global_index = None
    for path in paths:
        assert (index := path.rfind(_NS)) >= 0, \
            f"can't find '{_NS}' in {path=}"
        if global_index is None:
            global_index = index
        assert index == global_index, \
            f"{index=} of '{_NS}' in {path=} is != {global_index=}"
    
    result = paths[0][:global_index]
    if remove_domain is True and (host := urlparse(url=result).hostname) is not None:
        result = result.split(host, 1).pop()
    return result