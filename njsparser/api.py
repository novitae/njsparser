from os.path import join

_index_json = "index.json"

def get_index_api_endpoint(build_id: str, base_path: str = None):
    """Returns the path to the `index.json` file.

    Args:
        build_id (str): The build id of the website.
        base_path (str, optional): The base path (can be obtained with
            `njsparser.tools.get_base_path(...)`). Defaults to None.

    Returns:
        str: The url to the `index.json` file.
    """
    return join(base_path, "/next/data/", build_id, _index_json)