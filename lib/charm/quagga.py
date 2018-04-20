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
import subprocess
from charmhelpers.core import (
    hookenv,
    host,
)
import charms.reactive as reactive

# Quagga services based on Ubuntu Release
QUAGGA_SERVICES = {
    'xenial': ['quagga'],
    'bionic': ['zebra', 'bgpd'],
}


def get_asn():
    # Get bgp interface to generate our AS Number
    bgpserver = reactive.relations.endpoint_from_name('bgpserver')
    return hookenv.config('asn') or bgpserver.generate_asn()


def vtysh(args):
    cmds = ['/usr/bin/vtysh']
    for arg in args:
        cmds.append('-c')
        cmds.append(arg)
    output = subprocess.check_output(cmds)
    return output


def restart_services():
    """Determine which service names are required to be restarted based on
    Ubuntu release and restart them.
    """
    ubuntu_release = host.lsb_release()['DISTRIB_CODENAME']
    for service in QUAGGA_SERVICES[ubuntu_release]:
        host.service('restart', service)
