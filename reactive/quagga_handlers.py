# Copyright 2018 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import charmhelpers.core as ch_core
import charmhelpers.core.sysctl as ch_core_sysctl
import charmhelpers.core.templating as ch_core_templating
import charmhelpers.contrib.network.ip as ch_net_ip
import charms.reactive as reactive
import charm.quagga as quagga
import copy


@reactive.when_not('quagga.started')
def start_quagga():
    ch_core_sysctl.create("{'net.ipv4.ip_forward': 1}",
                          '/etc/sysctl.d/42-charm-quagga.conf')
    ch_core_templating.render('daemons', '/etc/quagga/daemons', {},
                              owner='quagga', group='quagga', perms=0o640)
    ch_core_templating.render('zebra.conf', '/etc/quagga/zebra.conf', {},
                              owner='quagga', group='quagga', perms=0o640)
    ch_core_templating.render('bgpd.conf', '/etc/quagga/bgpd.conf', {},
                              owner='quagga', group='quagga', perms=0o640)
    quagga.restart_services()

    # Perform basic BGP configuration
    quagga.vtysh(
        ['conf t',
         'router bgp {}'.format(quagga.get_asn()),
         'bgp router-id {}'.format(
             ch_core.hookenv.unit_get('private-address')
             ),
         'redistribute connected',
         'exit',
         'exit',
         'write',
         ]
        )

    ch_core.hookenv.status_set('active', 'Ready (AS Number {})'
                               .format(quagga.get_asn()))
    reactive.set_state('quagga.started')


@reactive.when_any('endpoint.bgpserver.joined', 'endpoint.bgpclient.joined')
def publish_bgp_info():
    for endpoint in (
            reactive.relations.endpoint_from_flag('endpoint.bgpserver.joined'),
            reactive.relations.endpoint_from_flag('endpoint.bgpclient.joined'),
            ):
        endpoint.publish_info(
                asn=quagga.get_asn(),
                bindings=ch_core.hookenv.metadata()['extra-bindings'])


@reactive.when_any('endpoint.bgpserver.changed', 'endpoint.bgpclient.changed')
def bgp_relation_changed():
    for endpoint in (
            reactive.relations.endpoint_from_flag(
                'endpoint.bgpserver.changed'),
            reactive.relations.endpoint_from_flag(
                'endpoint.bgpclient.changed'),
            ):
        for entry in endpoint.get_received_info():
            ch_core.hookenv.log("DEBUG: received info: '{}'".format(entry))
            if len(entry['links']):
                # configure BGP neighbours on extra-bindings interfaces
                for link in entry['links']:
                    configure_link(entry, link['remote'])
            else:
                # configure BGP neighbour on relation interface
                relation_addr = ch_core.hookenv.relation_get(
                        attribute='private-address',
                        unit=entry['remote_unit_name'],
                        rid=entry['relation_id'])
                configure_link(entry, relation_addr)


def configure_link(bgp_info, remote_addr):
    CONF_ROUTER_BGP = ['conf t', 'router bgp {}'.format(quagga.get_asn())]
    EXIT_ROUTER_BGP_WRITE = ['exit', 'exit', 'write']

    vtysh_cmd = copy.deepcopy(CONF_ROUTER_BGP)
    ch_core.hookenv.log(
            'DEBUG: configure neighbour {} '
            'remote-as {}'
            ''.format(remote_addr, bgp_info['asn']))
    vtysh_cmd += ['neighbor {} remote-as {}'
                  ''.format(remote_addr, bgp_info['asn'])]
    if bgp_info['passive']:
        vtysh_cmd += ['neighbor {} passive'
                      ''.format(remote_addr)]
    if ch_net_ip.is_ipv6(remote_addr):
        vtysh_cmd += ['no neighbor {} activate'.format(remote_addr),
                      'address-family ipv6',
                      # workaround for quagga redistribute connected
                      # not working as expected for IPv6
                      'network {}'.format(
                          ch_net_ip.resolve_network_cidr(remote_addr)),
                      'neighbor {} activate'.format(remote_addr),
                      'exit',
                      ]
    # Exit and write
    vtysh_cmd += EXIT_ROUTER_BGP_WRITE
    # Execute the command
    quagga.vtysh(vtysh_cmd)
