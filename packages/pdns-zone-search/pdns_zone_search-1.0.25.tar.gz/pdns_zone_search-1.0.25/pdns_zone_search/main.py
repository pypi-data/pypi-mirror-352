# Copyright (c) 2025 Captain Wulfstar <9593988-wulf-star@users.noreply.gitlab.com>
# This code is licensed under the MIT License - see the LICENSE file in the root directory.


import argparse
import json
import sys
from typing import List
import importlib.util
import os

# Get version using importlib
def get_version():
    try:
        # Try to import from the package
        if '.' in __name__:
            package_name = __name__.split('.')[0]
            package = importlib.import_module(package_name)
            return getattr(package, '__version__', 'unknown')
        else:
            # We're likely in development mode
            spec = importlib.util.spec_from_file_location("__init__",
                os.path.join(os.path.dirname(__file__), "__init__.py"))
            if spec and spec.loader:
                init_module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(init_module)
                return getattr(init_module, '__version__', 'unknown')
            return None
    except (ImportError, AttributeError, FileNotFoundError):
        return 'unknown'

__version__ = get_version()

def parse_pdnsutil_output(data) -> List[List[str]]:
    records = []
    lines = data.strip().split('\n')

    # Skip the "$ORIGIN ." line if present
    start_index = 0
    if lines and lines[0].strip() == "$ORIGIN .":
        start_index = 1

    for line in lines[start_index:]:
        if not line.strip():
            continue

        parts = line.strip().split()

        # Extract components - format is generally:
        if len(parts) >= 5:
            name = parts[0]
            ttl = parts[1]
            record_class = parts[2]
            record_type = parts[3]
            # The data part can contain spaces, so join the remaining elements
            record_data = ' '.join(parts[4:])

            record = [name, ttl, record_class, record_type, record_data]
            records.append(record)
    return records


def get_result_set(records, name, record_type) -> List[List[str]]:
    if record_type == 'A':
        record_matches = [l for l in records if (l[0] == name) and (l[3] == record_type)]
    else:
        record_matches = [l for l in records if (l[4] == name) and (l[3] == record_type)]
    return record_matches


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='''Search PowerDNS Zone Listing
        
Custom search tool for PowerDNS, searches directly from the pdnsutil zone listing.  There are two modes of
searching: forward zone search, reverse zone search.  If the type is 'A', then the search is forward zone search and
the stdin input is expected to be the pdnsutil output for a forward zone listing.  If the type is 'PTR', then the
search is reverse zone search and the stdin input is expected to be the pdnsutil output for a reverse zone listing.

For the forward zone search, the name is expected to be the fully qualified domain name, this is searched in the 
zone's NAME field (field 1 of the listing).  For the reverse zone search, the name is expected to also be a fully 
qualified domain name, but this is searched in the zone's DATA field (field 5 of the listing).  Search pattern is
an exact match search.

The result is that if you have multiple forward zone records with the same name, you get the entire list returned as
a JSON list of list records.  If you have multiple reverse zone records that point to data with the same name, you get
the entire list as a JSON list of list records.

Each list in the returned JSON list contains the fully qualified name, ttl, class, type, and data fields in that order.
If no match is found, an empty list is returned.
''',
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('name', type=str)
    parser.add_argument('type', type=str, choices=['A', 'PTR'])
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}')
    return parser.parse_args()

def main():
    args = parse_args()
    pdnsutil_output = ''.join(sys.stdin.readlines())
    records = parse_pdnsutil_output(pdnsutil_output)
    matched_records = get_result_set(records, args.name, args.type)
    print(json.dumps(matched_records, indent=2))

if __name__ == '__main__':
    main()
