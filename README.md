## Synopsis

This project is the core of the VESPA framework. It can enable communications between heterogeneous components.

[![Build Status](https://travis-ci.org/Orange-OpenSource/vespa-core.svg?branch=master)](https://travis-ci.org/Orange-OpenSource/vespa-core) [![Build Status](https://readthedocs.org/projects/vespa-core/badge/?version=latest)](http://vespa-core.readthedocs.org/en/latest/)

## Code Example

The politics are defined as Finite State Machine in Python. It enables easy parametrization and comprehensive view of autonomic loops. The ``alert`` function is the main component of the orchestration.

Agent nodes are linked to security components, such as firewalls and anti-viruses, and mediate vendor lock-ins with the framework orchestration APIs. The functions are exported to other nodes and can be called automatically. The ``sendRemote`` function is a primitive to communicate with other nodes.

## Motivation

The VESPA framework aims at giving the building block for an autonomic security on cloud computing environments.

## Installation

Grab the core files of the project with the following commands:

```bash
git clone https://github.com/Orange-OpenSource/vespa-core
cd vespa-core
```

A convenient way to start is to follow the tutorial (branch tutorial) and setup a local environment.

## API Reference

The API of nodes is described into the code headers, and will be available as a doxygen API soon.

## Tests

The tutorial (branch tutorial) delivers the basic of agent implementation and how to manage alerts on the Vertical Orchestrator.

## Contributors

Aurélien Wailly, Marc Lacoste, Kévin Grandemange, Aymerik Tabourin.

## License

The code is released as LGPL v2.1, and contains some external code under MIT license.
