from typing import Callable, Dict, List
from .routes import Router, Route
from .server_adapters import servers


class Kobin(object):
    def __init__(self):
        self.router = Router()

    def run(self, host: str='', port: int=8000, server: str='wsgiref', **kwargs):
        try:
            if server in servers:
                server = servers.get(server)
            if isinstance(server, type):
                server = server(host=host, port=port, **kwargs)

            server.run(self)
            print('Serving on port %d...' % port)
        except KeyboardInterrupt:
            print('Goodbye.')

    def add_route(self, route: Route):
        self.router.add(route.rule, route.method, route)

    def route(self, path: str=None, method: str='GET',
              callback: Callable[..., str]=None) -> Callable[..., str]:
        def decorator(callback_func):
            route = Route(path, method, callback_func)
            self.add_route(route)
            return callback_func
        return decorator(callback) if callback else decorator

    def _handle(self, environ: Dict):
        route, args = self.router.match(environ)
        return route.call(*args)

    def wsgi(self, environ: Dict, start_response) -> List[str]:
        out = self._handle(environ)
        if isinstance(out, str):
            out = out.encode('utf-8')
        start_response('200 OK', [('Content-Type', 'text/html')])
        return [out]

    def __call__(self, environ: Dict, start_response) -> List[str]:
        """It is called when receive http request."""
        return self.wsgi(environ, start_response)
