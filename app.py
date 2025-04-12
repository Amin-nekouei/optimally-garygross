from flask import Flask, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <iframe src="/clean-full" width="100%" height="1500" style="border:none;"></iframe>
    '''

@app.route('/clean-full')
def clean_full():
    url = "https://optimally.com/garygross/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # ✅ KEEP header — do NOT remove it

    # ❌ Only remove the "Contact Us" <li> from the header nav
    contact_us_menu = soup.find('li', {'id': 'menu-item-24'})
    if contact_us_menu:
        contact_us_menu.decompose()

    # ✅ Keep all other content (body, footer, layout)
    head = soup.find('head')
    body = soup.find('body')

    # ✅ Add AOS script if needed for animations
    animation_script = soup.new_tag("script", src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js")
    init_script = soup.new_tag("script")
    init_script.string = "AOS.init();"
    body.append(animation_script)
    body.append(init_script)

    # ✅ Assemble the clean page
    html = f"""
    <html lang="en">
    {str(head)}
    {str(body)}
    </html>
    """
    return Response(html, mimetype='text/html')


if __name__ == '__main__':
    app.run(debug=True)
