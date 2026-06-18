"""End-to-end integration test for the VitiScience dashboard pipeline.

Proves the full chain works:  MQTT publish -> Mosquitto -> Telegraf -> InfluxDB,
and that Grafana is up with its datasource provisioned.

Requires the stack to be running:  (cd dashboard && docker compose up -d)
If the services are not reachable, the whole module is SKIPPED (so unit tests
still pass on a machine without Docker).

    pip install -r tests/requirements-test.txt
    pytest tests/test_pipeline_integration.py -v
"""

from __future__ import annotations

import json
import time
import uuid
from datetime import datetime, timezone

import pytest

# Optional deps: skip cleanly if missing.
mqtt = pytest.importorskip("paho.mqtt.client")
influxdb_client = pytest.importorskip("influxdb_client")
requests = pytest.importorskip("requests")

from influxdb_client import InfluxDBClient  # noqa: E402


# ----------------------------------------------------------------------------- helpers

def _influx_url(env) -> str:
    return env.get("INFLUXDB_URL", "http://localhost:8086")


def _grafana_url(env) -> str:
    return env.get("GRAFANA_URL", "http://localhost:3000")


def _mqtt_host_port(env):
    return env.get("MQTT_HOST", "localhost"), int(env.get("MQTT_TCP_PORT", "1883"))


def _influx_reachable(env) -> bool:
    try:
        r = requests.get(_influx_url(env) + "/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


def _grafana_reachable(env) -> bool:
    try:
        r = requests.get(_grafana_url(env) + "/api/health", timeout=3)
        return r.status_code == 200
    except Exception:
        return False


@pytest.fixture(scope="module")
def require_stack(stack_env):
    if not _influx_reachable(stack_env) or not _grafana_reachable(stack_env):
        pytest.skip(
            "dashboard stack not reachable on localhost - run "
            "`docker compose up -d` in dashboard/ first."
        )
    return stack_env


def _make_client():
    try:
        return mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)
    except (AttributeError, TypeError):
        return mqtt.Client()


# ----------------------------------------------------------------------------- tests

def test_grafana_health(require_stack):
    env = require_stack
    r = requests.get(_grafana_url(env) + "/api/health", timeout=5)
    assert r.status_code == 200
    assert r.json().get("database") == "ok"


def test_grafana_datasources_provisioned(require_stack):
    env = require_stack
    auth = (env.get("GRAFANA_USER", "admin"), env.get("GRAFANA_PASSWORD", "admin"))
    r = requests.get(_grafana_url(env) + "/api/datasources", auth=auth, timeout=5)
    assert r.status_code == 200, r.text
    types = {ds["type"] for ds in r.json()}
    assert "influxdb" in types, f"InfluxDB datasource missing; got {types}"


def test_publish_lands_in_influxdb(require_stack):
    env = require_stack
    host, port = _mqtt_host_port(env)
    bucket = env.get("INFLUXDB_BUCKET", "telemetry")
    org = env.get("INFLUXDB_ORG", "vitiscience")
    token = env.get("INFLUXDB_TOKEN")

    node_id = f"itest-{uuid.uuid4().hex[:8]}"
    payload = {
        "node_id": node_id,
        "timestamp": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "temperature_c": 24.5,
        "humidity_pct": 61.0,
        "battery_v": 12.7,
        "rssi_dbm": -75,
    }
    topic = f"vitiscience/nodes/{node_id}/telemetry"

    client = _make_client()
    client.connect(host, port, keepalive=30)
    client.loop_start()
    info = client.publish(topic, json.dumps(payload), qos=1)
    info.wait_for_publish(timeout=5)
    client.loop_stop()
    client.disconnect()

    flux = f'''
from(bucket: "{bucket}")
  |> range(start: -10m)
  |> filter(fn: (r) => r._measurement == "telemetry" and r.node_id == "{node_id}")
  |> filter(fn: (r) => r._field == "temperature_c")
  |> last()
'''

    deadline = time.time() + 40  # allow for Telegraf flush interval (5s) + margin
    found = None
    with InfluxDBClient(url=_influx_url(env), token=token, org=org) as ic:
        query_api = ic.query_api()
        while time.time() < deadline and found is None:
            tables = query_api.query(flux)
            for table in tables:
                for record in table.records:
                    found = record.get_value()
            if found is None:
                time.sleep(3)

    assert found is not None, (
        f"point for {node_id} never appeared in bucket '{bucket}' "
        "- check telegraf logs (docker compose logs telegraf)."
    )
    assert abs(found - 24.5) < 0.001
