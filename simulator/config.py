"""Runtime configuration for the VitiScience sensor simulator.

Everything is overridable via environment variables so the *same* script can
target a local broker (Windows dev: ``localhost``) or the Raspberry Pi, without
editing code. Defaults are tuned for local development.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env_str(name: str, default: str) -> str:
    return os.environ.get(name, default)


def _env_int(name: str, default: int) -> int:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return int(raw)


def _env_float(name: str, default: float) -> float:
    raw = os.environ.get(name)
    if raw is None or raw.strip() == "":
        return default
    return float(raw)


def _env_node_ids(name: str, default_count: int) -> list[str]:
    """SIM_NODE_IDS as a comma list (e.g. 'node-01,node-02'), else SIM_NODE_COUNT."""
    raw = os.environ.get(name)
    if raw and raw.strip():
        return [n.strip() for n in raw.split(",") if n.strip()]
    count = _env_int("SIM_NODE_COUNT", default_count)
    return [f"node-{i:02d}" for i in range(1, count + 1)]


@dataclass(frozen=True)
class SimConfig:
    broker_host: str = field(default_factory=lambda: _env_str("MQTT_HOST", "localhost"))
    broker_port: int = field(default_factory=lambda: _env_int("MQTT_PORT", 1883))
    keepalive: int = field(default_factory=lambda: _env_int("MQTT_KEEPALIVE", 60))
    qos: int = field(default_factory=lambda: _env_int("MQTT_QOS", 1))
    topic_template: str = field(
        default_factory=lambda: _env_str(
            "MQTT_TOPIC_TEMPLATE", "vitiscience/nodes/{node_id}/telemetry"
        )
    )
    node_ids: list[str] = field(default_factory=lambda: _env_node_ids("SIM_NODE_IDS", 3))
    # Seconds between publish rounds (one message per node per round).
    interval_s: float = field(default_factory=lambda: _env_float("SIM_INTERVAL_S", 5.0))
    # Optional fixed seed for reproducible noise; empty -> nondeterministic.
    seed: int | None = field(
        default_factory=lambda: (
            int(os.environ["SIM_SEED"]) if os.environ.get("SIM_SEED") else None
        )
    )

    def topic_for(self, node_id: str) -> str:
        return self.topic_template.format(node_id=node_id)
