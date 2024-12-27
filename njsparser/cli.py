import requests
import typer
from rich.console import Console

from njsparser import tools, utils, parser, api

app = typer.Typer()
console = Console()

@app.command()
def analyze(url: str, force_api: bool = False):
    """Scan the given website to find any interesting exploitable data.

    Args:
        url (str): The url of the website to analyze (can contain a path).
    """
    main_response = requests.get(url=url)
    assert main_response.status_code == 200, main_response.status_code
    domain = main_response.url.split("/", 3).pop(2)
    base_url = f"https://{domain}"
    value = utils.make_tree(value=main_response.text)
    assert tools.has_nextjs(value=value) is True, "page doesn't have nextjs"
    assert (build_id := tools.find_build_id(value=value)) is not None, "can't find any build id"
    print("Build Id:", build_id)
    assert (base_path := parser.get_base_path(value=value, remove_domain=True)) is not None, "no next static url found"
    if parser.has_flight_data(value=value):
        print("The site contains flight data.")
    if parser.has_next_data(value=value):
        print("The site contains a __NEXT_DATA__ script.")
    index_api_path = api.get_index_api_path(build_id=build_id, base_path=base_path)
    is_api_exposed_response = requests.get(f"{base_url}{index_api_path}")
    is_api_exposed = api.is_api_exposed_from_response(
        status_code=is_api_exposed_response.status_code,
        content_type=is_api_exposed_response.headers["Content-Type"],
        text=is_api_exposed_response.text
    )
    build_manifest_path = parser.get_build_manifest_path(build_id=build_id, base_path=base_path)
    build_manifest_resp = requests.get(f"{base_url}{build_manifest_path}")
    assert build_manifest_resp.status_code == 200, build_manifest_resp.status_code
    build_manifest = parser.parse_buildmanifest(script=build_manifest_resp.text)
    sorted_pages = build_manifest.get("sortedPages") or []
    if sorted_pages:
        print("Pages:")
        for page in sorted_pages:
            print(f"- {base_url}{page}")
    if (api_paths := api.list_api_paths(
        sorted_pages=sorted_pages,
        build_id=build_id,
        base_path=base_path,
        is_api_exposed=is_api_exposed or force_api,
    )):
        if is_api_exposed:
            print("The api is exposed, possible endpoints:")
        else:
            print("Forced api endpoints display:")
        for page in api_paths:
            print(f"- {base_url}{page}")

# https://linktr.ee/profiles/_next/data/30108fd15e4750972e218b4f910c6d98db8e774c/index.json
# Redirecting infinitely
# 

if __name__ == "__main__":
    app()