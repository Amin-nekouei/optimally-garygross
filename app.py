from flask import Flask, Response, redirect, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# -----------------------------
# Constants
# -----------------------------
HEADERS = {"User-Agent": "Mozilla/5.0"}
GMG_URL = "https://gmg.me/705075"

# -----------------------------
# Helper: fetch + clean page
# -----------------------------
def fetch_and_clean(url, remove_nav=True):
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Remove nav if exists
    if remove_nav:
        nav = soup.find("nav", class_="main-nav")
        if nav:
            nav.decompose()

    head = soup.find("head") or soup.new_tag("head")
    body = soup.find("body") or soup.new_tag("body")

    # Add animation script (optional)
    animation_script = soup.new_tag(
        "script",
        src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"
    )
    init_script = soup.new_tag("script")
    init_script.string = "AOS.init();"

    body.append(animation_script)
    body.append(init_script)

    return f"""
    <!doctype html>
    <html lang="en">
    {str(head)}
    {str(body)}
    </html>
    """

# -----------------------------
# Home (navigation UI)
# -----------------------------
@app.route("/")
def home():
    return """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Landing Pages</title>
        <style>
            body { margin: 0; font-family: Arial, sans-serif; }
            .nav {
                position: fixed;
                top: 0;
                left: 0;
                right: 0;
                background: #111;
                padding: 12px;
                z-index: 1000;
            }
            .nav a {
                color: white;
                margin-right: 20px;
                text-decoration: none;
                font-weight: bold;
            }
            iframe {
                margin-top: 50px;
                width: 100%;
                height: 2800px;
                border: none;
            }
        </style>
    </head>
    <body>

        <div class="nav">
            <a href="/optimally" target="frame">Optimally</a>
            <a href="/legalshield" target="frame">LegalShield</a>
            <a href="/aspire" target="frame">Aspire</a>
            <a href="/gmg" target="frame">GMG</a>
        </div>

        <iframe name="frame" src="/optimally"></iframe>

    </body>
    </html>
    """

# -----------------------------
# Optimally
# -----------------------------
@app.route("/optimally")
def optimally():
    html = fetch_and_clean("https://optimally.com/garygross/")
    return Response(html, mimetype="text/html")

# -----------------------------
# LegalShield
# -----------------------------
@app.route("/legalshield")
def legalshield():
    html = fetch_and_clean("https://ggross.legalshieldassociate.com/")
    return Response(html, mimetype="text/html")

# -----------------------------
# Aspire Partners
# -----------------------------
@app.route("/aspire")
def aspire():
    html = fetch_and_clean("https://workwithaspirepartners.com/id/netspan/")
    return Response(html, mimetype="text/html")

# -----------------------------
# GMG iframe page
# -----------------------------
@app.route("/gmg")
def gmg_home():
    return """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>GMG Proxy</title>
        <style>
            html, body { margin: 0; height: 100%; }
            iframe { width: 100%; height: 100vh; border: none; }
        </style>
    </head>
    <body>
        <iframe src="/gmg-clean"></iframe>
    </body>
    </html>
    """

# -----------------------------
# GMG cleaned page
# -----------------------------
@app.route("/gmg-clean")
def gmg_clean():
    resp = requests.get(GMG_URL, headers=HEADERS)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Replace buttons
    for btn in soup.select(".saveDetails"):
        link = soup.new_tag("a", href="https://gmg.me/activate/705075", role="button")

        for attr in ["class", "id", "style"]:
            if btn.has_attr(attr):
                link[attr] = btn[attr]

        link.append(BeautifulSoup(btn.decode_contents(), "html.parser"))
        btn.replace_with(link)

    head = soup.find("head") or soup.new_tag("head")

    # Fix scrolling issues
    style = soup.new_tag("style")
    style.string = """
    html, body {
        height: auto !important;
        overflow: visible !important;
        margin: 0;
    }
    """
    head.append(style)

    return Response(str(soup), mimetype="text/html")

# -----------------------------
# Redirect /activate
# -----------------------------
@app.route("/activate/<path:_>")
def activate_redirect(_):
    return redirect("https://gmg.me/activate/705075", code=302)

# -----------------------------
# GMG API Proxy
# -----------------------------
@app.route("/api/gmg/writeSession")
def gmg_write_session():
    target = "https://gmg.me/api/gmg/writeSession"

    resp = requests.get(
        target,
        params=request.args,
        headers=HEADERS,
        timeout=10
    )

    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/json")
    )

# -----------------------------
# Health check
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200

# -----------------------------
# Run
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
