"""VitiScience sensor simulator.

Publishes synthetic SHT31-style telemetry (temperature + relative humidity) to the
MQTT broker, exactly as the real Raspberry Pi gateway will. It lets you run and
demo the whole dashboard pipeline on a laptop with no hardware.

This script depends ONLY on the data contract (topic + JSON payload), never on the
dashboard code. Swapping it for the real gateway requires no dashboard change.

Usage:
    pip install -r requirements.txt
    python sensor_simulator.py

Configuration is via environment variables (see config.py). Common ones:
    MQTT_HOST (default localhost), MQTT_PORT (1883),
    SIM_NODE_COUNT (3) or SIM_NODE_IDS (node-01,node-02),
    SIM_INTERVAL_S (5), SIM_SEED (optional, for reproducible noise).
"""

from __future__ import annotations

import json
import random
import signal
import sys
import time
from datetime import datetime, timezone

import paho.mqtt.client as mqtt

from config import SimConfig
from models import NodeProfile, build_payload


def _make_client(client_id: str) -> mqtt.Client:
    """Create a paho client that works on both paho-mqtt 2.x and 1.x."""
    try:
        # paho-mqtt >= 2.0 requires an explicit callback API version.
        return mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
        )
    except (AttributeError, TypeError):
        # paho-mqtt 1.x
        return mqtt.Client(client_id=client_id)


class Simulator:
    def __init__(self, config: SimConfig) -> None:
        self.config = config
        self.profiles = [NodeProfile.for_node(n) for n in config.node_ids]
        self.rng = random.Random(config.seed)
        self.client = _make_client("vitiscience-simulator")
        self._running = True

    def connect(self) -> None:
        print(
            f"[simulator] connecting to {self.config.broker_host}:{self.config.broker_port} ...",
            flush=True,
        )
        self.client.connect(
            self.config.broker_host,
            self.config.broker_port,
            keepalive=self.config.keepalive,
        )
        self.client.loop_start()
        print(
            f"[simulator] publishing for nodes: {', '.join(self.config.node_ids)} "
            f"every {self.config.interval_s}s",
            flush=True,
        )

    def publish_round(self, ts: datetime | None = None) -> int:
        """Publish one message per node. Returns how many were sent."""
        ts = ts or datetime.now(timezone.utc)
        sent = 0
        for profile in self.profiles:
            payload = build_payload(profile, ts=ts, rng=self.rng)
            topic = self.config.topic_for(profile.node_id)
            self.client.publish(topic, json.dumps(payload), qos=self.config.qos)
            print(
                f"[simulator] {topic}  "
                f"T={payload['temperature_c']}C  HR={payload['humidity_pct']}%",
                flush=True,
            )
            sent += 1
        return sent

    def run(self) -> None:
        self.connect()
        try:
            while self._running:
                self.publish_round()
                time.sleep(self.config.interval_s)
        finally:
            self.client.loop_stop()
            self.client.disconnect()
            print("[simulator] stopped.", flush=True)

    def stop(self, *_args) -> None:
        self._running = False


def main() -> int:
    config = SimConfig()
    sim = Simulator(config)
    signal.signal(signal.SIGINT, sim.stop)
    signal.signal(signal.SIGTERM, sim.stop)
    try:
        sim.run()
    except ConnectionRefusedError:
        print(
            f"[simulator] ERROR: could not connect to broker at "
            f"{config.broker_host}:{config.broker_port}. "
            "Is the dashboard stack running (docker compose up -d)?",
            file=sys.stderr,
        )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
