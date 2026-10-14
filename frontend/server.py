"""MS2 local/demo frontend server and fixed-destination search proxy."""
import json
import mimetypes
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

STATIC = Path(__file__).parent / 'static'
ASSETS = {'/': 'index.html', '/index.html': 'index.html', '/style.css': 'style.css',
          '/app.js': 'app.js', '/api.mjs': 'api.mjs', '/mock.mjs': 'mock.mjs'}
MAX_REQUEST = 16_384
MAX_RESPONSE = 2_000_000


class Handler(BaseHTTPRequestHandler):
    # A fixed allowlist serves public assets only (never configuration/source/tests).
    def reply(self, status, body, content_type='application/json'):
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(body)

    def error(self, status, message):
        self.reply(status, json.dumps({'error': message}).encode())

    def do_GET(self):
        path = self.path.split('?', 1)[0]
        if path == '/health':
            return self.reply(200, b'{"status":"ok","component":"frontend"}')
        asset = ASSETS.get(path)
        if not asset:
            return self.error(404, 'Not found')
        content_type = 'text/javascript' if asset.endswith(('.js', '.mjs')) else mimetypes.guess_type(asset)[0]
        self.reply(200, (STATIC / asset).read_bytes(), content_type + '; charset=utf-8')

    def do_POST(self):
        if self.path != '/search':
            return self.error(404, 'Not found')
        if self.headers.get_content_type() != 'application/json':
            return self.error(415, 'Expected application/json')
        try:
            length = int(self.headers.get('Content-Length', '0'))
        except ValueError:
            return self.error(400, 'Invalid content length')
        if not 0 < length <= MAX_REQUEST:
            return self.error(413, 'Invalid request size')
        try:
            data = json.loads(self.rfile.read(length))
        except (ValueError, UnicodeDecodeError):
            return self.error(400, 'Invalid JSON')
        if not isinstance(data, dict) or not isinstance(data.get('query'), str) or not data['query'].strip():
            return self.error(400, 'A nonempty query is required')
        top_k = data.get('top_k', 5)
        if type(top_k) is not int or not 1 <= top_k <= 20:
            return self.error(400, 'top_k must be an integer from 1 to 20')
        # Only configuration chooses the upstream; browser input cannot choose a URL.
        url = getattr(self.server, 'search_api_url', os.getenv('SEARCH_API_URL', ''))
        if not url:
            return self.reply(503, b'{"code":"SEARCH_NOT_CONFIGURED","error":"Live search is not connected yet"}')
        from urllib.parse import urlparse
        if urlparse(url).scheme not in ('http', 'https'):
            return self.error(503, 'Search service is not configured correctly')
        request = Request(url, data=json.dumps({'query': data['query'], 'top_k': top_k}).encode(),
                          headers={'Content-Type': 'application/json', 'Accept': 'application/json'}, method='POST')
        try:
            with urlopen(request, timeout=12) as response:
                raw = response.read(MAX_RESPONSE + 1)
                if len(raw) > MAX_RESPONSE:
                    return self.error(502, 'Search response is too large')
                parsed = json.loads(raw)
                if not isinstance(parsed, dict) or not isinstance(parsed.get('results'), list):
                    return self.error(502, 'Invalid search response')
                self.reply(200, json.dumps(parsed).encode())
        except HTTPError as exc:
            self.error(503 if exc.code == 429 else 502, 'Search service rejected the request')
        except (TimeoutError, URLError, OSError):
            self.error(503, 'Search service unavailable')
        except (ValueError, UnicodeDecodeError):
            self.error(502, 'Search service returned invalid JSON')


def make_server(host='127.0.0.1', port=8080, search_api_url='http://127.0.0.1:8000/search'):
    from urllib.parse import urlparse
    if urlparse(search_api_url).scheme not in ('http', 'https'):
        raise ValueError('SEARCH_API_URL must be an HTTP(S) URL')
    server = ThreadingHTTPServer((host, port), Handler)
    server.search_api_url = search_api_url
    return server


if __name__ == '__main__':
    host = os.getenv('HOST', '127.0.0.1')
    port = int(os.getenv('PORT', '8080'))
    server = make_server(host, port, os.getenv('SEARCH_API_URL', 'http://127.0.0.1:8000/search'))
    print(f'WayFind frontend: http://{host}:{server.server_port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
