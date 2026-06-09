# VitiScience — Sensor Simulator

A standalone MQTT publisher that emits **synthetic SHT31-style telemetry**
(temperature + relative humidity) so the whole [dashboard](../dashboard) pipeline can
be run and demoed on a laptop, with no hardware.

It depends **only** on the data contract
([`dashboard/docs/data-contract.md`](../dashboard/docs/data-contract.md)) — same MQTT
topic, same JSON payload the real Raspberry Pi gateway will use. Swapping the simulator
for the real gateway requires **no dashboard change**.

## What it produces

For each configured node it publishes, every `SIM_INTERVAL_S` seconds, to:

```
vitiscience/nodes/<node_id>/telemetry
```

a payload like:

```json
{ "node_id": "node-01", "timestamp": "2026-06-07T12:00:00Z",
  "temperature_c": 23.45, "humidity_pct": 56.12, "battery_v": 12.7, "rssi_dbm": -78 }
```

Readings follow a realistic **daily cycle** (coldest near dawn, warmest mid-afternoon;
humidity in anti-phase), with per-node offsets emulating microclimatic differences
between vineyard quarters, plus small measurement noise.

## Run

Start the dashboard stack first (so the broker exists), then:

```powershell
cd simulator
pip install -r requirements.txt
python sensor_simulator.py
```

Stop with Ctrl+C.

## Configuration (environment variables)

| Variable             | Default                                   | Meaning                              |
|----------------------|-------------------------------------------|--------------------------------------|
| `MQTT_HOST`          | `localhost`                               | Broker host (use the Pi's IP for remote) |
| `MQTT_PORT`          | `1883`                                    | Broker TCP port                      |
| `MQTT_QOS`           | `1`                                       | Publish QoS                          |
| `SIM_NODE_COUNT`     | `3`                                       | Number of nodes (`node-01`…)         |
| `SIM_NODE_IDS`       | (unset)                                   | Explicit ids, e.g. `node-a,node-b` (overrides count) |
| `SIM_INTERVAL_S`     | `5`                                       | Seconds between publish rounds       |
| `SIM_SEED`           | (unset)                                   | Fix the RNG for reproducible noise   |
| `MQTT_TOPIC_TEMPLATE`| `vitiscience/nodes/{node_id}/telemetry`   | Topic pattern                        |

Example — point at the Raspberry Pi and simulate 5 nodes every 2 s:

```powershell
$env:MQTT_HOST="192.168.1.50"; $env:SIM_NODE_COUNT="5"; $env:SIM_INTERVAL_S="2"
python sensor_simulator.py
```

## Tests

```powershell
cd simulator
pip install -r requirements-dev.txt
pytest tests -v
```

- `test_models.py` — the diurnal model stays within physical bounds and is deterministic.
- `test_payload_contract.py` — generated payloads validate against the dashboard's
  authoritative `telemetry.schema.json` (the guard rail that keeps simulator and
  dashboard interchangeable).

## Files

```
simulator/
  sensor_simulator.py    # MQTT publisher (paho-mqtt)
  models.py              # diurnal temp/RH model + payload builder (pure, testable)
  config.py              # env-driven configuration
  requirements.txt       # paho-mqtt
  requirements-dev.txt   # + pytest, jsonschema
  tests/
```
