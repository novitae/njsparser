from .utils import join

_index_json = "index.json"

_excluded_paths = ("/404", "/_app", "/_error", "/sitemap.xml", "/_middleware")
def get_api_path(build_id: str, base_path: str = None, path: str = None):
    """Returns the path to the `index.json` file.

    Args:
        build_id (str): The build id of the website.
        base_path (str, optional): The base path (can be obtained with
            `njsparser.tools.get_base_path(...)`). Defaults to None.
        path (str, optional): The path to the file to get. Defaults to
            `index.json`.

    Returns:
        str | None: The url to the file, or None if the file has no api equivalent.
    """
    if path is None:
        path = _index_json
    elif path in _excluded_paths:
        return
    if path.endswith(".json") is False:
        path += ".json"
    if path.endswith("/.json"):
        path = _index_json
    return join(base_path, "/_next/data/", build_id, path)

def get_index_api_path(build_id: str, base_path: str = None):
    """Returns the path of the `index.json` api endpoint.

    Args:
        build_id (str): The buildid of the website.
        base_path (str, optional): The base path (can be obtained with
            `njsparser.tools.get_base_path(...)`). Defaults to None.

    Returns:
        str: The path to index.json endpoint.
    """
    return get_api_path(build_id=build_id, base_path=base_path, path=_index_json)

# Works:
# - https://coindrop.to/[piggybankName]
#   https://coindrop.to/_next/data/cSqeZiCyPxe_rbiYdsZdp/[piggybankName].json
# Doesn't:
# - https://www.bible.com/users/[username]
#   https://www.bible.com/_next/data/EhmmkHrUA0ygbv7dJJTtH/users/[username].json
def is_api_exposed_from_response(status_code: int, content_type: str, text: str):
    """Tells if the api is exposed from the response of the request to
    `f"https://{domain}{njsparser.utils.get_index_api_path(...)}"`.

    Args:
        status_code (int): The status code of the response.
        content_type (str): The value of the `"Content-Type"` header from
            the response.
        text (str): The text content of the response.

    Returns:
        bool: Is the api exposed ?
    """
    if status_code == 200:
        return True
    elif content_type.startswith("application/json"):
        return True
    else:
        return text == '{"notFound":true}'
    
def list_api_paths(sorted_pages: list[str], build_id: str, base_path: str, is_api_exposed: bool = None):
    """Lists the api paths based of off the build manifest.

    Args:
        sorted_pages (list[str]): The value `["sortedPages"]` from the
            parsed build manifest.
        build_id (str): The build id of the website.
        base_path (str): The base path (can be obtained by using the
            `njsparser.parser.get_base_path(...)` function).
        is_api_exposed (bool, optional): Is the api exposed ? Should be
            the result of `njsparser.is_api_exposed_from_response(...)`.
            Defaults to True.

    Returns:
        list[str]: The list of api paths exposed.
    """
    result = []
    if is_api_exposed is not False:
        for path in sorted_pages:
            if (api_path := get_api_path(build_id=build_id, base_path=base_path, path=path)) is not None:
                result.append(api_path)
    return result