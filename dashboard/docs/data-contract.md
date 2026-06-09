# Data Contract — VitiScience telemetry

This document is the **single source of truth** that decouples the *publisher* (the simulator
today, the real Raspberry Pi gateway tomorrow) from the *dashboard* (storage + visualization).

As long as a publisher respects this contract, the dashboard works **without any code change**.
Nothing inside `dashboard/` knows or cares who produced the data.

---

## 1. Transport — MQTT

| Property            | Value                                                        |
|---------------------|-------------------------------------------------------------|
| Broker              | Mosquitto                                                    |
| Host (dev)          | `localhost`                                                  |
| Host (deployed)     | the Raspberry Pi running the `dashboard/` stack             |
| Port (TCP)          | `1883`                                                       |
| Port (WebSocket)    | `9001` (used by Grafana Live / browser real-time)           |
| Auth                | anonymous for the prototype (see §5 for hardening)          |
| QoS                 | `1` recommended (at-least-once); `0` acceptable             |
| Retain              | `false`                                                     |

### Topic

```
vitiscience/nodes/<node_id>/telemetry
```

- `<node_id>` is the unique id of the sensing node (e.g. `node-01`).
- One node publishes to exactly one topic.
- The dashboard subscribes with the wildcard `vitiscience/nodes/+/telemetry`.

Example: `vitiscience/nodes/node-01/telemetry`

---

## 2. Payload — JSON

A single UTF-8 JSON object per message. Example:

```json
{
  "node_id": "node-01",
  "timestamp": "2026-06-07T12:00:00Z",
  "temperature_c": 23.45,
  "humidity_pct": 56.12,
  "battery_v": 12.7,
  "rssi_dbm": -78
}
```

### Fields

| Field            | Type    | Unit  | Required | Notes                                                        |
|------------------|---------|-------|----------|--------------------------------------------------------------|
| `node_id`        | string  | —     | **yes**  | Must match the `<node_id>` in the topic.                     |
| `temperature_c`  | number  | °C    | **yes**  | Air temperature. Plausible range −40 … 85 (SHT31 range).    |
| `humidity_pct`   | number  | %RH   | **yes**  | Relative humidity. Range 0 … 100.                           |
| `timestamp`      | string  | —     | no       | ISO-8601 UTC (RFC3339), e.g. `2026-06-07T12:00:00Z`. If omitted, Telegraf timestamps the message on arrival. |
| `battery_v`      | number  | V     | no       | Node battery voltage (LiFePO4 ≈ 12 V nominal).             |
| `rssi_dbm`       | number  | dBm   | no       | Link signal strength (e.g. BLE/LoRa/5G), typically negative. |

The machine-readable version of these rules lives in
[`telemetry.schema.json`](./telemetry.schema.json) (JSON Schema, draft 2020-12) and is
validated by tests on **both** the simulator side and the dashboard side.

---

## 3. Storage mapping (InfluxDB)

Telegraf's `mqtt_consumer` input decodes the payload and writes it to InfluxDB:

| InfluxDB concept | Value                                                      |
|------------------|-----------------------------------------------------------|
| Measurement      | `telemetry`                                               |
| Tag              | `node_id`                                                 |
| Fields           | `temperature_c`, `humidity_pct`, `battery_v`, `rssi_dbm`  |
| Time             | from `timestamp`, else message arrival time              |
| Bucket           | `telemetry` (3-day retention — the historical buffer)     |

---

## 4. The two read paths (dashboard side)

1. **Historical** — Grafana queries InfluxDB (bucket `telemetry`, last ~3 days) with Flux.
2. **Real-time** — Grafana subscribes directly to the MQTT broker (Grafana Live) and streams
   new messages to the browser as they arrive, independent of the database.

Both consume the *same* contract above.

---

## 5. Notes for the real gateway / production hardening

- The gateway's `mqtt_connector` must publish to the **exact** topic and payload defined here.
- For the prototype the broker is anonymous. Before field deployment, enable
  username/password (or TLS client certs) in `mosquitto.conf` and update both the publisher
  and Telegraf credentials. This does **not** change the topic or payload contract.
- Keep payloads well under MQTT/Telegraf limits; a telemetry message is < 256 bytes, matching
  the small-packet budget discussed in the project literature.
