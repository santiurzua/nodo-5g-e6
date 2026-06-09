# VitiScience — Dashboard (storage + visualization)

The storage + visualization layer for the VitiScience microclimate node. It ingests
telemetry (temperature & relative humidity) from the MQTT broker, stores ~3 days of
history in InfluxDB, and shows it in Grafana — with a real-time MQTT stream panel.

Everything runs in **one Docker Compose stack** that is identical on a Windows dev
machine and on the Raspberry Pi (the Pi is the server). See
[`docs/architecture.md`](docs/architecture.md) for the full picture and
[`docs/data-contract.md`](docs/data-contract.md) for the MQTT/JSON contract that
keeps this layer independent of whoever produces the data.

```
Mosquitto (MQTT) ──► Telegraf ──► InfluxDB (3-day buffer) ──► Grafana
       └──────────────── live stream ──────────────────────────┘
```

## Services

| Service   | URL / port              | Purpose                                  |
|-----------|-------------------------|------------------------------------------|
| Grafana   | http://localhost:3000   | Dashboards (open "VitiScience — Overview")|
| InfluxDB  | http://localhost:8086   | Time-series DB / admin UI                |
| Mosquitto | localhost:1883 (TCP), 9001 (WS) | MQTT broker — publishers connect here |
| Telegraf  | (internal)              | MQTT → InfluxDB writer                    |

## Prerequisites

- Docker Desktop (Windows/macOS) or Docker Engine + compose plugin (Raspberry Pi, 64-bit OS).

## Quick start (Windows dev)

```powershell
cd dashboard
Copy-Item .env.example .env      # then review passwords/token inside
docker compose up -d
# or use the helper:  ./run.ps1 up
```

Open Grafana at http://localhost:3000 (user/pass from `.env`, defaults `admin` /
the password you set). The **VitiScience — Overview** dashboard is auto-provisioned.

To see data flowing, start the simulator in another terminal (separate folder):

```powershell
cd ../simulator
pip install -r requirements.txt
python sensor_simulator.py
```

Within a few seconds the historical panels fill in and the live panel streams.

### Helper script

```powershell
./run.ps1 up      # create .env if missing + start
./run.ps1 logs    # follow logs
./run.ps1 ps      # status
./run.ps1 down    # stop (keep data)
./run.ps1 reset   # stop + wipe data volumes
./run.ps1 urls    # print URLs
```

## The dashboard

`VitiScience — Overview` has:
1. **Temperatura actual** — latest temp per node (stat).
2. **Humedad relativa actual** — latest RH per node (gauge).
3. **Riesgo de oídio (simplificado)** — placeholder risk flag: "Favorable" when temp
   ∈ [15, 30] °C and RH ≥ 70 % in the last hour. ⚠️ Tune this rule with VitiScience's
   agronomic criteria (thresholds are dashboard constants `temp_min`/`temp_max`/`rh_min`).
4. **Temperatura / Humedad por nodo** — 3-day time series from InfluxDB.
5. **Stream en vivo desde el broker MQTT** — real-time push via Grafana Live.

> The live panel uses the experimental `grafana-mqtt-datasource` plugin (installed
> automatically). If it ever fails to load, panels 1–4 (InfluxDB + 5 s auto-refresh)
> still give you near-real-time data.

## Deploy on the Raspberry Pi

Same commands; just use a 64-bit Raspberry Pi OS. Then point the real gateway's
publisher at the Pi's broker (`<pi-ip>:1883`) using the same topic/payload. For remote
viewing over 5G, install **Tailscale** on the Pi and your phone/PC and browse to the
Pi's tailnet IP on port 3000 — see [`docs/architecture.md`](docs/architecture.md).

## Tests

```powershell
cd dashboard
pip install -r tests/requirements-test.txt
pytest tests/test_data_contract.py -v          # no stack needed
docker compose up -d
pytest tests/test_pipeline_integration.py -v   # full MQTT→InfluxDB→Grafana check
```

The integration test publishes a known reading and asserts it lands in InfluxDB and
that Grafana is healthy with its datasources provisioned. If the stack isn't running,
that test is skipped (the contract tests still run).

## Configuration

All knobs live in `.env` (copied from `.env.example`): InfluxDB org/bucket/retention/token,
Grafana credentials, MQTT ports. Changing `INFLUXDB_BUCKET` also means updating the
`bucket` constant in the dashboard JSON (or via the dashboard's variables).

## Layout

```
dashboard/
  docker-compose.yml          # the 4-service stack
  .env.example                # copy to .env
  run.ps1                     # convenience wrapper
  config/
    mosquitto/mosquitto.conf
    telegraf/telegraf.conf
    grafana/provisioning/...  # datasources + dashboard provider
    grafana/dashboards/vitiscience-overview.json
  docs/
    data-contract.md          # MQTT topic + JSON payload (source of truth)
    telemetry.schema.json     # machine-readable contract
    architecture.md
  tests/                      # contract (no stack) + integration (stack)
```
