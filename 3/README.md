# CS 6381

## Assignment 3
Fault-Tolerant Broker-Based Publish-Subscribe With QoS Using ZMQ, Mininet and Zookeeper

### Testing

Run `sudo python3 test.py` with the appropriate options. Two common examples for each of the approaches listed below. The `test.py` script will create a mininet network and run the `application.py` script on the appropiate hosts and output from the hosts will be logged into the same directory e.g. `h1.log` and `h2.log` etc.

This assignment only supports approach 2 per the professor's instructions.

Approach 2 (publishers relay everything through broker)

```
sudo python3 test.py --relay --delay 1 --topics 1 --hosts 2 --zookeepers h1 --brokers h1 --publishers h1 --subscribers h2
```

### test.py options

```
--automate - the number of end-to-end messages that you would like to be recorded

--output - the generated file name desired for the recorded end-to-end messages
 
--delay - the delay in seconds that publishers wait between sending data, can be fraction of a second or whole seconds e.g. 0.5 for half a second

--topics - the number of topics that subscribers and publishers will use

--hosts - the number of hosts to create in the mininet tree topology

--zookeepers - the list of zookeeper hosts, only the first one in the list is used for this assignment, all others are ignored (no clustering)

--brokers - the list of broker hosts, must make sense based on the number of hosts specified with the --hosts flag i.e. don't list h3 as one of the hosts if you specified --hosts 2 because only h1 and h2 hosts will exist

--publishers - list of publisher hosts, must also make sense based on the note above for brokers

--subscriber - list of subscriber hosts, must also make sense based on the note above for brokers
```
*** Example with all options:

`sudo python3 test.py --automate 1000 --output 5pub-5sub-relay.log --relay --delay 0.01 --topics 1 --hosts 12 --zookeepers h11 --brokers h11-h12 --publishers h1-h5 --subscribers h6-h10`

### Application

Run `python3 application.py` with the appropiate options. Two common examples given below. Zookeeper must already be running on port 2181.

This assignment only supports approach 2 per the professor's instructions.

Approach 2 (publishers relay everything through broker)

```
python3 application.py broker --relay 127.0.0.1 2181
python3 application.py publisher --relay --delay 1 --topics 1 127.0.0.1 2181
python3 application.py subscriber --relay --topics 1 127.0.0.1 2181
```

### application.py options

First argument should be one of:

```
broker
publisher
subscriber
```

```
--delay - the delay in seconds that publishers wait between sending data, can be fraction of a second or whole seconds e.g. 0.5 for half a second (only available for publisher)

--topics - the number of topics that subscribers and publishers will use (only available for publisher and subscriber)
```

The final two arguments should be zookeeper address and port.
