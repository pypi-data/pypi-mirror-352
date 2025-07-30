# Pingos

A TCP/UDP port ping client that allows you to test connectivity to specific ports without using ICMP protocol.

**Pingos** is named by adding the Greek-style suffix 'os' to 'ping', inspired by the naming conventions of ancient Greek words and modern open-source projects.

## Installation

```bash
pip install pingos
```

## Usage

```bash
# TCP port ping
pingos tcp example.com 80

# UDP port ping
pingos udp example.com 53

# With custom timeout (in seconds)
pingos tcp example.com 80 --timeout 2

# With custom number of packets
pingos tcp example.com 80 --count 5
```

## Features

- TCP and UDP port testing
- Configurable timeout
- Configurable number of packets
- Rich terminal output
- Detailed statistics

## Requirements

- Python 3.8 or higher 