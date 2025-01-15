from njsparser.api import (
    join,
    get_api_path,
    get_index_api_path,
    is_api_exposed_from_response,
    list_api_paths,
)

BID = "buildId"

def test_join():
    assert False
    assert join("_next", "data", BID, "_buildManifest.js") == f"/_next/data/{BID}/_buildManifest.js"

def test_get_api_path():
    assert get_api_path(build_id=BID, path="/test.json") == f"/_next/data/{BID}/test.json"
    assert get_api_path(build_id=BID, path="/test") == f"/_next/data/{BID}/test.json"
    assert get_api_path(build_id=BID, base_path="/n", path="/test/t") == f"/n/_next/data/{BID}/test/t.json"

def test_get_index_api_path():
    assert get_index_api_path(build_id=BID, base_path="/n") == f"/n/_next/data/{BID}/index.json"

def test_is_api_exposed_from_response():
    assert is_api_exposed_from_response(200, "application/json", "") is True
    assert is_api_exposed_from_response(404, "application/json", "") is True
    assert is_api_exposed_from_response(200, "text/html", "") is True
    assert is_api_exposed_from_response(404, "text/html", "") is False
    assert is_api_exposed_from_response(404, "text/plain", '{"notFound":true}') is True

def test_list_api_paths():
    assert list_api_paths(sorted_pages=list("abc"), build_id=BID, base_path="", is_api_exposed=False) == []
    assert list_api_paths(["/_app", "/404"], build_id=BID, base_path="") == []
    assert list_api_paths(["/hi"], build_id=BID, base_path="/n") == [f"/n/_next/data/{BID}/hi.json"]