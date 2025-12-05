from flask import Flask, Response
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

app = Flask(__name__)

# ============================================================================
# 1) HOMEPAGE → loads Optimally (Gary Gross) inside an iframe
# ============================================================================

@app.route('/')
def home():
    return '''
        <!doctype html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>Optimally Proxy</title>
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <style>
                html, body {
                    margin: 0;
                    padding: 0;
                    height: 100%;
                }
                iframe {
                    width: 100%;
                    height: 2800px;
                    border: none;
                    display: block;
                }
            </style>
        </head>
        <body>
            <iframe src="/clean-full"></iframe>
        </body>
        </html>
    '''


# ============================================================================
# 2) Proxy for Optimally page (Gary Gross)
# Removes navigation and adds AOS animations
# ============================================================================

@app.route('/clean-full')
def clean_full():
    url = "https://optimally.com/garygross/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove the main nav bar
    nav_bar = soup.find('nav', class_='main-nav')
    if nav_bar:
        nav_bar.decompose()

    # Ensure head/body exist
    head = soup.find('head') or soup.new_tag("head")
    body = soup.find('body') or soup.new_tag("body")

    # Add AOS animation support
    animation_script = soup.new_tag(
        "script",
        src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js"
    )
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
    return Response(html, mimetype='text/html')


# ============================================================================
# 3) GMG TAX CALCULATOR PAGE (Iframe wrapper)
# ============================================================================

GMG_URL = "https://gmg.me/705075"
GMG_BASE = "https://gmg.me"


@app.route('/gmg')
def gmg_home():
    return """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>GMG Proxy</title>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            html, body {
                margin: 0;
                padding: 0;
                height: 100%;
            }
            .frame-wrapper {
                width: 100%;
                height: 100vh;
            }
            iframe {
                width: 100%;
                height: 100%;
                border: none;
                display: block;
            }
        </style>
    </head>
    <body>
        <div class="frame-wrapper">
            <iframe src="/gmg-clean" loading="lazy"></iframe>
        </div>
    </body>
    </html>
    """


# ============================================================================
# 4) GMG CLEAN HTML (Fix relative CSS/JS paths + preserve full layout)
# ============================================================================

@app.route('/gmg-clean')
def gmg_clean():
    resp = requests.get(GMG_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Ensure head/body exist
    head = soup.find("head") or soup.new_tag("head")
    body = soup.find("body") or soup.new_tag("body")

    # Fix relative paths for CSS, JS, IMG → convert to absolute URLs
    for tag in soup.find_all(["link", "script", "img"]):
        attr = "href" if tag.name == "link" else "src"
        url = tag.get(attr)
        if not url:
            continue

        # Skip if already absolute
        if url.startswith("http://") or url.startswith("https://") or url.startswith("//"):
            continue

        # Convert relative → absolute
        tag[attr] = urljoin(GMG_BASE, url)

    # Override styling to avoid layout breakdown inside iframe
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

    html = f"<!doctype html>\n<html lang='en'>\n{str(head)}\n{str(body)}\n</html>"
    return Response(html, mimetype="text/html")


# ============================================================================
# 5) HEALTH CHECK ENDPOINT (Required for Render Uptime)
# ============================================================================

@app.route('/health')
def health():
    return "OK", 200


# ============================================================================
# 6) LOCAL DEBUG MODE
# ============================================================================

if __name__ == '__main__':
    app.run(debug=True)
