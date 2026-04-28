from flask import Flask, Response, redirect, request
import requests
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

app = Flask(__name__)

HEADERS = {"User-Agent": "Mozilla/5.0"}
GMG_URL = "https://gmg.me/705075"


def render_and_clean(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(user_agent=HEADERS["User-Agent"])

        page.goto(url, wait_until="networkidle", timeout=60000)
        html = page.content()

        browser.close()

    soup = BeautifulSoup(html, "html.parser")

    # Remove ugly headers/nav/menus
    for tag in soup.find_all(["header", "nav"]):
        tag.decompose()

    for selector in [
        ".main-nav",
        ".navbar",
        ".nav",
        ".site-header",
        ".header",
        ".top-bar",
        ".skip-link",
        ".skip-to-content",
        "#header",
        "#navbar",
        "#main-nav",
    ]:
        for el in soup.select(selector):
            el.decompose()

    head = soup.find("head")
    if not head:
        head = soup.new_tag("head")
        soup.insert(0, head)

    style = soup.new_tag("style")
    style.string = """
    html, body {
        margin: 0 !important;
        padding: 0 !important;
        height: auto !important;
        overflow: visible !important;
    }

    header, nav, .main-nav, .navbar, .site-header, .top-bar {
        display: none !important;
    }

    * {
        max-width: 100% !important;
    }
    """
    head.append(style)

    return str(soup)


@app.route("/")
def home():
    return redirect("/optimally")


@app.route("/optimally")
def optimally():
    html = render_and_clean("https://optimally.com/garygross/")
    return Response(html, mimetype="text/html")


@app.route("/legalshield")
def legalshield():
    html = render_and_clean("https://ggross.legalshieldassociate.com/")
    return Response(html, mimetype="text/html")


@app.route("/aspire")
def aspire():
    html = render_and_clean("https://workwithaspirepartners.com/id/netspan/")
    return Response(html, mimetype="text/html")


@app.route("/gmg")
def gmg_home():
    return redirect("/gmg-clean")


@app.route("/gmg-clean")
def gmg_clean():
    resp = requests.get(GMG_URL, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    for btn in soup.select(".saveDetails"):
        link = soup.new_tag("a", href="https://gmg.me/activate/705075", role="button")

        for attr in ["class", "id", "style"]:
            if btn.has_attr(attr):
                link[attr] = btn[attr]

        link.append(BeautifulSoup(btn.decode_contents(), "html.parser"))
        btn.replace_with(link)

    return Response(str(soup), mimetype="text/html")


@app.route("/activate/<path:_>")
def activate_redirect(_):
    return redirect("https://gmg.me/activate/705075", code=302)


@app.route("/api/gmg/writeSession")
def gmg_write_session():
    resp = requests.get(
        "https://gmg.me/api/gmg/writeSession",
        params=request.args,
        headers=HEADERS,
        timeout=10
    )

    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/json")
    )


@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
