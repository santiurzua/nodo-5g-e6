"""Unit tests for the synthetic microclimate model (no broker required)."""

from __future__ import annotations

import random
from datetime import datetime, timedelta, timezone

import pytest

from models import (
    RH_MAX_PCT,
    RH_MIN_PCT,
    TEMP_MAX_C,
    TEMP_MIN_C,
    NodeProfile,
    build_payload,
    humidity_pct,
    temperature_c,
)


def test_profile_is_deterministic_per_node():
    a1 = NodeProfile.for_node("node-01")
    a2 = NodeProfile.for_node("node-01")
    b = NodeProfile.for_node("node-02")
    assert a1 == a2
    assert a1 != b


@pytest.mark.parametrize("hour", range(0, 24))
def test_temperature_and_humidity_stay_within_physical_bounds(hour):
    profile = NodeProfile.for_node("node-01")
    ts = datetime(2026, 1, 15, hour, 0, 0, tzinfo=timezone.utc)
    rng = random.Random(123)
    for _ in range(50):
        t = temperature_c(profile, ts, noise=rng.gauss(0, 0.3))
        h = humidity_pct(profile, ts, noise=rng.gauss(0, 1.5))
        assert TEMP_MIN_C <= t <= TEMP_MAX_C
        assert RH_MIN_PCT <= h <= RH_MAX_PCT


def test_diurnal_cycle_warmer_in_afternoon_than_pre_dawn():
    profile = NodeProfile(node_id="n", phase_offset_h=0.0)
    pre_dawn = datetime(2026, 1, 15, 5, 0, tzinfo=timezone.utc)
    afternoon = datetime(2026, 1, 15, 15, 0, tzinfo=timezone.utc)
    assert temperature_c(profile, afternoon) > temperature_c(profile, pre_dawn)


def test_humidity_anti_phase_with_temperature():
    profile = NodeProfile(node_id="n", phase_offset_h=0.0)
    pre_dawn = datetime(2026, 1, 15, 5, 0, tzinfo=timezone.utc)
    afternoon = datetime(2026, 1, 15, 15, 0, tzinfo=timezone.utc)
    # Humid before dawn, drier in the afternoon.
    assert humidity_pct(profile, pre_dawn) > humidity_pct(profile, afternoon)


def test_build_payload_shape_and_types():
    profile = NodeProfile.for_node("node-07")
    ts = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    payload = build_payload(profile, ts=ts, rng=random.Random(0))

    assert payload["node_id"] == "node-07"
    assert payload["timestamp"] == "2026-01-15T12:00:00Z"
    assert isinstance(payload["temperature_c"], float)
    assert isinstance(payload["humidity_pct"], float)
    assert "battery_v" in payload and "rssi_dbm" in payload


def test_build_payload_can_omit_optional_fields():
    profile = NodeProfile.for_node("node-07")
    payload = build_payload(profile, include_optional=False, rng=random.Random(0))
    assert "battery_v" not in payload
    assert "rssi_dbm" not in payload


def test_naive_timestamp_is_treated_as_utc():
    profile = NodeProfile.for_node("node-01")
    naive = datetime(2026, 1, 15, 9, 30, 0)  # no tzinfo
    payload = build_payload(profile, ts=naive, rng=random.Random(0))
    assert payload["timestamp"] == "2026-01-15T09:30:00Z"


def test_seeded_rng_makes_payloads_reproducible():
    profile = NodeProfile.for_node("node-01")
    ts = datetime(2026, 1, 15, 12, 0, tzinfo=timezone.utc)
    p1 = build_payload(profile, ts=ts, rng=random.Random(42))
    p2 = build_payload(profile, ts=ts, rng=random.Random(42))
    assert p1 == p2
