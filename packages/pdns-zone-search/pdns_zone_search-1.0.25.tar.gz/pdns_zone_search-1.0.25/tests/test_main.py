# Copyright (c) 2025 Captain Wulfstar <9593988-wulf-star@users.noreply.gitlab.com>
# This code is licensed under the MIT License - see the LICENSE file in the root directory.

# tests/test_main.py

import pytest
import sys
import io
import json
from pdns_zone_search.main import parse_pdnsutil_output, get_result_set, main

@pytest.fixture
def mock_stdin(monkeypatch):
    """Fixture to create a mock stdin that can be configured per test"""
    def _mock_stdin(content):
        monkeypatch.setattr(sys, 'stdin', io.StringIO(content))
    return _mock_stdin

@pytest.fixture
def mock_args(monkeypatch):
    """Fixture to mock command line arguments"""
    def _set_args(args):
        monkeypatch.setattr(sys, 'argv', args)
    return _set_args


def test_main_with_valid_arguments(mock_args, mock_stdin, capsys):
    # Set up the test
    result = {}
    mock_args(['main.py', 'example.com', 'A'])
    mock_stdin("$ORIGIN .\nexample.com 3600 IN A 192.168.1.1\nexample.com 3600 IN A 192.168.1.2")

    # Run the main function
    main()

    captured = capsys.readouterr()
    output = captured.out

    if not output:
        print(f"Warning: capsys captured empty output: {captured.err}")

    try:
        result = json.loads(output)
    except json.JSONDecodeError as e:
        pytest.fail(f"Failed to parse JSON output: {e}")

    # Verify the result structure
    assert len(result) == 2
    assert result[0][4] == "192.168.1.1"
    assert result[1][4] == "192.168.1.2"


@pytest.mark.parametrize("filename,expect_len,expected_names", [
    ("tests/pdnsutil-output/list-zone-0.0.10.in-addr.arpa.txt", 2, ["0.0.10.in-addr.arpa", "15.0.0.10.in-addr.arpa"]),
    ("tests/pdnsutil-output/list-zone-demo-example-com.txt", 30, ["proxmox.demo.example.com", "dns01.demo.example.com", "grafana.demo.example.com"]),
    ("tests/pdnsutil-output/list-zone-empty.txt", 0, []),
    ("tests/pdnsutil-output/list-zone-invalid.txt", 0, []),
    ("tests/pdnsutil-output/list-zone-multiple-blank-lines.txt", 1, ["demo.example.com"])
], ids=["zone-0.0.10", "zone-demo-example-com", "zone-empty", "zone-invalid", "zone-multiple-blank-lines"])

def test_parse_dnsutil(filename: str, expect_len: int, expected_names: list):
    data = open(filename).read()
    result = parse_pdnsutil_output(data)

    domain_names = {r[0] for r in result}
    assert len(domain_names) == expect_len
    assert set(expected_names).issubset(domain_names)

@pytest.mark.parametrize("filename,search_name,search_type,expect_data,expect_len", [
    ("tests/pdnsutil-output/list-zone-demo-example-com.txt", "proxmox.demo.example.com", "A", ["10.0.0.100","10.0.0.107"], 3),
    ("tests/pdnsutil-output/list-zone-demo-example-com.txt", "noexist.demo.example.com", "A", [], 0),
    ("tests/pdnsutil-output/list-zone-demo-example-com.txt", "prometheus.demo.example.com", "A", [], 0),
    ("tests/pdnsutil-output/list-zone-74.168.192.in-addr.arpa.txt", "wg-01.demo.example.com", "PTR", ["wg-01.demo.example.com"], 1),
    ], ids=["proxmox.demo.example.com",
        "not_exists_but_data_exists",
        "exists_but_not_type_A",
            "23.74.168.192.in-addr.arpa",
    ]
)
def test_get_rrset(filename: str, search_name: str, search_type: str, expect_data: list, expect_len: int):
    data = open(filename).read()
    result = parse_pdnsutil_output(data)
    rrset = get_result_set(result, search_name, search_type)
    data_set = {r[4] for r in rrset}

    assert len(rrset) == expect_len, \
        f"rrset is {rrset} search_type is {search_type} search_name is {search_name}"
    assert set(expect_data) == data_set, f"Expected {set(expect_data)} to equal {data_set}"

