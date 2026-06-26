"""Configuracion compartida del gateway BLE.

Centraliza los parametros que antes estaban duplicados entre
``ble_mqtt_gateway.py`` y ``ble_client.py``. Todo es ajustable por variables de
entorno, siguiendo la misma convencion que el resto del proyecto (ver
``.env.example``). Los valores por defecto reproducen el comportamiento original.
"""

import os

# UUID de la caracteristica GATT. Debe coincidir exactamente con el firmware del
# ESP32 (ver esp32/SENSOR_0x_*/src/main.cpp).
CHARACTERISTIC_UUID: str = os.getenv(
    "BLE_CHARACTERISTIC_UUID", "5bd26117-cecc-41b2-96b6-1ceefeb4526c"
)

# Tabla de sensores. La clave es un id interno; "name" es el nombre BLE que anuncia
# cada ESP32, "node_id" es el identificador del contrato MQTT y "prefix" se usa para
# nombrar los CSV del script de diagnostico.
SENSORES: dict[str, dict[str, str]] = {
    "sensor_1": {
        "name": "ESP32_SHT31_Sensor_01",
        "node_id": "node-01",
        "prefix": "sensor_01",
    },
    "sensor_2": {
        "name": "ESP32_DHT11_Sensor_02",
        "node_id": "node-02",
        "prefix": "sensor_02",
    },
}

# --- MQTT ---------------------------------------------------------------------
# Broker del dashboard. "localhost" cuando el gateway corre en la misma Pi.
MQTT_HOST: str = os.getenv("MQTT_HOST", "localhost")
MQTT_PORT: int = int(os.getenv("MQTT_PORT", "1883"))
MQTT_QOS: int = int(os.getenv("MQTT_QOS", "1"))
MQTT_KEEPALIVE_S: int = int(os.getenv("MQTT_KEEPALIVE_S", "60"))
MQTT_TOPIC_TEMPLATE: str = os.getenv(
    "MQTT_TOPIC_TEMPLATE", "vitiscience/nodes/{node_id}/telemetry"
)

# --- BLE ----------------------------------------------------------------------
# Tiempo de escaneo por intento y espera entre reintentos, en segundos.
BLE_SCAN_TIMEOUT_S: float = float(os.getenv("BLE_SCAN_TIMEOUT_S", "10"))
RECONNECT_DELAY_S: float = float(os.getenv("BLE_RECONNECT_DELAY_S", "5"))

# --- Telemetria aun no medida por hardware (valores fijos temporales) ---------
DUMMY_BATTERY_V: float = float(os.getenv("GATEWAY_BATTERY_V", "12.6"))
DUMMY_RSSI_DBM: int = int(os.getenv("GATEWAY_RSSI_DBM", "-65"))
