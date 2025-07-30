# Pong

A TCP/UDP port ping client that allows you to test connectivity to specific ports without using ICMP protocol.

## Installation

```bash
pip install pong
```

## Usage

```bash
# TCP port ping
pong tcp example.com 80

# UDP port ping
pong udp example.com 53

# With custom timeout (in seconds)
pong tcp example.com 80 --timeout 2

# With custom number of packets
pong tcp example.com 80 --count 5
```

## Features

- TCP and UDP port testing
- Configurable timeout
- Configurable number of packets
- Rich terminal output
- Detailed statistics

## Requirements

- Python 3.8 or higher 