import asyncio
import time
from datetime import datetime  
from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

# Configuración base (DEBE COINCIDIR EXACTAMENTE CON ARDUINO)
CHARACTERISTIC_UUID = "5bd26117-cecc-41b2-96b6-1ceefeb4526c"

CONFIG_SENSORES = {
    "sensor_1": {"name": "ESP32_SHT31_Sensor_01", "prefix": "sensor_01"},
    "sensor_2": {"name": "ESP32_SHT31_Sensor_02", "prefix": "sensor_02"}
}


def handle_notification(sender, data, nombre_archivo, ID_sensor):
    """ Recibe los datos de una ESP32 específica y los guarda en su CSV """
    try:
        payload_decodificado = data.decode('utf-8')
        valores = payload_decodificado.split(',')
        
        if len(valores) == 2:
            temp = valores[0]
            hum = valores[1]
            
            tiempo_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f" [{ID_sensor.upper()}] [{tiempo_actual}] Temp: {temp} °C | Humedad: {hum} %")
            
            with open(nombre_archivo, "a", encoding="utf-8") as archivo:
                archivo.write(f"{tiempo_actual},{temp},{hum}\n")
    except Exception as e:
        print(f" [{ID_sensor.upper()}] Error al procesar notificación: {e}")


def al_desconectar(client, ID_sensor):
    """ Callback ejecutado automáticamente al perder el enlace con un sensor """
    print(f"\n ⚠️ [{ID_sensor.upper()}] [{datetime.now().strftime('%H:%M:%S')}] [ALERTA] Se perdió la conexión remota.")


async def conectar_y_monitorear(ID_sensor, target_name, nombre_csv):
    """ Lógica de escaneo dirigido, conexión y suscripción """
    print(f" [{ID_sensor.upper()}] Buscando a {target_name}...")
    
    # Filtro dirigido por nombre: más rápido y eficiente que discover() en paralelo
    device = await BleakScanner.find_device_by_filter(
        lambda d, ad: d.name == target_name,
        timeout=10.0
    )
    
    if not device:
        print(f" [{ID_sensor.upper()}] No encontrado en este intento.")
        return False

    print(f" [{ID_sensor.upper()}] ¡Encontrado! MAC/UUID: {device.address}. Conectando...")
    
    async with BleakClient(device, disconnected_callback=lambda c: al_desconectar(c, ID_sensor)) as client:
        if client.is_connected:
            print(f" [{ID_sensor.upper()}] ¡Conexión establecida con éxito!")
            
            await client.start_notify(
                CHARACTERISTIC_UUID, 
                lambda sender, data: handle_notification(sender, data, nombre_csv, ID_sensor)
            )
            
            # Mantener la conexión viva mientras el cliente reporte estar conectado
            while client.is_connected:
                await asyncio.sleep(1)
                
            print(f" [{ID_sensor.upper()}] Saliendo del contexto de conexión de forma limpia.")
                
    return True


async def ciclo_sensor_inmortal(ID_sensor, target_name, timestamp_inicio):
    """ Bucle infinito de reconexión automática con esperas controladas """
    nombre_csv = f"{CONFIG_SENSORES[ID_sensor]['prefix']}_{timestamp_inicio}.csv"
    print(f" [{ID_sensor.upper()}] Archivo asignado: {nombre_csv}")

    # Inicializar cabecera de forma segura sin sobreescribir si ya existe
    try:
        with open(nombre_csv, "x", encoding="utf-8") as archivo:
            archivo.write("Tiempo,Temperatura,Humedad\n")
    except FileExistsError:
        pass 

    while True:
        try:
            conexion_exitosa = await conectar_y_monitorear(ID_sensor, target_name, nombre_csv)
            
            # Cooldown obligatorio de 5 segundos para no saturar el driver de Bluetooth
            if not conexion_exitosa:
                print(f" [{ID_sensor.upper()}] Reintentando búsqueda en 5 segundos...")
            else:
                print(f" [{ID_sensor.upper()}] Intentando reconexión tras pérdida de enlace en 5 segundos...")
                
            await asyncio.sleep(5)
                
        except (BleakError, asyncio.TimeoutError) as e:
            print(f" [{ID_sensor.upper()}] Error de comunicación BLE: {e}. Reintentando en 5s...")
            await asyncio.sleep(5)
        except Exception as e:
            print(f" [{ID_sensor.upper()}] Error inesperado en el loop: {e}. Reiniciando en 5s...")
            await asyncio.sleep(5)


async def main():
    timestamp_inicio = int(time.time())
    print(f"--- INICIANDO MONITOREO MULTI-SENSOR BLE (Timestamp: {timestamp_inicio}) ---")

    # Mapeo dinámico de tareas basado en tu diccionario de configuración
    tareas = []
    for id_sensor, info in CONFIG_SENSORES.items():
        tarea = asyncio.create_task(
            ciclo_sensor_inmortal(id_sensor, info["name"], timestamp_inicio)
        )
        tareas.append(tarea)

    # Ejecutar ambas tareas concurrentemente de forma indefinida
    await asyncio.gather(*tareas)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n Grabación múltiple detenida de forma segura. Script finalizado.")