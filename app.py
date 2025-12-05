from flask import Flask, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# --------- 1) صفحه Optimally (Gary Gross)  --------- #

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


@app.route('/clean-full')
def clean_full():
    url = "https://optimally.com/garygross/"
    response = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')

    nav_bar = soup.find('nav', class_='main-nav')
    if nav_bar:
        nav_bar.decompose()

    head = soup.find('head')
    body = soup.find('body')


    if head is None:
        head = soup.new_tag("head")
    if body is None:
        body = soup.new_tag("body")

  
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


# --------- 2) صفحه GMG (Tax Credit Calculator)  --------- #

GMG_URL = "https://gmg.me/705075"


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


@app.route('/gmg-clean')
def gmg_clean():
    resp = requests.get(GMG_URL, headers={"User-Agent": "Mozilla/5.0"})
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # header = soup.find("header", class_="welcome-header")
    # if header:
    #     header.decompose()
    # footer = soup.find("footer", class_="welcome-footer")
    # if footer:
    #     footer.decompose()

    head = soup.find("head")
    body = soup.find("body")

    if head is None:
        head = soup.new_tag("head")
    if body is None:
        body = soup.new_tag("body")

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
    
@app.route('/health')
def health():
    return "OK", 200

if __name__ == '__main__':
    app.run(debug=True)
