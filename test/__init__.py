# Has NextJS (with flight data)
with open("test/nextjs.org.html", "rb") as read:
    nextjs_org_html = read.read()

# Has NextJS (with __next_data__)
with open("test/m.soundcloud.com.html", "rb") as read:
    m_soundcloud_com_html = read.read()

# Doesn't have NextJS
with open("test/x.com.html", "rb") as read:
    x_com_html = read.read()