from flask import Flask, Response, redirect, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}

OPTIMALLY_URL = "https://optimally.com/garygross/"
LEGALSHIELD_URL = "https://ggross.legalshieldassociate.com/"
ASPIRE_URL = "https://workwithaspirepartners.com/id/netspan/"
GMG_URL = "https://gmg.me/705075"


def proxy_clean_page(url):
    response = requests.get(url, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    nav_bar = soup.find("nav", class_="main-nav")
    if nav_bar:
        nav_bar.decompose()

    head = soup.find("head") or soup.new_tag("head")
    body = soup.find("body") or soup.new_tag("body")

    style = soup.new_tag("style")
    style.string = """
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        width: 100% !important;
        min-height: 100% !important;
        overflow: visible !important;
    }
    """
    head.append(style)

    return f"""
    <!doctype html>
    <html lang="en">
    {str(head)}
    {str(body)}
    </html>
    """


def iframe_page(title, iframe_src, height="2800px"):
    return f"""
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>{title}</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            html, body {{
                margin: 0;
                padding: 0;
                height: 100%;
            }}
            iframe {{
                width: 100%;
                height: {height};
                border: none;
                display: block;
            }}
        </style>
    </head>
    <body>
        <iframe src="{iframe_src}"></iframe>
    </body>
    </html>
    """


@app.route("/")
def home():
    return """
    <!doctype html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Proxy Server</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                padding: 40px;
            }
            a {
                display: block;
                margin: 12px 0;
                font-size: 20px;
            }
        </style>
    </head>
    <body>
        <h1>Proxy Pages</h1>
        <a href="/optimally-page">Optimally Page</a>
        <a href="/legalshield-page">LegalShield Page</a>
        <a href="/aspire-page">Aspire Partners Page</a>
        <a href="/gmg">GMG Page</a>
    </body>
    </html>
    """


# -----------------------------
# Optimally
# -----------------------------
@app.route("/optimally-page")
def optimally_page():
    return iframe_page("Optimally Proxy", "/optimally")


@app.route("/optimally")
def optimally_clean():
    html = proxy_clean_page(OPTIMALLY_URL)
    return Response(html, mimetype="text/html")


# -----------------------------
# LegalShield
# -----------------------------
@app.route("/legalshield-page")
def legalshield_page():
    return iframe_page("LegalShield Proxy", "/legalshield")


@app.route("/legalshield")
def legalshield_clean():
    html = proxy_clean_page(LEGALSHIELD_URL)
    return Response(html, mimetype="text/html")


# -----------------------------
# Aspire Partners
# -----------------------------
@app.route("/aspire-page")
def aspire_page():
    return iframe_page("Aspire Partners Proxy", "/aspire")


@app.route("/aspire")
def aspire_clean():
    html = proxy_clean_page(ASPIRE_URL)
    return Response(html, mimetype="text/html")


# -----------------------------
# GMG
# -----------------------------
@app.route("/gmg")
def gmg_home():
    return iframe_page("GMG Proxy", "/gmg-clean", "100vh")


@app.route("/gmg-clean")
def gmg_clean():
    response = requests.get(GMG_URL, headers=HEADERS, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    for btn in soup.select(".saveDetails"):
        link = soup.new_tag("a")
        link["href"] = "https://gmg.me/activate/705075"
        link["role"] = "button"

        for attr in ["class", "id", "style"]:
            if btn.has_attr(attr):
                link[attr] = btn[attr]

        link.append(BeautifulSoup(btn.decode_contents(), "html.parser"))
        btn.replace_with(link)

    return Response(str(soup), mimetype="text/html")


@app.route("/activate/<path:suffix>")
def gmg_activate(suffix):
    return redirect("https://gmg.me/activate/705075", code=302)


@app.route("/api/gmg/writeSession")
def gmg_write_session():
    target_url = "https://gmg.me/api/gmg/writeSession"

    response = requests.get(
        target_url,
        params=request.args,
        headers=HEADERS,
        timeout=10,
    )

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers.get("Content-Type", "application/json"),
    )


# -----------------------------
# Health Check
# -----------------------------
@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
