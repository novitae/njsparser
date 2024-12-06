# Has NextJS (with recent flight data)
with open("test/nextjs.org.html", "rb") as read:
    nextjs_org_html = read.read()

# Has NextJS (with older flight data) and custom prefix to static paths
# https://swag.live/user/624dc255c12744f2fdaf90c8
with open("test/swag.live.html", "rb") as read:
    swag_live_html = read.read()

# Build manifest from nextjs (function)
with open("test/nextjs_org_4mSOwJptzzPemGzzI8AOo_buildManifest.js", "r") as read:
    nextjs_org_4mSOwJptzzPemGzzI8AOo_buildManifest = read.read()

# Build manifest from swag.live (function)
with open("test/swag_live_giz3a1H7OUzfxgxRHIdMx_buildManifest.js", "r") as read:
    swag_live_giz3a1H7OUzfxgxRHIdMx_buildManifest = read.read()

# Build manifest from app.osint.industries (not function)
with open("test/app_osint_industries_yAzR27j6CjHLWW3VxUzzi_buildManifest.js", "r") as read:
    app_osint_industries_yAzR27j6CjHLWW3VxUzzi_buildManifest = read.read()

# Has NextJS (with __next_data__)
with open("test/m.soundcloud.com.html", "rb") as read:
    m_soundcloud_com_html = read.read()

# Doesn't have NextJS
with open("test/x.com.html", "rb") as read:
    x_com_html = read.read()
