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
__NOTE__:
The bgp interface is currently not in the directory and you must download it
manually from [here](https://github.com/fnordahl/interface-bgp).

Instructions for building charm with local artifacts can be found in the
[Juju documentation](https://jujucharms.com/docs/devel/developer-layers-interfaces#creating-an-interface-layer). There is also an example below.


## Build
This is a layered charm and it must be built before it can be deployed.

Example build instructions:

    export JUJU_REPOSITORY=`pwd`
    export LAYER_PATH=$JUJU_REPOSITORY/layers
    export INTERFACE_PATH=$JUJU_REPOSITORY/interfaces
    mkdir -p $LAYER_PATH $INTERFACE_PATH
    
    git clone https://github.com/fnordahl/interface-bgp $INTERFACE_PATH/bgp
    git clone https://github.com/fnordahl/charm-quagga quagga
    
    cd quagga
    sudo snap install charm
    charm build

You will now find a deployable charm in ../builds/quagga


## Simple Usage
To just get a BGP router to play and speak with you can deploy the charm to a
LXD container on your laptop using the localhost provider.

    juju deploy quagga

To interface with quagga CLI:

    juju ssh quagga/0 sudo -s
    VTYSH_PAGER=cat vtysh
    
    Hello, this is Quagga (version 0.99.24.1).
    Copyright 1996-2005 Kunihiro Ishiguro, et al.
    
    juju-c7f4d7-0# show run
    Building configuration...
    
    Current configuration:
    !
    !
    ...


## Advanced Usage
Set up MAAS and create the required fabrics, spaces and subnets.

Example spaces:

|     Space     |       CIDR       |                 Note                 |
| ------------- | ---------------- | ------------------------------------ |
| space-0       | 192.168.122.0/24 | (oob management, charm connectivity) |
| tor0uplink0   | 172.16.100.0/30  |                                      |
| tor0uplink1   | 172.16.101.0/30  |                                      |
| tor1uplink0   | 172.16.110.0/30  |                                      |
| tor1uplink1   | 172.16.111.0/30  |                                      |
| tor2uplink0   | 172.16.120.0/30  |                                      |
| tor2uplink1   | 172.16.121.0/30  |                                      |
| rack0         | 172.16.200.0/24  |                                      |
| rack1         | 172.16.210.0/24  |                                      |
| rack2         | 172.16.220.0/24  |                                      |


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
