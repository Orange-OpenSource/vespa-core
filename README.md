# Tutorial [![Build Status](https://travis-ci.org/Orange-OpenSource/vespa-core.svg?branch=tutorial)](https://travis-ci.org/Orange-OpenSource/vespa-core)

## Setup

You can setup your local environment with the following commands :

```bash
git clone https://github.com/Orange-OpenSource/vespa-core.git --branch tutorial
cd vespa-core/vespa
```

Now we configure our VESPA instance to fit our infrastructure

## Configuration

The [configuration files](vespa/config.ini) describes both the physical infrastructure and the VESPA deployment.

### Physical infrastructure

Each node of the infrastructure is represented as following :

```ini
[infrastructurenodename]
Type= (Machine|Hypervisor|VM)
Interfaces= IP1, IP2, ...
```

The ``infrastructurenodename`` is the hostname of the object (as returned by the ``hostname`` command). The sed command may help you to replace the ``laptop`` with your hostname:

```bash
sed -i "s/laptop/$(hostname)" config.ini
```

First, we define a single node in our infrastructure that will host all VESPA components :

```ini
[laptop]
Type= Machine
Interfaces= 127.0.0.1
```

### VESPA deployment

The framework objects are represented as following :

```ini
[frameworknodename]
Location= [infrastructurenodename]
Master= [masterframeworknodename]
Port= (UniquePort)
```

The VESPA model requires a `Vertical Orchestrator`, a `Horizontal Orchestrator`, and `Agents`. Thus we define a starter template :

```ini
[VO]
Location= laptop
Master=
Port= 4150

[HO]
Location= laptop
Master= VO
Port= 4151

[Agent_Demo]
Location= laptop
Master= HO
Port= 4152
```

Note that the `Vertical Orchestrator` doesn't have a master, it is the root of the hierarchy.

We name the agent for the tutorial `Agent_Demo` that will be further referenced through the [agent_demo.py](vespa/agent_demo.py). The VESPA node name in the configuration file have to be identical to the node filename.

## Agent implementation

Our first agent will monitor a file (here ``/home/dad/file``) and wait for a specific keyword (here ``bilou``) to generate an alert.

We first need an equivalent of the ``tail -f`` command:

```python
def follow(self, thefile):
    thefile.seek(0,2)      # Go to the end of the file
    while not self.quitting:
        line = thefile.readline()
        if not line:
            time.sleep(0.1)    # Sleep briefly
            continue
        yield line
```

The Node class uses the ``run`` argument to specify if its role is Detection, Reaction or both. Here it is a Detection agent (run=True) that call the ``launch`` function during this startup. We can then define the function as :

```python
def launch(self):
    logfile = open("/home/dad/file")
    loglines = self.follow(logfile)
    keyword = "bilou"
    for line in loglines:
	if keyword in line:
	    self.sendAlert("new_line#%s" % line)
```

The ``sendAlert`` function inform the master defined in the configuration when a new event appear. The event is a ``new_line`` with the line containing the keyword as the first argument. The # is a reserved keyword to separate arguments.

Now we have to define the framework behavior when the ``new_line`` alert is received.

## Policies implementation

The policies are defined at the root of the hierarchy in the ``vo.py`` file. The special function alert is called when the ``sendAlert`` primitive is used by a node. The parsing of the message is done as following :

```python
def alert(self, msg):
    debug_comm_len("[%s] Received alert : %s" % (self.name, msg))
    source = msg.split("|")[1].split(">")[-2]
    message = msg.split(">")[-1]
    #
    # New node registered
    #
    if "archi=" in message:
	self.sendRemotef(self.model, "alert|%s>%s" % (self.name, msg.split("|")[1]))

    if source == "Agent_Demo":
    if "new_line" in message:
        args = message.split('#')
        line = args[1]

        #agent_demo = self.findNode("Agent_Demo")
        #self.sendRemotef(agent_controller, "alert_ip|%s#%s" % (ipobj['value'], mac))
        debug_info("Alert received: %s" % line)
    else:
        self.sendRemotef(self.model, "alert|%s>Unexpected alert: %s" % (self.name, message))
```

This tutorial doesn't show how to send a request back to a Reaction agent. The comment lines hold the code needed to do it.

## Starting the framework

Our tutorial is setup, and we test if everything is working by using the [starter.py](vespa/starter.py) helper:

```bash
touch /home/dad/file
cd vespa
python2 ./starter.py
```

_NOTE_: The framework may hang if you quit using CTRL+C. You will need to do CTRL+Z and kill the background job with ``kill %``.

## Creating an event

An event is created when a line containing the keyword is added to the monitored file :

```bash
echo "noevent" >> /home/dad/file
echo "bilou" >> /home/dad/file
```

## Logging verbosity

The file [log_pipe.py](vespa/log_pipe.py) provides logging facilities for the framework. For extra verbosity you have to uncomment the part you are interested in.

To better understand how objects are registered, you can activate the `debug_init` logging :

```python
def debug_init(str):
#    print "%s[INIT]%s %s" % (bcolors.OKGREEN, bcolors.ENDC, str)
    pass
```

Become:

```python
def debug_init(str):
    print "%s[INIT]%s %s" % (bcolors.OKGREEN, bcolors.ENDC, str)
    pass
```
