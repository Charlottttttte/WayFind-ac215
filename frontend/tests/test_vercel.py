"""Exercise the actual Vercel handler through HTTP, with no deployment needed."""
import json
import os
import sys
import threading
import unittest
from http.server import ThreadingHTTPServer
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError
from urllib.request import Request, urlopen

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from api.search import handler
from test_server import Upstream


class VercelTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.url = f'http://127.0.0.1:{self.server.server_port}/api/search'

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()

    def request(self):
        return Request(self.url, data=b'{"query":"ML","top_k":5}', headers={'Content-Type':'application/json'})

    def test_no_upstream_is_explicit(self):
        with patch.dict(os.environ, {'SEARCH_API_URL':''}):
            with self.assertRaises(HTTPError) as error:
                urlopen(self.request())
            self.assertEqual(error.exception.code, 503)
            self.assertEqual(json.load(error.exception)['code'], 'SEARCH_NOT_CONFIGURED')

    def test_configured_upstream_is_forwarded(self):
        upstream = ThreadingHTTPServer(('127.0.0.1', 0), Upstream)
        upstream.status = 200
        upstream.body = b'{"results":[],"dataset_version":"vercel-adapter-stub"}'
        thread = threading.Thread(target=upstream.serve_forever, daemon=True)
        thread.start()
        try:
            with patch.dict(os.environ, {'SEARCH_API_URL':f'http://127.0.0.1:{upstream.server_port}/search'}):
                with urlopen(self.request()) as response:
                    self.assertEqual(json.load(response)['dataset_version'], 'vercel-adapter-stub')
                self.assertEqual(upstream.payload, {'query':'ML','top_k':5})
        finally:
            upstream.shutdown()
            upstream.server_close()
            thread.join()

    def test_get_does_not_expose_assets_or_source(self):
        with self.assertRaises(HTTPError) as error:
            urlopen(self.url)
        self.assertEqual(error.exception.code, 405)
