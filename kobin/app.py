from typing import Callable, Dict, List, Union
from .static_files import static_file
from .routes import Router, Route
from .server_adapters import servers
from .environs import request, response


class Kobin(object):
    def __init__(self, static_url_path: str= 'static') -> None:
        self.router = Router()

        route = Route('^/{}/(?P<filename>.*)'.format(static_url_path), 'GET', static_file)
        self.router.add(route.rule, 'GET', route)

    def run(self, host: str='', port: int=8000, server: str='wsgiref', **kwargs) -> None:
        try:
            if server in servers:
                server = servers.get(server)
            if isinstance(server, type):
                server = server(host=host, port=port, **kwargs)

            print('Serving on port %d...' % port)
            server.run(self)  # type: ignore
        except KeyboardInterrupt:
            print('Goodbye.')

    def add_route(self, route: Route):
        self.router.add(route.rule, route.method, route)

    def route(self, path: str=None, method: str='GET',
              callback: Callable[..., str]=None) -> Callable[..., Union[str, bytes]]:
        def decorator(callback_func):
            route = Route(path, method, callback_func)
            self.add_route(route)
            return callback_func
        return decorator(callback) if callback else decorator

    def _handle(self, environ: Dict) -> Union[str, bytes]:
        route, kwargs = self.router.match(environ)
        environ['kobin.app'] = self
        request.bind(environ)  # type: ignore
        response.bind()        # type: ignore
        return route.call(**kwargs) if kwargs else route.call()

    def wsgi(self, environ: Dict, start_response) -> List[bytes]:
        out = self._handle(environ)
        if isinstance(out, str):
            out = out.encode('utf-8')
        start_response(response._status_line, response.headerlist)
        return [out]

    def __call__(self, environ: Dict, start_response) -> List[bytes]:
        """It is called when receive http request."""
        return self.wsgi(environ, start_response)
