from flask import Flask, Response
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/')
def home():
    return '''
        <h2>Optimally Cleaned Page (No Header/Footer)</h2>
        <iframe src="/clean-full" width="100%" height="3500" style="border:none;"></iframe>
    '''

@app.route('/clean-full')
def clean_full():
    url = "https://optimally.com/garygross/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Remove header and footer from the soup
    if soup.find('header'):
        soup.find('header').decompose()


    # Keep head as-is
    head = soup.find('head')
    body = soup.find('body')

    # Add fallback script for animations (in case not included)
    animation_script = soup.new_tag("script", src="https://cdn.jsdelivr.net/npm/aos@2.3.4/dist/aos.js")
    init_script = soup.new_tag("script")
    init_script.string = "AOS.init();"
    body.append(animation_script)
    body.append(init_script)

    html = f"""
    <html lang="en">
    {str(head)}
    {str(body)}
    </html>
    """
    return Response(html, mimetype='text/html')


if __name__ == '__main__':
    app.run(debug=True)
