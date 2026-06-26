"""Contract test: every payload the simulator emits must validate against the
authoritative JSON Schema owned by the Raspberry Pi stack
(``rpi/docs/telemetry.schema.json``).

This is the guard rail that keeps the simulator and the dashboard interchangeable:
if the simulator ever drifts from the data contract, this test fails. The schema is
read from the stack side (the contract owner); the stack never reads anything from
the simulator.
"""

from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path

import pytest

jsonschema = pytest.importorskip("jsonschema")

from models import NodeProfile, build_payload  # noqa: E402

# simulator/tests/ -> simulator/ -> project root -> rpi/docs/...
SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "rpi"
    / "docs"
    / "telemetry.schema.json"
)


@pytest.fixture(scope="module")
def schema() -> dict:
    assert SCHEMA_PATH.exists(), f"data contract schema not found at {SCHEMA_PATH}"
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


@pytest.mark.parametrize("node_id", ["node-01", "node-02", "node-15"])
@pytest.mark.parametrize("hour", [0, 6, 12, 18])
def test_payload_validates_against_contract(schema, node_id, hour):
    profile = NodeProfile.for_node(node_id)
    ts = datetime(2026, 1, 15, hour, 0, tzinfo=timezone.utc)
    payload = build_payload(profile, ts=ts, rng=random.Random(hour))
    jsonschema.validate(instance=payload, schema=schema)


def test_payload_without_optional_fields_still_valid(schema):
    profile = NodeProfile.for_node("node-01")
    payload = build_payload(profile, include_optional=False, rng=random.Random(0))
    jsonschema.validate(instance=payload, schema=schema)


def test_topic_segment_matches_node_id_in_payload(schema):
    """The contract requires the topic's <node_id> to equal payload.node_id."""
    from config import SimConfig

    profile = NodeProfile.for_node("node-03")
    payload = build_payload(profile, rng=random.Random(0))
    topic = SimConfig().topic_for(payload["node_id"])
    assert topic == "vitiscience/nodes/node-03/telemetry"
