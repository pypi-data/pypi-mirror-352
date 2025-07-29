# PDNS Zone Search

[![pipeline status](https://gitlab.com/wulfstar-com/pdns-zone-search/badges/main/pipeline.svg)](https://gitlab.com/wulfstar-com/pdns-zone-search/-/commits/main)
[![coverage report](https://gitlab.com/wulfstar-com/pdns-zone-search/badges/main/coverage.svg)](https://gitlab.com/wulfstar-com/pdns-zone-search/-/commits/main)

A lightweight CLI tool for searching PowerDNS zone listings and extracting matching record sets as structured JSON.

## Overview

PDNS Zone Search is designed to simplify searching through PowerDNS zone files by providing a simple command-line 
interface to extract and filter DNS records. It takes the output from `pdnsutil list-zone` commands, parses it 
into structured data, and allows filtering by record name, type, and optionally by record data.

## Installation

```shell script
pip install pdns-zone-search
```


## Usage

The tool is designed to be used in a pipeline with `pdnsutil`, reading zone data from standard input:

```shell script
pdnsutil list-zone example.com | pdns-zone-search example.com A
```


### Command Line Options

```
pdns-zone-search NAME TYPE
```


- `NAME`: The DNS record name to search for
- `TYPE`: The DNS record type (supported types: A, PTR)

### Examples

1. Find all the A records for "www.example.com":
    ```shell script
    pdnsutil list-zone example.com | pdns-zone-search www.example.com A
    ```
2. Find all the PTR records for "server.example.com" (searches the data field of the zone):
    ```shell script
    pdnsutil list-zone 1.168.192.in-addr.arpa | pdns-zone-search server.example.com PTR
    ```


## Output Format

The tool outputs JSON-formatted data for easy parsing in scripts:

```json
[
  [
    "proxmox.demo.example.com",
    "3600",
    "IN",
    "A",
    "10.0.0.100"
  ],
  [
    "proxmox.demo.example.com",
    "3600",
    "IN",
    "A",
    "10.0.0.100"
  ],
  [
    "proxmox.demo.example.com",
    "3600",
    "IN",
    "A",
    "10.0.0.107"
  ]
]
```

For record sets with multiple entries (like multiple A records for load balancing), all matching records are returned 
in the array.

## Features

- Parses the output of `pdnsutil list-zone` into structured data
- Filters records by name
- Returns full record sets (all records of the same name and type)
- JSON output for easy integration with other tools and scripts

## How It Works

1. The tool reads zone data from standard input
2. It parses the zone data into a structured format
3. It filters records based on the provided name and type
4. It returns the matching record set as JSON

## License

This project is licensed under the MIT License, see the [LICENSE](LICENSE) file in the root directory for details.
