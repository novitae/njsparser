import re
from typing import Any

from ..utils import logger, join
from .urls import _NS
from .js import loads

_build_manifest_name, _ssg_manifest_name = "_buildManifest.js", "_ssgManifest.js"
_build_manifest_path, _ssg_manifest_path = f"/{_build_manifest_name}", f"/{_ssg_manifest_name}"
_manifest_paths = (_build_manifest_path, _ssg_manifest_path)

_re_function_buildmanifest = re.compile(r"^function\((?P<keys>(?:[\w$]+,)*[\w$]+)\)\s*{\s*return\s*(?P<content>{[\S\s]*})\s*}\((?P<values>.*?)\)")
def parse_buildmanifest(script: str) -> dict[str, Any]:
    """Parses the buildmanifest script (`"/_buildManifest.js"`).

    Args:
        script (str): The content of the script.

    Returns:
        dict[str, Any] | None: The content of the script, or nothing if no matches.
    """
    s = script.lstrip()
    if s.startswith("self.__BUILD_MANIFEST") is False:
        raise ValueError( 'Invalid build manifest (not starting by '
                          '`"self.__BUILD_MANIFEST"`).' )
    else:
        s = s.removeprefix("self.__BUILD_MANIFEST").lstrip().removeprefix("=").lstrip()
    if s.startswith("{"):
        return loads(string=s)
    elif (match := _re_function_buildmanifest.search(s)):
        groupdict = match.groupdict()
        keys = [item.strip() for item in groupdict.pop("keys").split(",")]
        values = loads(string="[{}]".format(groupdict.pop("values")))
        return loads(string=groupdict.pop("content"), kwargs=dict(zip(keys, values)))
    else:
        logger.warning(f'Could not parse the given build manifest `{s}`')
    
def get_build_manifest_path(build_id: str, base_path: str = None):
    """Gives the path of the build manifest based on the given build id
    and base path.

    Args:
        build_id (str): The build id of the website.
        base_path (str, optional): The base path (can be obtained with
            `njsparser.tools.get_base_path(...)`). Defaults to None.

    Returns:
        str: The path of the build manifest.
    """
    base_path = "" if base_path is None else base_path
    return join(base_path, _NS, build_id, _build_manifest_name)
