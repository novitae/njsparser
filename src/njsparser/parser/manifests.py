import re
from typing import Any
import pythonmonkey

from ..utils import logger, join
from .urls import _NS

_build_manifest_name, _ssg_manifest_name = "_buildManifest.js", "_ssgManifest.js"
_build_manifest_path, _ssg_manifest_path = f"/{_build_manifest_name}", f"/{_ssg_manifest_name}"
_manifest_paths = (_build_manifest_path, _ssg_manifest_path)

def parse_buildmanifest(script: str) -> dict[str, Any]:
    """Parses the buildmanifest script (`"/_buildManifest.js"`).

    Args:
        script (str): The content of the script.

    Returns:
        dict[str, Any] | None: The content of the script, or nothing if no matches.
    """
    s = script.strip()
    if s.startswith("self.__BUILD_MANIFEST") is False:
        raise ValueError( 'Invalid build manifest (not starting by '
                          '`"self.__BUILD_MANIFEST"`).' )
    func = f"""(function() {{self={{}};{s.removesuffix(";")};return self.__BUILD_MANIFEST}})();"""
    try:
        return pythonmonkey.eval(func)
    except pythonmonkey.SpiderMonkeyError:
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
