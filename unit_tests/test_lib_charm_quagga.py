import mock

import lib.charm.quagga
import unit_tests.utils as ut_utils


class TestLibCharmQuagga(ut_utils.BaseTestCase):

    def test_get_asn(self):
        self.patch_object(lib.charm.quagga, 'reactive')
        self.patch_object(lib.charm.quagga, 'hookenv')
        bgpserver = mock.Mock()
        bgpserver.generate_asn.return_value = 4200000000
        self.reactive.relations.endpoint_from_name.return_value = bgpserver
        self.hookenv.config.return_value = False
        asn = lib.charm.quagga.get_asn()
        self.assertTrue(self.reactive.relations.endpoint_from_name.called)
        self.assertTrue(self.hookenv.config.called)
        self.assertTrue(bgpserver.generate_asn.called)
        self.assertEqual(asn, 4200000000)

    def test_get_asn_16bit(self):
        self.patch_object(lib.charm.quagga, 'reactive')
        self.patch_object(lib.charm.quagga, 'hookenv')
        bgpserver = mock.Mock()
        bgpserver.generate_asn_16.return_value = 64542
        self.reactive.relations.endpoint_from_name.return_value = bgpserver

        def _mock_config_16(key):
            if key == 'use-16bit-asn':
                return True
            if key == 'asn':
                return False

        self.hookenv.config = _mock_config_16
        asn = lib.charm.quagga.get_asn()
        self.assertTrue(self.reactive.relations.endpoint_from_name.called)
        self.assertTrue(bgpserver.generate_asn_16.called)
        self.assertEqual(asn, 64542)

    def test_get_asn_config(self):
        self.patch_object(lib.charm.quagga, 'reactive')
        self.patch_object(lib.charm.quagga, 'hookenv')
        bgpserver = mock.Mock()
        bgpserver.generate_asn.return_value = 4200000000
        self.reactive.relations.endpoint_from_name.return_value = bgpserver

        def _mock_config_asn(key):
            if key == 'asn':
                return 4200000042

        self.hookenv.config = _mock_config_asn
        asn = lib.charm.quagga.get_asn()
        self.assertTrue(self.reactive.relations.endpoint_from_name.called)
        self.assertTrue(bgpserver.generate_asn.called)
        self.assertEqual(asn, 4200000042)
