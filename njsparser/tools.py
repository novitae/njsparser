from .utils import _supported_tree, make_tree, logger
from .parser.next_data import has_next_data, get_next_data
from .parser.flight_data import has_flight_data, get_flight_data
from .parser.types import FlightRSCPayload
from .parser.urls import get_next_static_urls, get_base_path, _NS
from .parser.manifests import parse_buildmanifest, _manifest_paths

__all__ = ("has_nextjs", "find_build_id")

def has_nextjs(value: _supported_tree):
    """Tells if the page has some nextjs data in it.

    Args:
        value (_supported_tree): The page to check for.

    Returns:
        bool: True if it contains any nextjs data, otherwise, False.
    """
    return any([has_next_data(value=value), has_flight_data(value=value)])

def find_build_id(value: _supported_tree) -> str | None:
    """Searches and return (or not) the build id of the given page.

    Args:
        value (_supported_tree): The page to find the build id from.

    Returns:
        str | None: Either the buildId if it was found, or None if it didn't.
    """
    tree = make_tree(value=value)

    # Searches through the static next urls, and if we find anything that ends
    # with `"/_buildManifest.js"` or `"/_ssgManifest.js"`, we can extract the
    # build id from it.
    if (next_static_urls := get_next_static_urls(value=tree)) is not None:
        base_path = get_base_path(value=next_static_urls, remove_domain=False)
        for next_static_url in next_static_urls:
            sliced_su = next_static_url.removeprefix(base_path).removeprefix(_NS)
            for manifest_path in _manifest_paths:
                if sliced_su.endswith(manifest_path):
                    return sliced_su.removesuffix(manifest_path)
                
    # We search for the buildId directly into the `__NEXT_DATA__` script.
    if (next_data := get_next_data(value=tree)) is not None:
        if "buildId" in next_data:
            return next_data["buildId"]
        else:
            logger.warning( "Found a next_data dict in the page, " \
                            "but did't contain any `buildId` key." )
            
    # We search for the builId in the flight data.
    elif (flight_data := get_flight_data(value=tree)) is not None:
        if isinstance(flight_data[0], FlightRSCPayload):
            return flight_data[0].build_id
        else:
            logger.warning( "Found flight data in the page, but " \
                            "couldnt find the build id. If are certain" \
                            " there is one, open an issue with your " \
                            "html to investigate :)" )
            