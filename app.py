from flask import Flask, Response, redirect, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

GMG_URL = "https://gmg.me/705075"

# -------------------------------------------------
# Home → loads the Optimally proxy inside iframe
# -------------------------------------------------
@app.route("/")
def home():
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>Optimally Proxy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            html, body { margin: 0; padding: 0; height: 100%; }
            iframe { width: 100%; height: 2800px; border: none; display: block; }
        </style>
    </head>
    <body>
        <iframe src="/clean-full"></iframe>
    </body>
    </html>
    """

# -------------------------------------------------
# Optimally cleaned version
# -------------------------------------------------
@app.route("/clean-full")
def clean_full():
    url = "https://optimally.com/garygross/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    nav_bar = soup.find("nav", class_="main-nav")
    if nav_bar:
        nav_bar.decompose()

    head = soup.find("head") or soup.new_tag("head")
    body = soup.find("body") or soup.new_tag("body")

    animation_script = soup.new_tag("script", src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js")
    init_script = soup.new_tag("script")
    init_script.string = "AOS.init();"

    body.append(animation_script)
    body.append(init_script)

    html = f"""
    <!doctype html>
    <html lang="en">
    {str(head)}
    {str(body)}
    </html>
    """
    return Response(html, mimetype="text/html")

# -------------------------------------------------
# GMG iframe loader
# -------------------------------------------------
@app.route("/gmg")
def gmg_home():
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>GMG Proxy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            html, body { margin: 0; padding: 0; height: 100%; }
            iframe { width: 100%; height: 100vh; border: none; }
        </style>
    </head>
    <body>
        <iframe src="/gmg-clean" loading="lazy"></iframe>
    </body>
    </html>
    """

# -------------------------------------------------
# GMG cleaned HTML + buttons rewritten
# -------------------------------------------------
@app.route("/gmg-clean")
def gmg_clean():
    resp = requests.get(GMG_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    head = soup.find("head") or soup.new_tag("head")
    body = soup.find("body") or soup.new_tag("body")

    # Replace "saveDetails" buttons with static links
    for btn in soup.select(".saveDetails"):
        link = soup.new_tag("a")
        link["href"] = "https://gmg.me/activate/705075"
        link["role"] = "button"

        if btn.has_attr("class"):
            link["class"] = btn["class"]

        if btn.has_attr("id"):
            link["id"] = btn["id"]

        if btn.has_attr("style"):
            link["style"] = btn["style"]

        inner_html = btn.decode_contents()
        link.append(BeautifulSoup(inner_html, "html.parser"))
        btn.replace_with(link)

    override_style = soup.new_tag("style")
    override_style.string = """
    html, body {
        height: auto !important;
        min-height: 0 !important;
        overflow: visible !important;
        margin: 0;
        padding: 0;
    }
    """
    head.append(override_style)

    final_html = f"<!doctype html>\n<html lang='en'>\n{str(head)}\n{str(body)}\n</html>"
    return Response(final_html, mimetype="text/html")

# -------------------------------------------------
# Redirect all /activate/* links to GMG
# -------------------------------------------------
@app.route("/activate/<path:suffix>")
def gmg_activate(suffix):
    return redirect("https://gmg.me/activate/705075", code=302)

# -------------------------------------------------
# Proxy for GMG Session API
# -------------------------------------------------
@app.route("/api/gmg/writeSession")
def gmg_write_session():
    target_url = "https://gmg.me/api/gmg/writeSession"

    resp = requests.get(
        target_url,
        params=request.args,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=10,
    )

    return Response(
        resp.content,
        status=resp.status_code,
        content_type=resp.headers.get("Content-Type", "application/json")
    )

# -------------------------------------------------
# Healthcheck for Render
# -------------------------------------------------
@app.route("/health")
def health():
    return "OK", 200


if __name__ == "__main__":
    app.run(debug=True)
