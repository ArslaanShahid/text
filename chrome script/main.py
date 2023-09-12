from flask import Flask, render_template, request, jsonify
from helpers import getWebBodyWithChrome, extractMainText, getPageTitle
import validators

app = Flask(__name__)

#send response as json for api
def sendJSON(msg, status, data = {}):
    return  jsonify({
        'msg' : msg,
        'status' : 'success' if status == 200 else 'failed',
        'data' : data
    }), status

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/scrape', methods=["POST"])
def scrape():
    post = request.get_json()
    outputFormat = "txt"

    # Validating post body

    # if url is empty or invalid url
    if not post['url'] or not validators.url(post['url']):
        return sendJSON('Invalid URL', 400)

    # scrape web page and extract main content
    # check if client has asked to use chrome
    try:
        webBody = getWebBodyWithChrome(post['url'])
    except Exception as e:
        return sendJSON(str(e) , 500)

    output = extractMainText(body=webBody, formatting=outputFormat)

    data = {
        'output' : output,
    }

    return sendJSON(msg='Success', status=200, data=data)


if __name__ == '__main__':
    app.run(debug=False)
