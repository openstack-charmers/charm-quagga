# Overview
Testing and developing code for use in advanced networking topologies can be
challenging without a test environment.

Establishing a physical network in CLOS Topology with a Layer 3-Only design
is no exception.

Utilizing Juju, MAAS and this charm you can spin up your own virtual
environment in no time.

                    +----------+   +----------+
                    |  spine0  |   |  spine1  |
                    +----------+   +----------+
                      /   \    \     /  /   \
                     /     \    \___/__/_    \
                    /      _\______/  /  \    \
                   /      /  \       /    \    \
                  /      /    \     /      \    \
               +---------+  +---------+  +---------+
               |  tor0   |  |  tor1   |  |  tor2   |
               +---------+  +---------+  +---------+
                    |            |            |
                  rack0        rack1        rack2

# Usage
Set up MAAS and create the required fabrics, spaces and subnets.

Example spaces:
  - space-0     192.168.122.0/24 (default, oob management, charm connectivity)
  - tor0uplink0 172.16.100.0/30
  - tor0uplink1 172.16.101.0/30
  - tor1uplink0 172.16.110.0/30
  - tor1uplink1 172.16.111.0/30
  - tor2uplink0 172.16.120.0/30
  - tor2uplink1 172.16.121.0/30
  - rack0       172.16.200.0/24
  - rack1       172.16.210.0/24
  - rack2       172.16.220.0/24


Add first Spine router and Top of Rack routers.

    juju deploy --bind "ptp0=tor0uplink0 ptp1=tor1uplink0 ptp2=tor2uplink0 space-0" quagga spine0
    juju deploy --bind "ptp0=tor0uplink0 ptp1=tor0uplink1 lan0=rack0 space-0" quagga tor0
    juju deploy --bind "ptp0=tor1uplink0 ptp1=tor1uplink1 lan0=rack1 space-0" quagga tor1
    juju deploy --bind "ptp0=tor2uplink0 ptp1=tor2uplink1 lan0=rack2 space-0" quagga tor2

    juju add-relation spine0:bgpserver tor0:bgpclient
    juju add-relation spine0:bgpserver tor1:bgpclient
    juju add-relation spine0:bgpserver tor2:bgpclient

## Scale out Usage
Add the second Spine router and relate it to the existing Top of Rack routers.

    juju deploy --bind "ptp0=tor0uplink1 ptp1=tor1uplink1 ptp2=tor2uplink1 space-0" quagga spine1

    juju add-relation spine1:bgpserver tor0:bgpclient
    juju add-relation spine1:bgpserver tor1:bgpclient
    juju add-relation spine1:bgpserver tor2:bgpclient

## Known Limitations and Issues
At the current stage this charm is meant for simulation and testing purposes only.

# Configuration
No configuration is currently necessary, the charm infers required information from the environment it is deployed in.

# Contact Information
Author: Frode Nordahl <frode.nordahl@gmail.com>

## Upstream Project Name
Quagga Software Routing Suite

Website: http://www.nongnu.org/quagga/
Bug tracker: https://bugzilla.quagga.net/
