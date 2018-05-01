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
To just get a BGP router to play and speak with you can deploy the charm to a
LXD container on your laptop using the localhost provider.

    $ juju deploy cs:~openstack-charmers-next/quagga

To interface with quagga CLI:

    $ juju ssh quagga/0 sudo -s
    $ VTYSH_PAGER=cat vtysh
    
    Hello, this is Quagga (version 0.99.24.1).
    Copyright 1996-2005 Kunihiro Ishiguro, et al.
    
    juju-c7f4d7-0# show bgp ipv4 unicast
    BGP table version is 0, local router ID is 172.16.122.254
    Status codes: s suppressed, d damped, h history, * valid, > best, = multipath,
                  i internal, r RIB-failure, S Stale, R Removed
    Origin codes: i - IGP, e - EGP, ? - incomplete
    
       Network          Next Hop            Metric LocPrf Weight Path
    *> 172.16.100.0/30  172.16.120.1             0             0 4279270138 ?
    *> 172.16.101.0/30  172.16.120.1                           0 4279270138 4279270139 ?
    *> 172.16.110.0/30  172.16.120.1             0             0 4279270138 ?
    *> 172.16.111.0/30  172.16.120.1                           0 4279270138 4279270140 ?
    *  172.16.120.0/30  172.16.120.1             0             0 4279270138 ?
    *>                  0.0.0.0                  0         32768 ?
    *> 172.16.121.0/30  0.0.0.0                  0         32768 ?
    *  172.16.122.0/24  172.16.120.1             0             0 4279270138 ?
    *>                  0.0.0.0                  0         32768 ?
    
    Total number of prefixes 7
    juju-c7f4d7-0# show bgp ipv6 unicast
    BGP table version is 0, local router ID is 172.16.122.254
    Status codes: s suppressed, d damped, h history, * valid, > best, = multipath,
                  i internal, r RIB-failure, S Stale, R Removed
    Origin codes: i - IGP, e - EGP, ? - incomplete
    
       Network          Next Hop            Metric LocPrf Weight Path
    *> 2001:db8:100::/64
                        2001:db8:120::1:0:0
                                                 0             0 4279270138 i
    *> 2001:db8:110::/64
                        2001:db8:120::1:0:0
                                                 0             0 4279270138 i
    *  2001:db8:120::/64
                        2001:db8:120::1:0:0
                                                 0             0 4279270138 i
    *>                  ::                       0         32768 i
    
    Total number of prefixes 3


## Advanced Usage
Set up MAAS and create the required fabrics, spaces and subnets.

Example spaces:

|     Space     |   IPv4/IPv6 CIDR    |                 Note                 |
| ------------- | :------------------ | ------------------------------------ |
| space-0       | `192.168.122.0/24`  | (oob management, charm connectivity) |
| tor0uplink0   | `172.16.100.0/30`   |                                      |
|               | `2001:db8:100::/64` |                                      |
| tor0uplink1   | `172.16.101.0/30`   |                                      |
|               | `2001:db8:101::/64` |                                      |
| tor1uplink0   | `172.16.110.0/30`   |                                      |
|               | `2001:db8:110::/64` |                                      |
| tor1uplink1   | `172.16.111.0/30`   |                                      |
|               | `2001:db8:111::/64` |                                      |
| tor2uplink0   | `172.16.120.0/30`   |                                      |
|               | `2001:db8:120::/64` |                                      |
| tor2uplink1   | `172.16.121.0/30`   |                                      |
|               | `2001:db8:121::/64` |                                      |
| rack0         | `172.16.200.0/24`   |                                      |
|               | `2001:db8:200::/56` |                                      |
| rack1         | `172.16.210.0/24`   |                                      |
|               | `2001:db8:210::/56` |                                      |
| rack2         | `172.16.220.0/24`   |                                      |
|               | `2001:db8:220::/56` |                                      |


Add first Spine router and Top of Rack routers.

    juju deploy --bind "ptp0=tor0uplink0 ptp1=tor1uplink0 ptp2=tor2uplink0 space-0" cs:~openstack-charmers-next/quagga spine0
    juju deploy --bind "ptp0=tor0uplink0 ptp1=tor0uplink1 lan0=rack0 space-0" cs:~openstack-charmers-next/quagga tor0
    juju deploy --bind "ptp0=tor1uplink0 ptp1=tor1uplink1 lan0=rack1 space-0" cs:~openstack-charmers-next/quagga tor1
    juju deploy --bind "ptp0=tor2uplink0 ptp1=tor2uplink1 lan0=rack2 space-0" cs:~openstack-charmers-next/quagga tor2

    juju add-relation spine0:bgpserver tor0:bgpclient
    juju add-relation spine0:bgpserver tor1:bgpclient
    juju add-relation spine0:bgpserver tor2:bgpclient


## Scale out Usage
Add the second Spine router and relate it to the existing Top of Rack routers.

    juju deploy --bind "ptp0=tor0uplink1 ptp1=tor1uplink1 ptp2=tor2uplink1 space-0" cs:~openstack-charmers-next/quagga spine1

    juju add-relation spine1:bgpserver tor0:bgpclient
    juju add-relation spine1:bgpserver tor1:bgpclient
    juju add-relation spine1:bgpserver tor2:bgpclient


## Known Limitations and Issues
At the current stage this charm is meant for simulation and testing purposes only.


# Configuration
The charm infers required information from the environment it is deployed in
and from relations with other charms.

For available configuration options and usage take a look at [config.yaml](config.yaml).


# Contact Information
Author: OpenStack Charmers <openstack-dev@lists.openstack.org>

Icon made from "Zebra" (C) Nevit Dilmen licensed as Creative Commons BY-SA 3.0


## Upstream Project Name
Quagga Software Routing Suite

Website: http://www.nongnu.org/quagga/
Bug tracker: https://bugzilla.quagga.net/
