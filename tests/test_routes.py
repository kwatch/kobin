from unittest import TestCase
from kobin.routes import Route, Router


class RouteTests(TestCase):
    def test_call(self):
        def dummy_func(num: int) -> None:
            return num
        route = Route('/hoge', 'GET', dummy_func)
        self.assertEqual(route.call(**{'num': 1}), 1)


class RouterTests(TestCase):
    def setUp(self):
        self.router = Router()

    def test_match_static_routes(self):
        def target_func():
            pass
        self.router.add('^/tests/$', 'GET', target_func)
        test_env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/tests/'}
        actual_target, actual_args = self.router.match(test_env)

        self.assertEqual(actual_target, target_func)
        self.assertEqual(actual_args, {})

    def test_match_dynamic_routes_with_numbers(self):
        def target_func():
            pass
        self.router.add('^/tests/(?P<year>\d{4})/$', 'GET', target_func)
        test_env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/tests/2015/'}
        actual_target, actual_args = self.router.match(test_env)

        self.assertEqual(actual_target, target_func)
        self.assertEqual(actual_args, {'year': '2015'})

    def test_match_dynamic_routes_with_string(self):
        def target_func():
            pass
        self.router.add('^/tests/(?P<name>\w+)/$', 'GET', target_func)
        test_env = {'REQUEST_METHOD': 'GET', 'PATH_INFO': '/tests/kobin/'}
        actual_target, actual_args = self.router.match(test_env)

        self.assertEqual(actual_target, target_func)
        self.assertEqual(actual_args, {'name': 'kobin'})
