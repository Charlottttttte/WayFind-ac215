import json
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from server import make_server


class Upstream(BaseHTTPRequestHandler):
    def do_POST(self):
        self.server.payload = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        self.send_response(self.server.status)
        self.end_headers()
        self.wfile.write(self.server.body)

    def log_message(self, *args):
        pass


class FrontendTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.upstream = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        cls.frontend = make_server(port=0, search_api_url=f'http://127.0.0.1:{cls.upstream.server_port}/search')
        cls.threads = []
        for server in [cls.upstream, cls.frontend]:
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            cls.threads.append(thread)
        cls.url = f'http://127.0.0.1:{cls.frontend.server_port}'

    @classmethod
    def tearDownClass(cls):
        for server in [cls.frontend, cls.upstream]:
            server.shutdown()
            server.server_close()
        for thread in cls.threads:
            thread.join()

    def setUp(self):
        self.upstream.status = 200
        self.upstream.body = b'{"results":[],"dataset_version":"stub-v1"}'

    def post(self, payload):
        return urlopen(Request(self.url + '/search', data=json.dumps(payload).encode(), headers={'Content-Type':'application/json'}), timeout=3)

    def test_serves_assets_but_not_private_files(self):
        for path in ['/', '/app.js', '/api.mjs', '/style.css', '/health']:
            with urlopen(self.url + path) as response:
                self.assertEqual(response.status, 200)
        for path in ['/server.py', '/.env', '/../server.py']:
            with self.assertRaises(HTTPError) as error:
                urlopen(self.url + path)
            self.assertEqual(error.exception.code, 404)

    def test_forwards_query_and_preserves_version(self):
        with self.post({'query':'ML','top_k':5,'url':'https://untrusted.example'}) as response:
            self.assertEqual(json.load(response), {'results':[], 'dataset_version':'stub-v1'})
        self.assertEqual(self.upstream.payload, {'query':'ML','top_k':5})

    def test_bad_queries(self):
        for payload in [{}, {'query':' '}, {'query':'x','top_k':False}, {'query':'x','top_k':21}]:
            with self.assertRaises(HTTPError) as error:
                self.post(payload)
            self.assertEqual(error.exception.code, 400)

    def test_upstream_failures_are_not_success(self):
        for status, body in [(500,b'private detail'),(200,b'not json'),(200,b'{"wrong":[]}')]:
            self.upstream.status, self.upstream.body = status, body
            with self.assertRaises(HTTPError) as error:
                self.post({'query':'ML'})
            self.assertEqual(error.exception.code, 502)
            self.assertNotIn(b'private detail', error.exception.read())

    def test_unreachable_backend(self):
        original = self.frontend.search_api_url
        # The frontend itself gives 404 for this path, exercising upstream HTTP failure.
        self.frontend.search_api_url = self.url + '/missing'
        try:
            with self.assertRaises(HTTPError) as error:
                self.post({'query':'ML'})
            self.assertEqual(error.exception.code, 502)
        finally:
            self.frontend.search_api_url = original


if __name__ == '__main__':
    unittest.main()
