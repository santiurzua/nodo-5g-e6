# Gateway BLE -> MQTT

Pasarela que conecta el hardware real con el pipeline del dashboard. Escucha en
paralelo las notificaciones Bluetooth (BLE) de los nodos ESP32, decodifica las
lecturas y las publica como JSON del contrato de datos en el broker Mosquitto.
Reemplazar el simulador por esta pasarela no requiere ningun cambio en el dashboard.

```
ESP32_SHT31_Sensor_01 (BLE notify) ─┐
                                     ├─> gateway (este modulo) ─(MQTT JSON)─> Mosquitto :1883
ESP32_DHT11_Sensor_02 (BLE notify) ─┘
```

## Archivos

| Archivo                | Funcion                                                            |
|------------------------|-------------------------------------------------------------------|
| `ble_mqtt_gateway.py`  | Pasarela principal: BLE -> MQTT. Es lo que corre el contenedor.   |
| `ble_client.py`        | Diagnostico: guarda la telemetria de cada sensor en un CSV.       |
| `config.py`            | Configuracion compartida (sensores, UUID, MQTT, BLE) por env vars.|
| `Dockerfile`           | Imagen `python:3.11-slim` + `bleak` + `paho-mqtt`.                |
| `requirements.txt`     | Dependencias Python.                                              |

## Como corre (recomendado: contenedor)

Forma parte del `docker-compose.yml` de `rpi/`, detras del perfil `gateway`:

```bash
cd ..                                   # carpeta rpi/
docker compose --profile gateway up -d --build
docker logs -f vitiscience-gateway
```

El servicio usa `network_mode: host` y monta `/var/run/dbus` para que `bleak`
alcance el stack BlueZ del host. Corre con `privileged: true` para simplificar el
prototipo; mas adelante puede acotarse a `cap_add: [NET_ADMIN]` mas el montaje de
D-Bus. Es solo para Linux/Raspberry Pi (Windows no tiene BlueZ; alli se usa el
simulador).

## Como corre (alternativa: directo en el host)

Util para depurar BLE. En Raspberry Pi OS (Bookworm) conviene un entorno virtual:

```bash
python3 -m venv env-ble
source env-ble/bin/activate
pip install -r requirements.txt
python ble_mqtt_gateway.py          # o: python ble_client.py para grabar CSV
```

## Contrato de datos emitido

La pasarela mapea cada nombre BLE a un `node_id` fijo y publica en
`vitiscience/nodes/<node_id>/telemetry`:

```json
{
  "node_id": "node-01",
  "timestamp": "2026-06-19T19:47:00+00:00",
  "temperature_c": 21.45,
  "humidity_pct": 58.20,
  "battery_v": 12.6,
  "rssi_dbm": -65
}
```

`battery_v` y `rssi_dbm` son valores fijos por ahora (el hardware aun no los mide);
se ajustan con `GATEWAY_BATTERY_V` y `GATEWAY_RSSI_DBM`. El timestamp en formato
RFC3339 con offset `+00:00` es aceptado por el parser de Telegraf. La carga BLE de
cada ESP32 es un string CSV simple `"temp,hum"` (ej. `"25.4,60.1"`).

## Configuracion (variables de entorno)

| Variable                 | Default                                   | Descripcion                                  |
|--------------------------|-------------------------------------------|----------------------------------------------|
| `MQTT_HOST`              | `localhost`                               | Host del broker                              |
| `MQTT_PORT`              | `1883`                                    | Puerto TCP del broker                        |
| `MQTT_QOS`               | `1`                                       | QoS de publicacion                           |
| `MQTT_TOPIC_TEMPLATE`    | `vitiscience/nodes/{node_id}/telemetry`   | Patron de topic                              |
| `BLE_CHARACTERISTIC_UUID`| `5bd26117-...-feb4526c`                   | UUID GATT (debe coincidir con el firmware)   |
| `BLE_SCAN_TIMEOUT_S`     | `10`                                      | Ventana de escaneo por intento (s)           |
| `BLE_RECONNECT_DELAY_S`  | `5`                                       | Espera entre reintentos (s)                  |
| `GATEWAY_BATTERY_V`      | `12.6`                                    | Valor fijo temporal de bateria               |
| `GATEWAY_RSSI_DBM`       | `-65`                                     | Valor fijo temporal de RSSI                  |

La tabla de sensores (nombre BLE -> `node_id`) vive en `config.py`. Debe coincidir
con los nombres que anuncian los ESP32 (ver [`../../esp32/README.md`](../../esp32/README.md)).
