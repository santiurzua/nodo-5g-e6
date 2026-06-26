"""Dashboard-side contract tests.

These assert the data contract is internally consistent and that the dashboard's
expectations (topic shape, required fields, InfluxDB mapping) hold. They need no
running stack and no simulator code.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

DASHBOARD_DIR = Path(__file__).resolve().parents[1]
CONTRACT_MD = DASHBOARD_DIR / "docs" / "data-contract.md"
TELEGRAF_CONF = DASHBOARD_DIR / "config" / "telegraf" / "telegraf.conf"

TOPIC_RE = re.compile(r"^vitiscience/nodes/[A-Za-z0-9_-]+/telemetry$")


def test_schema_is_valid_jsonschema(schema):
    # Raises if the schema document itself is malformed.
    jsonschema.Draft202012Validator.check_schema(schema)


def test_valid_payload_passes(schema):
    payload = {
        "node_id": "node-01",
        "timestamp": "2026-06-07T12:00:00Z",
        "temperature_c": 23.45,
        "humidity_pct": 56.12,
        "battery_v": 12.7,
        "rssi_dbm": -78,
    }
    jsonschema.validate(payload, schema)


def test_minimal_payload_passes(schema):
    jsonschema.validate(
        {"node_id": "n1", "temperature_c": 20.0, "humidity_pct": 50.0}, schema
    )


@pytest.mark.parametrize(
    "bad",
    [
        {"temperature_c": 20.0, "humidity_pct": 50.0},                       # missing node_id
        {"node_id": "n1", "humidity_pct": 50.0},                             # missing temp
        {"node_id": "n1", "temperature_c": 20.0},                            # missing rh
        {"node_id": "n1", "temperature_c": 200.0, "humidity_pct": 50.0},     # temp out of range
        {"node_id": "n1", "temperature_c": 20.0, "humidity_pct": 150.0},     # rh out of range
        {"node_id": "n1", "temperature_c": 20.0, "humidity_pct": 50.0, "x": 1},  # extra field
        {"node_id": "bad id!", "temperature_c": 20.0, "humidity_pct": 50.0}, # bad id chars
    ],
)
def test_invalid_payloads_rejected(schema, bad):
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(bad, schema)


def test_topic_format_regex():
    assert TOPIC_RE.match("vitiscience/nodes/node-01/telemetry")
    assert not TOPIC_RE.match("vitiscience/nodes//telemetry")
    assert not TOPIC_RE.match("vitiscience/node-01/telemetry")


def test_telegraf_subscribes_to_contract_topic_and_fields():
    """Telegraf config must match the contract (wildcard topic, node_id tag,
    telemetry measurement, JSON timestamp key)."""
    conf = TELEGRAF_CONF.read_text(encoding="utf-8")
    assert "vitiscience/nodes/+/telemetry" in conf
    assert 'tag_keys = ["node_id"]' in conf
    assert 'name_override = "telemetry"' in conf
    assert 'json_time_key = "timestamp"' in conf
    assert 'data_format = "json"' in conf


def test_contract_doc_exists_and_mentions_core_fields():
    md = CONTRACT_MD.read_text(encoding="utf-8")
    for token in ("node_id", "temperature_c", "humidity_pct",
                  "vitiscience/nodes/", "telemetry"):
        assert token in md
