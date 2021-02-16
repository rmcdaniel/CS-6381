# CS 6381

## Assignment 1
Single Broker-Based Publish-Subscribe Using ZMQ and Mininet

### Testing

Run `sudo python3 test.py` with the appropriate options. Two common examples for each of the approaches listed below. The `test.py` script will create a mininet network and run the `application.py` script on the appropiate hosts and output from the hosts will be logged into the same directory e.g. `h1.log` and `h2.log` etc.

Approach 1 (publishers talk directly to subscribers, broker only makes introduction)

```
sudo python3 test.py --delay 1 --topics 1 --hosts 2 --brokers h1 --publishers h1 --subscribers h2
```

Approach 2 (publishers relay everything through broker)

```
sudo python3 test.py --relay --delay 1 --topics 1 --hosts 2 --brokers h1 --publishers h1 --subscribers h2
```

### test.py options

```
--automate - the number of end-to-end messages that you would like to be recorded.

--output - the generated file name desired for the recorded end-to-end messages.
 
--relay - if this flag is present then publishers relay everything through the broker otherwise the publishers talk directly to the subscribers

--delay - the delay in seconds that publishers wait between sending data, can be fraction of a second or whole seconds e.g. 0.5 for half a second

--topics - the number of topics that subscribers and publishers will use

--hosts - the number of hosts to create in the mininet tree topology

--brokers - the list of broker hosts, only the first one in the list is used for this assignment, all others are ignored (single broker)

--publishers - list of publisher hosts, must make sense base on the number of hosts specified with the --hosts flag i.e. don't list h3 as one of the hosts if you specified --hosts 2 because only h1 and h2 hosts will exist

--subscriber - list of subscriber hosts, must also make sense based on the note above for publishers
```
*** Example with all options:

`sudo python3 test.py --automate 1000 --output 5pub-5sub-relay.log --relay --delay 0.01 --topics 1 --hosts 11 --brokers h11 --publishers h1-h5 --subscribers h6-h10`

### Application

Run `python3 application.py` with the appropiate options. Two common examples given below.

Approach 1 (publishers talk directly to subscribers, broker only makes introduction)

```
python3 application.py broker 127.0.0.1 5555
python3 application.py publisher --delay 1 --topics 1 127.0.0.1 5555
python3 application.py subscriber --topics 1 127.0.0.1 5555
```

Approach 2 (publishers relay everything through broker)

```
python3 application.py broker --relay 127.0.0.1 5555
python3 application.py publisher --relay --delay 1 --topics 1 127.0.0.1 5555
python3 application.py subscriber --relay --topics 1 127.0.0.1 5555
```

### application.py options

First argument should be one of:

```
broker
publisher
subscriber
```

```
--relay - if this flag is present then publishers relay everything through the broker otherwise the publishers talk directly to the subscribers (available for broker, publisher and subscriber, all must use relay or not for things to work, cannot mix and match)

--delay - the delay in seconds that publishers wait between sending data, can be fraction of a second or whole seconds e.g. 0.5 for half a second (only available for publisher)

--topics - the number of topics that subscribers and publishers will use (only available for publisher and subscriber)
```

Final two arguments should be broker address and broker port. If broker relay option is specified then broker will also open a second sequential port i.e. if you specify relay and broker port = 5555 then broker will listen on both port 5555 and 5556.

### graphical data processing

To produce the graphical representation of the application's end-to-end time measurements, we ran the following scenarios:

***NOTE: EACH SCENARIO WAS RAN TWICE (ONCE FOR EACH APPROACH) FOR A TOTAL OF 10 RUNS)
```  
1. 1Topic, 1Broker(always), 1Publisher, 1Subscriber
2. 5Topic, 1Broker, 5Publisher, 5Subscriber
3. 10Topic, 1Broker, 10Publisher, 10Subscriber
4. 15Topic, 1Broker, 15Publisher, 15Subscriber
5. 20Topic, 1Broker, 20Publisher, 20Subscriber
```
The subcriber is responsible for producing the time measurements. For scenarios wwith more than one subscriber, measurements from each sub was collated into one file to facilitate processing.

The graphical representation present within the repo identifies the max amount of time in each of the 10 runs and the average end-to-end measurement across a minimum of 300 measurement inquiries. It allows the viewer to (1) compare the speed of approach 1 to approach 2 for a specific scenario and (2) compare the end-to-end measurements across an increasing network. For clarity the Y-axis expresses time while the X-axis expresses the scenario. An example scenario nomenclature is as follows: 1T_1P_1S or 1T_1P_1S_R.
	T = Topic
	P = Publisher
	S = Subscriber
	R indicated the presence of the relay broker
