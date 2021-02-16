'''
Mininet Test
'''
import argparse
import os

from mininet.cli import CLI
from mininet.log import lg, info
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.topolib import TreeTopo
from mininet.util import waitListening

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Single Broker-Based Publish-Subscribe Using ZMQ')
    parser.add_argument('-b', '--brokers', nargs='*', required=True, help='broker host names')
    parser.add_argument('-d', '--delay', type=float, default=1, required=False, help='delay between publisher sends')
    parser.add_argument('-n', '--hosts', type=int, default=2, required=False, help='number of hosts')
    parser.add_argument('-p', '--publishers', nargs='*', required=True, help='publisher host names')
    parser.add_argument('-r', '--relay', action='store_true', required=False, help='use relay')
    parser.add_argument('-s', '--subscribers', nargs='*', required=True, help='subscriber host names')
    parser.add_argument('-t', '--topics', type=int, default=1, required=False, help='number of topics')
    options = parser.parse_args()
    path = os.path.dirname(os.path.realpath(__file__))
    if len(options.brokers) > 1:
        raise Exception('Multiple brokers not supported for this assignment')
    lg.setLogLevel('info')
    topo = TreeTopo(1, options.hosts)
    network = Mininet(topo=topo, switch=OVSBridge, controller=None, waitConnected=True)
    IP = '10.123.123.1/32'
    switch = network['s1']
    routes = ['10.0.0.0/24']
    root = Node('root', inNamespace=False)
    intf = network.addLink(root, switch).intf1
    root.setIP(IP, intf=intf)
    network.start()
    for route in routes:
        root.cmd('route add -net {} dev {}'.format(route, intf))
    for host in network.hosts:
        if host.name in options.brokers:
            broker = host
    if options.relay:
        broker.cmd('python3 "{}/application.py" broker -r {} 5555 &> "{}/{}.log" &'.format(path, broker.IP(), path, broker.name))
    else:
        broker.cmd('python3 "{}/application.py" broker {} 5555 &> "{}/{}.log" &'.format(path, broker.IP(), path, broker.name))
    info('*** Waiting for broker to start\n')
    waitListening(server=broker.IP(), port=5555, timeout=5)
    for host in network.hosts:
        if host.name in options.publishers:
            if options.relay:
                host.cmd('python3 "{}/application.py" publisher -r -d {} -t {} {} 5555 &> "{}/{}.log" &'.format(path, options.delay, options.topics, broker.IP(), path, host.name))
            else:
                host.cmd('python3 "{}/application.py" publisher -d {} -t {} {} 5555 &> "{}/{}.log" &'.format(path, options.delay, options.topics, broker.IP(), path, host.name))
        if host.name in options.subscribers:
            if options.relay:
                host.cmd('python3 -u "{}/application.py" subscriber -r -t {} {} 5555 &> "{}/{}.log" &'.format(path, options.topics, broker.IP(), path, host.name))
            else:
                host.cmd('python3 -u "{}/application.py" subscriber -t {} {} 5555 &> "{}/{}.log" &'.format(path, options.topics, broker.IP(), path, host.name))
    info('\n')
    info('*** Listing hosts\n')
    for host in network.hosts:
        info(host.name, host.IP(), '\n')
    info('*** Press Ctrl-D to stop network\n')
    CLI(network)
    network.stop()
