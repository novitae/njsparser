from pathlib import Path

d = Path(__file__).parent

# Has NextJS (with recent flight data)
with open(d / "nextjs.org.html", "rb") as read:
    nextjs_org_html = read.read()

# Has NextJS (with flightdata including a noindex data:
# "...\n:HL["/_next/static/css/86a46c8e043ff692.css","style"]\n:HL[...",
# differing from index data:
# "...\n1:HL["/_next/static/css/86a46c8e043ff692.css","style"]\n2:HL[...")
with open(d / "mintstars.com.html", "rb") as read:
    mintstars_com_html = read.read()

# Has NextJS (with older flight data) and custom prefix to static paths
# https://swag.live/user/624dc255c12744f2fdaf90c8
with open(d / "swag.live.html", "rb") as read:
    swag_live_html = read.read()

# Build manifest from nextjs (function)
with open(d / "nextjs_org_4mSOwJptzzPemGzzI8AOo_buildManifest.js", "r") as read:
    nextjs_org_4mSOwJptzzPemGzzI8AOo_buildManifest = read.read()

# Build manifest from swag.live (function)
with open(d / "swag_live_giz3a1H7OUzfxgxRHIdMx_buildManifest.js", "r") as read:
    swag_live_giz3a1H7OUzfxgxRHIdMx_buildManifest = read.read()

# Build manifest from app.osint.industries (not function)
with open(d / "app_osint_industries_yAzR27j6CjHLWW3VxUzzi_buildManifest.js", "r") as read:
    app_osint_industries_yAzR27j6CjHLWW3VxUzzi_buildManifest = read.read()

# Build manifest from runpod.io (function with lot of vars)
with open(d / "runpod_io_s4xe_TFYlTTFF_bw1HfD4_buildManifest.js", "r") as read:
    runpod_io_s4xe_TFYlTTFF_bw1HfD4_buildManifest = read.read()

# Has NextJS (with __next_data__)
with open(d / "m.soundcloud.com.html", "rb") as read:
    m_soundcloud_com_html = read.read()

# Doesn't have NextJS
with open(d / "x.com.html", "rb") as read:
    x_com_html = read.read()

# Has nextjs (with flight data, having a rscpayload in a list)
# To test recursive search of elements. 
with open(d / "club.fans.html", "rb") as read:
    club_fans_html = read.read()