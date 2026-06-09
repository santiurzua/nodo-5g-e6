# Simulador de sensores

Publicador MQTT independiente que emite **telemetría sintética estilo SHT31**
(temperatura + humedad relativa) para que todo el pipeline del
[dashboard](../dashboard) pueda correrse y demostrarse en un PC, sin hardware.

Solo depende del contrato de datos
([`dashboard/docs/data-contract.md`](../dashboard/docs/data-contract.md)) —
mismo topic MQTT, mismo payload JSON que usará el gateway real de la Raspberry Pi.
Reemplazar el simulador por el gateway real **no requiere ningún cambio en el dashboard**.

## Qué produce

Por cada nodo configurado, publica cada `SIM_INTERVAL_S` segundos en:

```
vitiscience/nodes/<node_id>/telemetry
```

un payload como:

```json
{ "node_id": "node-01", "timestamp": "2026-06-07T12:00:00Z",
  "temperature_c": 23.45, "humidity_pct": 56.12, "battery_v": 12.7, "rssi_dbm": -78 }
```

Las lecturas siguen un **ciclo diario realista** (más frío cerca del amanecer, más
cálido a media tarde; humedad en fase contraria), con offsets por nodo que emulan
diferencias microclimáticas entre sectores del viñedo, más ruido de medición pequeño.

## Cómo correr

Primero iniciar el stack del dashboard (para que exista el broker), luego:

```bash
cd simulator
pip install -r requirements.txt
python sensor_simulator.py
```

Detener con Ctrl+C.

## Configuración (variables de entorno)

| Variable               | Default                                     | Descripción                                         |
|------------------------|---------------------------------------------|-----------------------------------------------------|
| `MQTT_HOST`            | `localhost`                                 | Host del broker (usar IP de la Pi para acceso remoto) |
| `MQTT_PORT`            | `1883`                                      | Puerto TCP del broker                               |
| `MQTT_QOS`             | `1`                                         | QoS de publicación                                  |
| `SIM_NODE_COUNT`       | `3`                                         | Número de nodos (`node-01`…)                        |
| `SIM_NODE_IDS`         | (no fijado)                                 | IDs explícitos, ej. `node-a,node-b` (sobreescribe el conteo) |
| `SIM_INTERVAL_S`       | `5`                                         | Segundos entre rondas de publicación                |
| `SIM_SEED`             | (no fijado)                                 | Fija el RNG para ruido reproducible                 |
| `MQTT_TOPIC_TEMPLATE`  | `vitiscience/nodes/{node_id}/telemetry`     | Patrón de topic                                     |

Ejemplo — apuntar a la Raspberry Pi y simular 5 nodos cada 2 s:

```bash
MQTT_HOST="192.168.1.50" SIM_NODE_COUNT="5" SIM_INTERVAL_S="2" python sensor_simulator.py
```

PowerShell:
```powershell
$env:MQTT_HOST="192.168.1.50"; $env:SIM_NODE_COUNT="5"; $env:SIM_INTERVAL_S="2"
python sensor_simulator.py
```

## Tests

```bash
cd simulator
pip install -r requirements-dev.txt
pytest tests -v
```

- `test_models.py` — el modelo diurno se mantiene dentro de límites físicos y es
  determinista.
- `test_payload_contract.py` — los payloads generados validan contra el
  `telemetry.schema.json` del dashboard (la salvaguarda que mantiene simulador y
  dashboard intercambiables).

## Archivos

```
simulator/
  sensor_simulator.py    # publicador MQTT (paho-mqtt)
  models.py              # modelo diurno temp/HR + constructor de payload (puro, testeable)
  config.py              # configuración basada en variables de entorno
  requirements.txt       # paho-mqtt
  requirements-dev.txt   # + pytest, jsonschema
  tests/
```
