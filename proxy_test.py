import re
from contextlib import closing
import requests

from flask import Flask
from flask import request
from flask import Response
import argparse

app = Flask(__name__)
global host

@app.before_request
def before_request():
    entry_url = request.url
    global host
    host_url = 'http://{}/'.format(host)
    export_url = re.sub('http://(.*?)/', host_url, entry_url)
    
    method = request.method
    data = request.data or request.form or None

    headers = dict()
    for name, value in request.headers:
        if not value or name in ['Cache-Control', 'Host']:
            continue
        headers[name] = value
    with closing(requests.request(method, export_url, headers=headers, data=data, stream=True)) as r:
        resp_headers = []
        for name, value in r.headers.items():
            if name.lower() in ('content-length', 'connection','content-encoding'):
                continue
            resp_headers.append((name, value))
        return Response(r.content, status=r.status_code, headers=resp_headers)


@app.route('/index')
def index():
    return 'Error page'

def main(args):
    global host
    host = args.host
    app.run(host='0.0.0.0')

def init_args():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--host', help='the host you want acctact')
    args = parser.parse_args()
    return args
    
if __name__ == "__main__":
    args = init_args()
    main(args)