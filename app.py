from flask import Flask, Response, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}

SITES = {
    "optimally": "https://optimally.com/garygross/",
    "legalshield": "https://ggross.legalshieldassociate.com/",
    "aspire": "https://workwithaspirepartners.com/id/netspan/",
    "gmg": "https://gmg.me/705075"
}


# -----------------------------
# FULL HTML CLEAN + FIX LINKS
# -----------------------------
def proxy_page(base_url):
    resp = requests.get(base_url, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Fix relative URLs → absolute
    for tag in soup.find_all(["a", "link", "script", "img"]):
        attr = "href" if tag.name in ["a", "link"] else "src"

        if tag.has_attr(attr):
            val = tag[attr]

            if val.startswith("/"):
                tag[attr] = base_url.rstrip("/") + val
            elif val.startswith("//"):
                tag[attr] = "https:" + val

    # Remove nav if exists
    nav = soup.find("nav")
    if nav:
        nav.decompose()

    return str(soup)


# -----------------------------
# GENERIC ROUTE HANDLER
# -----------------------------
@app.route("/<site>")
def serve_site(site):
    if site not in SITES:
        return "Site not found", 404

    html = proxy_page(SITES[site])
    return Response(html, mimetype="text/html")


# -----------------------------
# HOME PAGE
# -----------------------------
@app.route("/")
def home():
    return """
    <!doctype html>
    <html>
    <head>
        <title>My Pages</title>
        <style>
            body { font-family: Arial; padding:40px; }
            a { display:block; margin:10px 0; font-size:20px; }
        </style>
    </head>
    <body>
        <h1>Pages</h1>

        <a href="/optimally">Optimally</a>
        <a href="/legalshield">LegalShield</a>
        <a href="/aspire">Aspire</a>
        <a href="/gmg">GMG</a>

    </body>
    </html>
    """


# -----------------------------
# HEALTH
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
