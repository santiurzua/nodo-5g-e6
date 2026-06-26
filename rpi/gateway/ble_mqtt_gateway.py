"""Pasarela BLE -> MQTT de VitiScience.

Escucha en paralelo las notificaciones BLE de los ESP32 definidos en
``config.SENSORES``, decodifica el string "temp,hum" de cada notificacion y
publica el payload JSON del contrato de datos en el broker MQTT del dashboard.
"""

import asyncio
import json
import logging
import sys
from datetime import datetime, timezone

import paho.mqtt.client as mqtt
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("gateway")

# Cliente MQTT global, compartido por todas las tareas de sensor.
mqtt_client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)


def procesar_y_publicar(data: bytearray, id_sensor: str) -> None:
    """Convierte el string BLE recibido en el JSON del contrato y lo publica."""
    try:
        payload_decodificado = data.decode("utf-8")
        valores = payload_decodificado.split(",")

        if len(valores) != 2:
            log.warning("[%s] Payload BLE con formato inesperado: %r",
                        id_sensor.upper(), payload_decodificado)
            return

        temp = float(valores[0])
        hum = float(valores[1])
        node_id = config.SENSORES[id_sensor]["node_id"]

        # Construir el JSON exactamente como lo exige el contrato del dashboard.
        payload_dict = {
            "node_id": node_id,
            "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "temperature_c": temp,
            "humidity_pct": hum,
            "battery_v": config.DUMMY_BATTERY_V,
            "rssi_dbm": config.DUMMY_RSSI_DBM,
        }

        topic = config.MQTT_TOPIC_TEMPLATE.format(node_id=node_id)
        info = mqtt_client.publish(topic, json.dumps(payload_dict), qos=config.MQTT_QOS)
        info.wait_for_publish()

        log.info("[%s -> MQTT] %s en %s | T: %.1f C | H: %.1f %%",
                 id_sensor.upper(), node_id, topic, temp, hum)

    except Exception as exc:  # noqa: BLE001 - no debe tumbar la tarea del sensor
        log.error("[%s] Error al procesar datos BLE: %s", id_sensor.upper(), exc)


def al_desconectar(_client: BleakClient, id_sensor: str) -> None:
    """Callback de bleak al perder el enlace con un sensor."""
    log.warning("[%s] Se perdio la conexion BLE con el sensor.", id_sensor.upper())


async def conectar_y_monitorear(id_sensor: str, target_name: str) -> bool:
    """Busca el ESP32 por nombre, se conecta y se suscribe a sus notificaciones."""
    log.info("[%s] Buscando a %s...", id_sensor.upper(), target_name)

    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name == target_name,
        timeout=config.BLE_SCAN_TIMEOUT_S,
    )

    if not device:
        return False

    log.info("[%s] Encontrado (%s). Estableciendo enlace BLE...",
             id_sensor.upper(), device.address)

    async with BleakClient(
        device, disconnected_callback=lambda c: al_desconectar(c, id_sensor)
    ) as client:
        if client.is_connected:
            log.info("[%s] Conectado. Escuchando telemetria...", id_sensor.upper())

            await client.start_notify(
                config.CHARACTERISTIC_UUID,
                lambda _sender, data: procesar_y_publicar(data, id_sensor),
            )

            while client.is_connected:
                await asyncio.sleep(1)

    return True


async def ciclo_sensor_inmortal(id_sensor: str, target_name: str) -> None:
    """Bucle infinito de reconexion para un sensor, con cooldown entre intentos."""
    while True:
        try:
            conexion_exitosa = await conectar_y_monitorear(id_sensor, target_name)
            if not conexion_exitosa:
                log.info("[%s] No disponible. Reintentando en %ss...",
                         id_sensor.upper(), config.RECONNECT_DELAY_S)
            else:
                log.info("[%s] Enlace cerrado. Reconectando en %ss...",
                         id_sensor.upper(), config.RECONNECT_DELAY_S)
            await asyncio.sleep(config.RECONNECT_DELAY_S)

        except (BleakError, asyncio.TimeoutError) as exc:
            log.warning("[%s] Error BLE: %s. Reintentando en %ss...",
                        id_sensor.upper(), exc, config.RECONNECT_DELAY_S)
            await asyncio.sleep(config.RECONNECT_DELAY_S)
        except Exception as exc:  # noqa: BLE001 - mantener viva la tarea
            log.error("[%s] Error inesperado: %s. Reiniciando en %ss...",
                      id_sensor.upper(), exc, config.RECONNECT_DELAY_S)
            await asyncio.sleep(config.RECONNECT_DELAY_S)


async def main() -> None:
    log.info("--- INICIANDO GATEWAY HARDWARE REAL -> DASHBOARD MQTT ---")

    # 1. Conectar al broker MQTT antes de escuchar los sensores.
    try:
        mqtt_client.connect(config.MQTT_HOST, config.MQTT_PORT,
                            keepalive=config.MQTT_KEEPALIVE_S)
        mqtt_client.loop_start()
        log.info("Conectado al broker MQTT en %s:%s.",
                 config.MQTT_HOST, config.MQTT_PORT)
    except Exception as exc:  # noqa: BLE001
        log.error("No se pudo conectar al broker MQTT en %s:%s (%s). "
                  "Esta corriendo el dashboard?",
                  config.MQTT_HOST, config.MQTT_PORT, exc)
        sys.exit(1)

    # 2. Lanzar una tarea asincrona por sensor fisico.
    tareas = [
        asyncio.create_task(ciclo_sensor_inmortal(id_sensor, info["name"]))
        for id_sensor, info in config.SENSORES.items()
    ]
    await asyncio.gather(*tareas)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Gateway detenido. Cerrando comunicaciones...")
        mqtt_client.loop_stop()
        mqtt_client.disconnect()
