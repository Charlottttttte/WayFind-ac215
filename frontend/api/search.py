"""Vercel adapter: reuse the locally tested search proxy without a persistent server."""
from server import Handler


class handler(Handler):
    def do_GET(self):
        self.error(405, 'Use POST for search')

    def do_POST(self):
        # Vercel maps /api/search here; vercel.json also rewrites /search here.
        self.path = '/search'
        super().do_POST()
