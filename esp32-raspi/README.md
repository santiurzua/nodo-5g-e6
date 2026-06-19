# Integración de Hardware Real: Módulos ESP32 + Pasarela Raspi 🍇📡

Este módulo contiene el firmware y los scripts necesarios para migrar el ecosistema VitiScience desde el entorno simulado hacia el despliegue con **hardware real en terreno**. 

La arquitectura captura datos meteorológicos locales mediante sensores físicos y los introduce directamente en el pipeline de telemetría (Mosquitto -> Telegraf -> InfluxDB -> Grafana) sin necesidad de modificar el backend del dashboard.

---

## 📂 Estructura del Módulo

* **`esp32/`**: Contiene los firmwares en C++ (compatibles con Arduino IDE / PlatformIO) para los nodos periféricos.
    * `SENSOR_01_SHT31/`: Código para el nodo equipado con el sensor de precisión SHT31 (comunicación I2C). Inicializa el BLE como `ESP32_SHT31_Sensor_01`.
    * `SENSOR_02_DHT11/`: Código para el nodo equipado con el sensor DHT11 (GPIO). Inicializa el BLE como `ESP32_SHT31_Sensor_02`.
* **`raspi/`**: Scripts en Python diseñados para ejecutarse de forma continua en la Raspberry Pi central.
    * `ble_mqtt_gateway.py`: **Pasarela asíncrona principal**. Escucha las notificaciones Bluetooth (BLE) de ambos sensores en paralelo, decodifica los strings y publica los payloads JSON bajo el contrato de datos estricto en el broker MQTT.
    * `ble_client.py`: Script secundario de diagnóstico para pruebas directas de conectividad y lectura secuencial BLE.

---

## 🔄 Diagrama de Flujo de Datos

[ Nodo 01: SHT31 ] ───(BLE Notify)───┐
▼
[ Nodo 02: DHT11 ] ───(BLE Notify)───> [ Raspberry Pi ] ───(MQTT JSON)───> [ Mosquitto Broker ]
(ble_mqtt_gateway.py)              (Puerto 1883)

---

## 🛠️ Requisitos e Instalación en la Raspberry Pi

Debido a las restricciones de las versiones de Raspberry Pi OS basadas en Debian Bookworm, es mandatorio aislar la ejecución de la pasarela en un entorno virtual (`venv`):

1. **Navega al directorio de la pasarela:**
   ```bash
   cd esp32-raspi/raspi

Crea y activa el entorno virtual:

Bash
python3 -m venv env-ble
source env-ble/bin/activate
Instala las dependencias asíncronas y de red:

Bash
pip install bleak paho-mqtt
🚀 Puesta en Marcha
Iniciar la infraestructura de contenedores: Asegúrate de levantar el stack de Docker del dashboard principal para activar los servicios de ingesta:

Bash
docker compose up -d
Energizar los sensores de campo: Conecta las placas ESP32 a sus fuentes de poder para que comiencen a emitir anuncios publicitarios Bluetooth.

Ejecutar el Gateway:

Bash
python ble_mqtt_gateway.py
📋 Especificación del Contrato de Datos Emitido
La pasarela mapea los nombres Bluetooth a identificadores fijos (node-01 y node-02) y formatea las estampas de tiempo en UTC estricto (%Y-%m-%dT%H:%M:%SZ) para cumplir simétricamente con el validador telemetry.schema.json:

JSON
{
  "node_id": "node-01",
  "timestamp": "2026-06-19T19:47:00Z",
  "temperature_c": 21.45,
  "humidity_pct": 58.20,
  "battery_v": 12.63,
  "rssi_dbm": -68
}

---

### 📤 Pasos finales en tu terminal para subirlo:

Como ya acomodaste todo en VS Code, limpia tu área de staging y empújalo a GitHub con:

```bash
git add .
git commit -m "docs: añade README detallado para el modulo esp32-raspi"
git push origin main   