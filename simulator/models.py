"""Synthetic microclimate model for the VitiScience node simulator.

This module is pure, dependency-free Python: given a node id and a moment in time
it produces a realistic-looking temperature / relative-humidity reading and the
JSON-serializable payload defined in ``dashboard/docs/data-contract.md``.

Keeping the physics here (separate from the MQTT plumbing in
``sensor_simulator.py``) makes it trivial to unit-test without a broker.
"""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from datetime import datetime, timezone


# Plausible bounds (kept in sync with telemetry.schema.json / SHT31 range).
TEMP_MIN_C = -40.0
TEMP_MAX_C = 85.0
RH_MIN_PCT = 0.0
RH_MAX_PCT = 100.0


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _seconds_since_midnight(ts: datetime) -> float:
    midnight = ts.replace(hour=0, minute=0, second=0, microsecond=0)
    return (ts - midnight).total_seconds()


def _diurnal_phase(ts: datetime) -> float:
    """Return the daily cycle position in radians (0 at 00:00, 2*pi at 24:00)."""
    return 2.0 * math.pi * _seconds_since_midnight(ts) / 86400.0


@dataclass(frozen=True)
class NodeProfile:
    """Per-node baseline so several simulated nodes look distinct but realistic.

    Each node has slightly different mean conditions and a deterministic phase
    offset, emulating microclimatic heterogeneity between vineyard quarters.
    """

    node_id: str
    temp_mean_c: float = 18.0       # daily mean temperature
    temp_amplitude_c: float = 7.0   # half peak-to-peak daily swing
    rh_mean_pct: float = 65.0       # daily mean relative humidity
    rh_amplitude_pct: float = 20.0  # half peak-to-peak daily swing
    phase_offset_h: float = 0.0     # shifts the daily curve (microclimate)
    battery_v: float = 12.8         # LiFePO4 nominal-ish

    @classmethod
    def for_node(cls, node_id: str) -> "NodeProfile":
        """Build a deterministic profile from the node id.

        Same id -> same profile across runs, so tests and dashboards are stable.
        """
        seed = abs(hash(node_id)) % 1000
        return cls(
            node_id=node_id,
            temp_mean_c=16.0 + (seed % 7),          # 16..22 C
            temp_amplitude_c=6.0 + (seed % 5),      # 6..10 C
            rh_mean_pct=60.0 + (seed % 15),         # 60..74 %
            rh_amplitude_pct=15.0 + (seed % 10),    # 15..24 %
            phase_offset_h=(seed % 6) - 3.0,        # -3..+2 h
            battery_v=12.4 + (seed % 6) / 10.0,     # 12.4..12.9 V
        )


def temperature_c(profile: NodeProfile, ts: datetime, noise: float = 0.0) -> float:
    """Temperature following a daily cosine (coldest ~06:00, warmest ~15:00)."""
    phase = _diurnal_phase(ts) - 2.0 * math.pi * profile.phase_offset_h / 24.0
    # Shift so the minimum lands roughly at dawn and maximum mid-afternoon.
    value = profile.temp_mean_c - profile.temp_amplitude_c * math.cos(phase - math.pi / 3.0)
    return _clamp(value + noise, TEMP_MIN_C, TEMP_MAX_C)


def humidity_pct(profile: NodeProfile, ts: datetime, noise: float = 0.0) -> float:
    """Relative humidity in anti-phase with temperature (humid at night)."""
    phase = _diurnal_phase(ts) - 2.0 * math.pi * profile.phase_offset_h / 24.0
    value = profile.rh_mean_pct + profile.rh_amplitude_pct * math.cos(phase - math.pi / 3.0)
    return _clamp(value + noise, RH_MIN_PCT, RH_MAX_PCT)


def build_payload(
    profile: NodeProfile,
    ts: datetime | None = None,
    rng: random.Random | None = None,
    include_optional: bool = True,
) -> dict:
    """Build one telemetry payload conforming to the project data contract.

    Args:
        profile: node baseline.
        ts: instant of the reading (defaults to now, UTC).
        rng: optional Random for reproducible noise (tests pass a seeded one).
        include_optional: when True, adds ``battery_v`` and ``rssi_dbm``.

    Returns:
        A JSON-serializable dict matching ``telemetry.schema.json``.
    """
    if ts is None:
        ts = datetime.now(timezone.utc)
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    rng = rng or random.Random()

    temp = temperature_c(profile, ts, noise=rng.gauss(0.0, 0.3))
    rh = humidity_pct(profile, ts, noise=rng.gauss(0.0, 1.5))

    payload: dict = {
        "node_id": profile.node_id,
        "timestamp": ts.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "temperature_c": round(temp, 2),
        "humidity_pct": round(rh, 2),
    }
    if include_optional:
        payload["battery_v"] = round(profile.battery_v + rng.gauss(0.0, 0.05), 2)
        payload["rssi_dbm"] = round(-70 + rng.gauss(0.0, 8.0))
    return payload
