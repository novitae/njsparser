import re
import barely_json
from typing import Any
from os.path import join

from ..utils import logger
from .urls import _NS

_build_manifest_name, _ssg_manifest_name = "_buildManifest.js", "_ssgManifest.js"
_build_manifest_path, _ssg_manifest_path = f"/{_build_manifest_name}", f"/{_ssg_manifest_name}"
_manifest_paths = (_build_manifest_path, _ssg_manifest_path)

# TODO: Find a better way to parse this.
class _BuildManifestParser:
    def __init__(self) -> None:
        self.kwargs = {}

    def resolver(self, value: Any, source: barely_json._source = None):
        if source != "dict_key":
            if value in self.kwargs:
                return self.kwargs[value]
            elif value in ("undefined", "void 0"):
                return None
        return barely_json.default_resolver(value=value)
        
_re_buildmanifest = re.compile(r"^self\.__BUILD_MANIFEST=function\((?P<keys>(?:\w+,)*\w*)\){return(?P<content>{.*})}\((?P<values>.*?)\)")
def parse_buildmanifest(script: str) -> dict[str, Any]:
    """Parses the buildmanifest script (`"/_buildManifest.js"`).

    Args:
        script (str): The content of the script.

    Returns:
        dict[str, Any] | None: The content of the script, or nothing if no matches.
    """
    if (match := _re_buildmanifest.search(script)) is not None:
        parser, content = _BuildManifestParser(), match.groupdict()
        parser.kwargs = dict(zip(
            content.pop("keys").split(","),
            barely_json.parse("[{}]".format(content.pop("values")), resolver=parser.resolver),
        ))
        return barely_json.parse(content.pop("content"), resolver=parser.resolver)
    elif "self.__BUILD_MANIFEST = function" in script:
        logger.warning( "It looks like the script given to `parse_buildmanifest` is "
                        "beautified. Please feed to this function the raw script." )
        
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
    base_path = base_path or ""
    return join(base_path, _NS, build_id, _build_manifest_name)

# TODO: support non function manifests:
# self.__BUILD_MANIFEST={__rewrites:{afterFiles:[],beforeFiles:[],fallback:[]},"/_error":["static/chunks/pages/_error-dd86bf254bdae9ab.js"],sortedPages:["/_app","/_error"]},self.__BUILD_MANIFEST_CB&&self.__BUILD_MANIFEST_CB();