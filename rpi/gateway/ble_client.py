"""Script de diagnostico BLE: guarda la telemetria de cada ESP32 en un CSV.

Util para probar la conectividad y las lecturas BLE sin tocar el pipeline MQTT.
Reusa la tabla de sensores y los parametros de ``config.py``. Cada ejecucion crea
un CSV por sensor con sufijo de timestamp para no sobrescribir corridas previas.
"""

import asyncio
import logging
import time
from datetime import datetime

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

import config

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("ble-client")


def handle_notification(data: bytearray, nombre_archivo: str, id_sensor: str) -> None:
    """Recibe los datos de un ESP32 y los anexa a su CSV."""
    try:
        valores = data.decode("utf-8").split(",")
        if len(valores) != 2:
            log.warning("[%s] Payload con formato inesperado.", id_sensor.upper())
            return

        temp, hum = valores[0], valores[1]
        tiempo_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log.info("[%s] Temp: %s C | Humedad: %s %%", id_sensor.upper(), temp, hum)

        with open(nombre_archivo, "a", encoding="utf-8") as archivo:
            archivo.write(f"{tiempo_actual},{temp},{hum}\n")
    except Exception as exc:  # noqa: BLE001
        log.error("[%s] Error al procesar notificacion: %s", id_sensor.upper(), exc)


def al_desconectar(_client: BleakClient, id_sensor: str) -> None:
    """Callback de bleak al perder el enlace con un sensor."""
    log.warning("[%s] Se perdio la conexion remota.", id_sensor.upper())


async def conectar_y_monitorear(id_sensor: str, target_name: str, nombre_csv: str) -> bool:
    """Escaneo dirigido por nombre, conexion y suscripcion a notificaciones."""
    log.info("[%s] Buscando a %s...", id_sensor.upper(), target_name)

    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name == target_name,
        timeout=config.BLE_SCAN_TIMEOUT_S,
    )

    if not device:
        log.info("[%s] No encontrado en este intento.", id_sensor.upper())
        return False

    log.info("[%s] Encontrado (%s). Conectando...", id_sensor.upper(), device.address)

    async with BleakClient(
        device, disconnected_callback=lambda c: al_desconectar(c, id_sensor)
    ) as client:
        if client.is_connected:
            log.info("[%s] Conexion establecida.", id_sensor.upper())

            await client.start_notify(
                config.CHARACTERISTIC_UUID,
                lambda _sender, data: handle_notification(data, nombre_csv, id_sensor),
            )

            while client.is_connected:
                await asyncio.sleep(1)

    return True


async def ciclo_sensor_inmortal(id_sensor: str, target_name: str, timestamp_inicio: int) -> None:
    """Bucle infinito de reconexion con cooldown; escribe un CSV por sensor."""
    nombre_csv = f"{config.SENSORES[id_sensor]['prefix']}_{timestamp_inicio}.csv"
    log.info("[%s] Archivo asignado: %s", id_sensor.upper(), nombre_csv)

    # Inicializar la cabecera sin sobrescribir si el archivo ya existe.
    try:
        with open(nombre_csv, "x", encoding="utf-8") as archivo:
            archivo.write("Tiempo,Temperatura,Humedad\n")
    except FileExistsError:
        pass

    while True:
        try:
            conexion_exitosa = await conectar_y_monitorear(id_sensor, target_name, nombre_csv)
            if not conexion_exitosa:
                log.info("[%s] Reintentando busqueda en %ss...",
                         id_sensor.upper(), config.RECONNECT_DELAY_S)
            else:
                log.info("[%s] Reconectando tras perdida de enlace en %ss...",
                         id_sensor.upper(), config.RECONNECT_DELAY_S)
            await asyncio.sleep(config.RECONNECT_DELAY_S)

        except (BleakError, asyncio.TimeoutError) as exc:
            log.warning("[%s] Error BLE: %s. Reintentando en %ss...",
                        id_sensor.upper(), exc, config.RECONNECT_DELAY_S)
            await asyncio.sleep(config.RECONNECT_DELAY_S)
        except Exception as exc:  # noqa: BLE001
            log.error("[%s] Error inesperado: %s. Reiniciando en %ss...",
                      id_sensor.upper(), exc, config.RECONNECT_DELAY_S)
            await asyncio.sleep(config.RECONNECT_DELAY_S)


async def main() -> None:
    timestamp_inicio = int(time.time())
    log.info("--- INICIANDO MONITOREO MULTI-SENSOR BLE (timestamp: %s) ---", timestamp_inicio)

    tareas = [
        asyncio.create_task(ciclo_sensor_inmortal(id_sensor, info["name"], timestamp_inicio))
        for id_sensor, info in config.SENSORES.items()
    ]
    await asyncio.gather(*tareas)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Grabacion multiple detenida de forma segura.")
