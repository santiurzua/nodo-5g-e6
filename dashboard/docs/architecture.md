# Architecture — VitiScience storage + visualization layer

## Where this sits in the whole node

```
[SHT31]──I2C──[ESP32]──BLE/LoRa──►[Raspberry Pi 4 gateway]──5G──►(internet)
                                          │
                                          │  (Juan Ignacio's gateway app:
                                          │   mesh_receiver / mqtt_connector)
                                          ▼
                          ┌───────────────────────────────────────────────┐
                          │  THIS DELIVERABLE — dashboard/ (Docker stack)   │
                          │  runs ON the Raspberry Pi (it is the server)    │
                          └───────────────────────────────────────────────┘
```

The RPi is both the field gateway **and** the server: the whole storage +
visualization stack runs there in Docker. No cloud VM, no paid service. You reach
it from a phone or PC over the network.

## The stack (one Docker Compose)

```
  Publisher (simulator today / real gateway tomorrow)
        │  MQTT publish  vitiscience/nodes/<id>/telemetry  (JSON)
        ▼
  ┌──────────┐      subscribe        ┌──────────┐        ┌──────────┐
  │ Mosquitto│ ───────────────────►  │ Telegraf │ ─────► │ InfluxDB │
  │  broker  │                       │ mqtt_    │ write  │ bucket   │
  │ 1883/9001│                       │ consumer │        │ 'telemetry'
  └────┬─────┘                       └──────────┘        │ 3d reten.│
       │ subscribe (Grafana Live)                        └────┬─────┘
       │                                                       │ Flux query
       ▼                                                       ▼
  ┌────────────────────────────────────────────────────────────────┐
  │ Grafana  :3000   ── dashboard "VitiScience — Overview"           │
  │   • InfluxDB datasource  → historical panels (last ~3 days)      │
  │   • MQTT datasource      → live stream panel (real-time)         │
  └────────────────────────────────────────────────────────────────┘
        ▲ browser: phone / PC (LAN or Tailscale)
```

### Two read paths (by design, per Juan Ignacio)

| Path        | Source                | What it serves                                  |
|-------------|-----------------------|-------------------------------------------------|
| Historical  | InfluxDB (3-day bucket) | Trends/plots of the last 2–3 days (the buffer). |
| Real-time   | Direct MQTT subscription (Grafana Live) | Live values pushed as they arrive — the "cable from the broker to your screen". |

The historical panels also auto-refresh every 5 s, so they are a guaranteed
near-real-time fallback even if the experimental MQTT datasource plugin fails to load.

## Decoupling — why the dashboard never depends on the simulator

The only thing shared between *who produces data* and *who shows it* is the
**data contract** (`docs/data-contract.md` + `docs/telemetry.schema.json`):

- same MQTT topic: `vitiscience/nodes/<node_id>/telemetry`
- same JSON payload

Swap the `simulator/` for the real gateway's `mqtt_connector` and nothing in
`dashboard/` changes. The contract is enforced from both sides by tests
(`simulator/tests/test_payload_contract.py`, `dashboard/tests/test_data_contract.py`).

## Deployment & remote access

### Local development (Windows)
Docker Desktop runs the exact same `docker-compose.yml`. Everything is on
`localhost`. See the README for the run/demo steps.

### On the Raspberry Pi
- Use a **64-bit** Raspberry Pi OS (all images are multi-arch / arm64).
- `docker compose up -d` — identical to dev.
- Point the real gateway's publisher at the Pi's broker (`<pi-ip>:1883`, same topic/payload).

### Viewing from phone / PC
- **Same Wi-Fi/LAN:** open `http://<pi-ip>:3000`.
- **Remote over the internet / 5G:** the Pi usually has no public IP on cellular
  (carrier-grade NAT). Use a **free, zero-config tunnel — Tailscale** (recommended):
  install it on the Pi and on your phone/PC, then browse to the Pi's tailnet IP on
  port 3000. No port-forwarding, no paid service. (Cloudflare Tunnel is an
  equivalent free alternative.)

## Security note (prototype vs. field)

The prototype broker is **anonymous** and Grafana uses the admin password from
`.env`. Before any real field deployment: enable MQTT auth (username/password or
TLS) in `config/mosquitto/mosquitto.conf`, split the InfluxDB token into
write-only (Telegraf) and read-only (Grafana), and change all default passwords.
None of this changes the data contract.
