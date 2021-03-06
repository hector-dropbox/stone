import textwrap
import unittest

from stone.backends.js_client import JavascriptClientBackend
from test.backend_test_util import _mock_output
from stone.ir import Api, ApiNamespace, ApiRoute, Void, Int32
from stone.ir.data_types import Struct

MYPY = False
if MYPY:
    import typing  # noqa: F401 # pylint: disable=import-error,unused-import,useless-suppression


class TestGeneratedJSClient(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(TestGeneratedJSClient, self).__init__(*args, **kwargs)

    def _get_api(self):
        # type () -> Api
        api = Api(version='0.1b1')
        api.route_schema = Struct(u'Route', 'stone_cfg', None)
        route1 = ApiRoute('get_metadata', 1, None)
        route1.set_attributes(None, ':route:`get_metadata`', Void(), Void(), Void(), {})
        route2 = ApiRoute('get_metadata', 2, None)
        route2.set_attributes(None, ':route:`get_metadata:2`', Void(), Int32(), Void(), {})
        ns = ApiNamespace('files')
        ns.add_route(route1)
        ns.add_route(route2)
        api.namespaces[ns.name] = ns
        return api, ns

    def test_route_versions(self):
        # type: () -> None
        api, _ = self._get_api()
        backend = JavascriptClientBackend(
            target_folder_path='output',
            args=['files', '-c', 'DropboxBase'])
        get_result = _mock_output(backend)
        backend.generate(api)
        result = get_result()

        expected = textwrap.dedent('''\
            // Auto-generated by Stone, do not modify.
            var routes = {};

            /**
             * get_metadata
             * @function DropboxBase#filesGetMetadata
             * @arg {void} arg - The request parameters.
             * @returns {Promise.<void, Error.<void>>}
             */
            routes.filesGetMetadata = function (arg) {
              return this.request("files/get_metadata", arg);
            };

            /**
             * get_metadata_v2
             * @function DropboxBase#filesGetMetadataV2
             * @arg {void} arg - The request parameters.
             * @returns {Promise.<number, Error.<void>>}
             */
            routes.filesGetMetadataV2 = function (arg) {
              return this.request("files/get_metadata_v2", arg);
            };

            export { routes };
            ''')
        assert result == expected

    def test_route_with_version_number_conflict(self):
        # type: () -> None
        api, ns = self._get_api()

        # Add a conflicting route
        route3 = ApiRoute('get_metadata_v2', 1, None)
        route3.set_attributes(None, None, Void(), Int32(), Void(), {})
        ns.add_route(route3)

        backend = JavascriptClientBackend(
            target_folder_path='output',
            args=['files', '-c', 'DropboxBase'])

        with self.assertRaises(RuntimeError) as cm:
            backend.generate(api)
            self.assertTrue(str(cm.exception).startswith(
                'There is a name conflict between'))
