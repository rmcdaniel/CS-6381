'''
Mininet Test
'''
import argparse
import glob
import os
import sys
import time

from mininet.cli import CLI
from mininet.log import lg, info
from mininet.net import Mininet
from mininet.node import Node, OVSBridge
from mininet.topolib import TreeTopo
from mininet.util import waitListening

def get_path():
    '''
    Get path of test.py directory
    '''
    return os.path.dirname(os.path.realpath(__file__))

def parse_args():
    '''
    Parse command line arguments
    '''
    parser = argparse.ArgumentParser(description='Fault-Tolerant Broker-Based Publish-Subscribe Using ZMQ')
    parser.add_argument('-a', '--automate', type=int, required=False, help='sample number of lines to output.log and exit')
    parser.add_argument('-b', '--brokers', nargs='*', required=True, help='broker host names')
    parser.add_argument('-d', '--delay', type=float, default=1, required=False, help='delay between publisher sends')
    parser.add_argument('-n', '--hosts', type=int, default=2, required=False, help='number of hosts')
    parser.add_argument('-o', '--output', default='output.log', required=False, help='merged output log file name')
    parser.add_argument('-p', '--publishers', nargs='*', required=True, help='publisher host names')
    parser.add_argument('-r', '--relay', action='store_true', required=False, help='use relay')
    parser.add_argument('-s', '--subscribers', nargs='*', required=True, help='subscriber host names')
    parser.add_argument('-t', '--topics', type=int, default=1, required=False, help='number of topics')
    parser.add_argument('-z', '--zookeepers', nargs='*', required=True, help='zookeeper host names')
    args = parser.parse_args()
    args.zookeepers = parse_host_ranges(args.zookeepers)
    args.brokers = parse_host_ranges(args.brokers)
    args.publishers = parse_host_ranges(args.publishers)
    args.subscribers = parse_host_ranges(args.subscribers)
    if len(args.zookeepers) > 1:
        print('Multiple zookeepers not supported for this assignment')
        sys.exit(0)
    return args

def parse_host_ranges(host_list):
    '''
    Convert host ranges to list of hosts
    '''
    hosts = []
    for host_name in host_list:
        if '-' in host_name:
            (start, stop) = host_name.replace('h', '').split('-')
            for index in range(int(start), int(stop) + 1):
                hosts.append('h{}'.format(index))
        else:
            hosts.append(host_name)
    return hosts

def start_network():
    '''
    Start mininet network
    '''
    lg.setLogLevel('info')
    topo = TreeTopo(1, options.hosts)
    net = Mininet(topo=topo, switch=OVSBridge, controller=None, waitConnected=True)
    switch = net['s1']
    routes = ['10.0.0.0/24']
    root = Node('root', inNamespace=False)
    interface = net.addLink(root, switch).intf1
    root.setIP('10.123.123.1/32', intf=interface)
    net.start()
    for route in routes:
        root.cmd('route add -net {} dev {}'.format(route, interface))
    return net

def get_zookeeper(net):
    '''
    Get zookeeper from list of hosts
    '''
    for node in net.hosts:
        if node.name in options.zookeepers:
            return node
    return None

def count_log_lines(log_path):
    '''
    Count number of lines across all log files
    '''
    count = 0
    for file_name in glob.glob('{}/h*.log'.format(log_path)):
        with open(file_name, 'r') as input_file:
            count += sum(1 for line in input_file)
    return count

def merge_logs(log_path, output_name, max_number_of_lines):
    '''
    Merge log files into single output.log up to max number of lines
    '''
    count = 0
    try:
        os.remove(output_name)
    except OSError:
        pass
    with open(output_name, 'w') as output_file:
        for file_name in glob.glob('{}/h*.log'.format(log_path)):
            with open(file_name, 'r') as input_file:
                for line in input_file:
                    measurement = line.split()[-1]
                    output_file.write(measurement + '\n')
                    count += 1
                    if count >= max_number_of_lines:
                        return

def delete_logs(log_path):
    '''
    Delete all host log files
    '''
    for file_name in glob.glob('{}/h*.log'.format(log_path)):
        os.remove(file_name)

if __name__ == '__main__':
    path = get_path()

    options = parse_args()

    network = start_network()

    zookeeper = get_zookeeper(network)

    if zookeeper is None:
        network.stop()
        print('Zookeeper not found')
        sys.exit(0)

    info('*** Waiting for zookeeper to start\n')

    zookeeper.cmd('/opt/zookeeper/bin/zkServer.sh start')

    waitListening(server=zookeeper.IP(), port=2181, timeout=5)

    info('\n')

    for host in network.hosts:
        if host.name in options.brokers:
            if options.relay:
                host.cmd('python3 -u "{}/application.py" broker -r {} 2181 &> "{}/{}.log" &'.format(path, zookeeper.IP(), path, host.name))
            else:
                host.cmd('python3 -u "{}/application.py" broker {} 2181 &> "{}/{}.log" &'.format(path, zookeeper.IP(), path, host.name))
        if host.name in options.publishers:
            if options.relay:
                host.cmd('python3 -u "{}/application.py" publisher -r -d {} -t {} {} 2181 &> "{}/{}.log" &'.format(path, options.delay, options.topics, zookeeper.IP(), path, host.name))
            else:
                host.cmd('python3 -u "{}/application.py" publisher -d {} -t {} {} 2181 &> "{}/{}.log" &'.format(path, options.delay, options.topics, zookeeper.IP(), path, host.name))
        if host.name in options.subscribers:
            if options.relay:
                host.cmd('python3 -u "{}/application.py" subscriber -r -t {} {} 2181 &> "{}/{}.log" &'.format(path, options.topics, zookeeper.IP(), path, host.name))
            else:
                host.cmd('python3 -u "{}/application.py" subscriber -t {} {} 2181 &> "{}/{}.log" &'.format(path, options.topics, zookeeper.IP(), path, host.name))

    info('*** Listing hosts\n')

    for host in network.hosts:
        info(host.name, host.IP(), '\n')

    if options.automate:
        info('*** Sampling data\n')
        while count_log_lines(path) < options.automate:
            time.sleep(1)
    else:
        info('*** Press Ctrl-D to stop network\n')
        CLI(network)

    zookeeper.cmd('/opt/zookeeper/bin/zkServer.sh stop')

    network.stop()

    if options.automate:
        info('*** Merging log files to {}\n'.format(options.output))
        merge_logs(path, options.output, options.automate)

    info('*** Cleaning up log files\n')
    delete_logs(path)
