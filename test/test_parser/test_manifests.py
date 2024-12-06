from njsparser.parser.manifests import parse_buildmanifest, get_build_manifest_path
from njsparser.tools import find_build_id
import pytest

from .. import *

def test_parse_buildmanifest():
    assert parse_buildmanifest(nextjs_org_4mSOwJptzzPemGzzI8AOo_buildManifest) is not None
    assert parse_buildmanifest(swag_live_giz3a1H7OUzfxgxRHIdMx_buildManifest) is not None
    assert parse_buildmanifest("""self.__BUILD_MANIFEST = function(e) {
        return {}
    }(1), self.__BUILD_MANIFEST_CB && self.__BUILD_MANIFEST_CB();""") == {}
    assert parse_buildmanifest(app_osint_industries_yAzR27j6CjHLWW3VxUzzi_buildManifest) is not None
    assert parse_buildmanifest("self.__BUILD_MANIFEST=sdfnjjksdfn") is None
    assert parse_buildmanifest(runpod_io_s4xe_TFYlTTFF_bw1HfD4_buildManifest) is not None
    with pytest.raises(ValueError):
        parse_buildmanifest("dfsfdn")

def test_get_build_manifest_path():
    assert get_build_manifest_path(build_id=find_build_id(m_soundcloud_com_html)) == "/_next/static/1733156665/_buildManifest.js"