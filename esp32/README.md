# Firmware ESP32 (nodos sensores)

Firmware C++ (PlatformIO / framework Arduino) para los nodos perifericos del
ecosistema VitiScience. Cada ESP32 lee su sensor, levanta un servidor BLE GATT y
notifica las lecturas a la Raspberry Pi, que las reenvia al pipeline MQTT
(ver [`../rpi/gateway/`](../rpi/gateway/)).

```
[SHT31 / DHT11] --I2C/GPIO--> [ESP32] --BLE notify--> [Raspberry Pi: gateway] --MQTT-->
```

## Proyectos

| Proyecto            | Sensor | Bus            | Nombre BLE anunciado      | node_id |
|---------------------|--------|----------------|---------------------------|---------|
| `SENSOR_01_SHT31/`  | SHT31  | I2C (SDA 33, SCL 32) | `ESP32_SHT31_Sensor_01` | node-01 |
| `SENSOR_02_DHT11/`  | DHT11  | GPIO 32        | `ESP32_DHT11_Sensor_02`   | node-02 |

Los nombres BLE deben coincidir exactamente con la tabla de sensores del gateway
(`rpi/gateway/config.py`).

## BLE GATT

Ambos firmwares exponen el mismo servicio y caracteristica (sincronizados con el
gateway):

- Service UUID:        `fc3816f9-e1c0-4530-b80e-086f8d8f5491`
- Characteristic UUID: `5bd26117-cecc-41b2-96b6-1ceefeb4526c` (READ + NOTIFY)

La caracteristica emite un string CSV `"temp,hum"` (ej. `"25.4,60.1"`) cada 2 s
mientras la Raspberry Pi este conectada. El descriptor CCCD (0x2902) se agrega para
habilitar notificaciones desde Linux/BlueZ.

## Compilar y flashear (PlatformIO)

Cada carpeta es un proyecto PlatformIO independiente (board `featheresp32`):

```bash
cd SENSOR_01_SHT31         # o SENSOR_02_DHT11
pio run                    # compilar
pio run --target upload    # flashear por USB
pio device monitor         # consola serie (115200 baudios)
```

Las dependencias de librerias (`Adafruit SHT31`, `DHT sensor library`, etc.) estan
declaradas en cada `platformio.ini` y PlatformIO las instala automaticamente.

## Cableado

- **SHT31 (I2C):** SDA -> GPIO 33, SCL -> GPIO 32, VCC 3V3, GND.
- **DHT11 (GPIO):** pin de datos `S` -> GPIO 32, VCC 3V3, GND.
