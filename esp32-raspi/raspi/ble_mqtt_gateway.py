import asyncio
import time
import json
import sys
from datetime import datetime, timezone
import paho.mqtt.client as mqtt
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# ==============================================================================
# CONFIGURACIÓN DEL SISTEMA
# ==============================================================================
# Configuración BLE (Debe coincidir con tus ESP32)
CHARACTERISTIC_UUID = "5bd26117-cecc-41b2-96b6-1ceefeb4526c"

CONFIG_SENSORES = {
    "sensor_1": {"name": "ESP32_SHT31_Sensor_01", "node_id": "node-01"},
    "sensor_2": {"name": "ESP32_DHT11_Sensor_02", "node_id": "node-02"} 
}

# Configuración MQTT (Apunta al Broker de tu Dashboard)
MQTT_HOST = "localhost"  # Si el Dashboard corre en la misma Pi. Si no, usa su IP.
MQTT_PORT = 1883
MQTT_QOS = 1
MQTT_TOPIC_TEMPLATE = "vitiscience/nodes/{node_id}/telemetry"

# Cliente MQTT Global
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

# ==============================================================================
# LÓGICA DE PROCESAMIENTO Y ENVÍO
# ==============================================================================
def procesar_y_publicar(data, ID_sensor):
    """ Convierte el string BLE en el JSON oficial del contrato de datos """
    try:
        payload_decodificado = data.decode('utf-8')
        valores = payload_decodificado.split(',')
        
        if len(valores) == 2:
            temp = float(valores[0])
            hum = float(valores[1])
            node_id = CONFIG_SENSORES[ID_sensor]["node_id"]
            
            # Construir el JSON exactamente como lo exige el contrato del Dashboard
            payload_dict = {
                "node_id": node_id,
                "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                "temperature_c": temp,
                "humidity_pct": hum,
                "battery_v": 12.6,  # Valores fijos temporales o dummy si el hardware no los mide aún
                "rssi_dbm": -65
            }
            
            # Conversión a texto string JSON
            payload_json = json.dumps(payload_dict)
            topic = MQTT_TOPIC_TEMPLATE.format(node_id=node_id)
            
            # Publicar al Dashboard vía MQTT
            infot = mqtt_client.publish(topic, payload_json, qos=MQTT_QOS)
            infot.wait_for_publish()
            
            print(f"📡 [GATEWAY -> MQTT] {node_id} publicado en {topic} | T: {temp}°C | H: {hum}%")
            
    except Exception as e:
        print(f"❌ Error al procesar datos BLE de {ID_sensor}: {e}")


def al_desconectar(client, ID_sensor):
    print(f"\n ⚠️ [{ID_sensor.upper()}] Se perdió la conexión BLE con el sensor físico.")


async def conectar_y_monitorear(ID_sensor, target_name):
    """ Busca el ESP32, se conecta y se suscribe a sus notificaciones """
    print(f" [{ID_sensor.upper()}] Buscando en el aire a: {target_name}...")
    
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name == target_name,
        timeout=10.0
    )
    
    if not device:
        return False

    print(f" [{ID_sensor.upper()}] ¡Encontrado MAC: {device.address}! Estableciendo enlace BLE...")
    
    async with BleakClient(device, disconnected_callback=lambda c: al_desconectar(c, ID_sensor)) as client:
        if client.is_connected:
            print(f" [{ID_sensor.upper()}] ¡Conectado con éxito! Escuchando telemetría...")
            
            # Pasamos los datos recibidos directamente a nuestra función de empaquetado MQTT
            await client.start_notify(
                CHARACTERISTIC_UUID, 
                lambda sender, data: procesar_y_publicar(data, ID_sensor)
            )
            
            while client.is_connected:
                await asyncio.sleep(1)
                
    return True


async def ciclo_sensor_inmortal(ID_sensor, target_name):
    """ Bucle infinito de reconexión para cada sensor """
    while True:
        try:
            conexion_exitosa = await conectar_y_monitorear(ID_sensor, target_name)
            if not conexion_exitosa:
                print(f" [{ID_sensor.upper()}] No disponible. Reintentando en 5s...")
            else:
                print(f" [{ID_sensor.upper()}] Enlace cerrado. Intentando reconectar en 5s...")
            await asyncio.sleep(5)
                
        except (BleakError, asyncio.TimeoutError) as e:
            print(f" [{ID_sensor.upper()}] Error BLE: {e}. Reintentando en 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f" [{ID_sensor.upper()}] Error inesperado: {e}. Reiniciando en 5s...")
            await asyncio.sleep(5)


async def main():
    print("--- INICIANDO CONEXIÓN HARDWARE REAL -> DASHBOARD MQTT ---")
    
    # 1. Conectar al Broker MQTT antes de escuchar los sensores
    try:
        mqtt_client.connect(MQTT_HOST, MQTT_PORT, keepalive=60)
        mqtt_client.loop_start()
        print("[+] Conectado al Broker MQTT con éxito.")
    except Exception as e:
        print(f"❌ Error: No se pudo conectar al Broker MQTT en {MQTT_HOST}:{MQTT_PORT}. ¿Está el Dashboard corriendo?")
        sys.exit(1)

    # 2. Lanzar hilos asíncronos para los sensores físicos
    tareas = []
    for id_sensor, info in CONFIG_SENSORES.items():
        tarea = asyncio.create_task(ciclo_sensor_inmortal(id_sensor, info["name"]))
        tareas.append(tarea)

    await asyncio.gather(*tareas)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Gateway detenido. Cerrando comunicaciones...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()